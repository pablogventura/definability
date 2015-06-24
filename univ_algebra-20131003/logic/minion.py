################################################################
# Minion interface code Peter Jipsen 2011-03-26 alpha version
# requires sage.chapman.edu/sage/minion_20110326.spkg

import os
import subprocess as sp
from misc import readfile, writefile


# TODO ESTO ES PRUEBA, PERO ANDA MUCHO MEJOR DE VELOCIDAD


class MinionSol():
    __count = 0
    def __init__(self, inputdata):
        self.id = MinionSol.__count
        MinionSol.__count += 1
        
        os.mkfifo("input_minion%s" % self.id)
        
        minionargs = ["-printsolsonly","-findallsols","input_minion%s" % self.id]
            
        self.minionapp = sp.Popen(["minion"]+minionargs, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        writefile("input_minion%s" % self.id ,inputdata)
        self.buffer = ""
        self.EOF = False
        self.values = []
        
        self.__read() # primer lectura
        self.__parsebuffer() # primer parseo
        # TODO en el futuro habria que manejar pausas al proceso, por si se adelanta muy mucho y se hace muy grande
        
    def __parsebuffer(self):
        if self.buffer:
            buf = self.buffer.split("\n")
            if self.buffer[-1] != "\n": # no era el ultimo
                self.buffer = buf[-1]
            else:
                self.buffer = "" # lo vacio porque era el ultimo
            
            del buf[-1] # porque o habia parte de otra solucion, o era [] porque siempre hay un \n al final
            
            for fila in buf:
                self.values.append(map(int,fila.strip().split(" ")))
    
    def __read(self,size=1024):
        if not self.EOF:
            self.buffer += self.minionapp.stdout.readline()
            self.buffer += self.minionapp.stdout.read(size)
            if not self.buffer:
                self.EOF = True
                self.minionapp.terminate()
                os.remove("input_minion%s" % self.id)

    def __readall(self):
        if not self.EOF:
            data = self.minionapp.stdout.read()
            while data:
                self.buffer += data
                data = self.minionapp.stdout.read()

    def __iter__(self):
        for x in self.values:
            yield x
            if not self.EOF:
                self.__read()
                self.__parsebuffer()
    #def getitem TODO SE PODRIA AGREGAR
            
    def __len__(self):
        if not self.EOF:
            self.__readall() # yo no queria, pero me veo obligado a leer todo
            self.__parsebuffer()
        return len(self.values)

    def __del__(self):
        self.minionapp.kill()
        del self.minionapp
        if os.path.isfile("input_minion%s" % self.id):
            os.remove("input_minion%s" % self.id)
        

def t_op(st):
    # Minion accepts only letters for first character of names
    ops = {"^": "m", "+": "p", "-": "s", "*": "t"}
    if st in ops:
        return ops[st]
    return st


def minion_hom_algebras(A, B, inj=False, surj=False):
    # A,B are algebras CURRENTLY with only unary or binary operations
    if hasattr(A, "uc"):
        A.get_meet()
        A.get_join()
        B.get_meet()
        B.get_join()
    st = "MINION 3\n\n**VARIABLES**\nDISCRETE f[" + str(A.cardinality) + "]{0.." + str(B.cardinality - 1) + "}\n\n**TUPLELIST**\n"
    for s in B.operations:
        if type(B.operations[s]) == list:
            if type(B.operations[s][0]) == list:  # binary
                st += t_op(s) + " " + str(B.cardinality * B.cardinality) + " 3\n"
                for i in range(B.cardinality):
                    for j in range(B.cardinality):
                        st += str(i) + " " + str(j) + " " + str(B.operations[s][i][j]) + "\n"
            else:  # unary
                st += t_op(s) + " " + str(B.cardinality) + " 2\n"
                for i in range(B.cardinality):
                    st += str(i) + " " + str(B.operations[s][i]) + "\n"
        # still need to do constants and arity>2
        st += "\n"
    st += "**CONSTRAINTS**\n"
    if inj:
        st += "alldiff(f)\n"
    if surj:
        for i in range(B.cardinality):
            st += "occurrencegeq(f, " + str(i) + ", 1)\n"
    for s in A.operations:
        if type(A.operations[s]) == list:
            if type(A.operations[s][0]) == list:  # binary
                for i in range(A.cardinality):
                    for j in range(A.cardinality):
                        st += "table([f[" + str(i) + "],f[" + str(j) + "],f[" + str(A.operations[s][i][j]) + "]]," + t_op(s) + ")\n"
            else:  # unary
                for i in range(A.cardinality):
                    st += "table([f[" + str(i) + "],f[" + str(A.operations[s][i]) + "]]," + t_op(s) + ")\n"
        # still need to do constants and arity>2
        st += "\n"
    return st + "**EOF**\n"


def Hom(A, B):
    """
    call Minion to calculate all homomorphisms from algebra A to algebra B
    """
    st = minion_hom_algebras(A, B)
    return MinionSol(st)


def End(A):
    """
    call Minion to calculate all endomorphisms of algebra A
    """
    return Hom(A, A)


def Embeddings(A, B):
    """
    call Minion to calculate all embeddings of algebra A into algebra B
    """
    st = minion_hom_algebras(A, B, True)
    return MinionSol(st)


def Aut(A):
    """
    call Minion to calculate all automorphisms of algebra A
    """
    return Embeddings(A, A)


def is_hom_image(A, B):
    """return true if B is a homomorphic image of A (uses Minion)"""
    st = minion_hom_algebras(A, B, surj=True)
    return len(MinionSol(st)) > 0


def is_subalgebra(A, B):
    """
    return true if A is a subalgebra of B (uses Minion)
    """
    st = minion_hom_algebras(A, B, inj=True)
    return len(MinionSol(st)) > 0



def is_isomorphic(A, B):
    """
    return true if A is isomorphic to B (uses Minion)
    """
    return A.cardinality == B.cardinality and is_subalgebra(A, B)




def minion_hom_bin_rel(A, B):
    # A,B are relational structures with only BINARY relations
    st = "MINION 3\n\n**VARIABLES**\nDISCRETE f[" + str(A.cardinality) + "]{0.." + str(B.cardinality - 1) + "}\n\n**TUPLELIST**\n"
    for s in B.relations:
        cnt = [x for y in B.relations[s] for x in y].count(1)
        st += s + " " + str(cnt) + " 2\n"
        for i in range(B.cardinality):
            for j in range(B.cardinality):
                if B.relations[s][i][j] == 1:
                    st += str(i) + " " + str(j) + "\n"
    st += "\n**CONSTRAINTS**\n"
    for s in A.relations:
        for i in range(A.cardinality):
            for j in range(A.cardinality):
                if A.relations[s][i][j] == 1:
                    st += "table([f[" + str(i) + "],f[" + str(j) + "]]," + s + ")\n"
    return st + "\n**EOF**\n"


def Pol_1(U):
    """
    Find unary polynomials that preserve all relations of 
    the binary relational structure U
    """
    st = minion_hom_bin_rel(U, U)
    # antes devolvia una lista de tuplas, ahora es un generador de listas
    return MinionSol(st)


def ops2alg(ops):
    """
    Convert a list of operations to an algebra
    """
    return Model(cardinality=len(ops[0]),
                 operations=dict(["h" + str(i), list(ops[i])] for i in range(len(ops))))


def parts2relst(Ps):
    """
    Convert a list of partitions (strings) to a relational structure
    """
    return Model(cardinality=max(max(b) for b in str2part(Ps[0])) + 1,
                 relations=dict(["R" + str(i), part2eqrel(str2part(Ps[i]))]
                                for i in range(len(Ps))))


def is_congruence_closed(B):
    return len(B.relations) + 2 == len(Con(ops2alg(Pol_1(B))))


def congruence_closure(parts):
    return Con(ops2alg(Pol_1(parts2relst(parts))))


def monoid_closure(ops):
    return Pol_1(parts2relst(Con(ops2alg(ops))))
