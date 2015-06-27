################################################################
# Minion interface code Peter Jipsen 2011-03-26 alpha version
# requires sage.chapman.edu/sage/minion_20110326.spkg

import os
import subprocess as sp
from misc import readfile, writefile
import config
from itertools import product


class MinionSol():
    __count = 0

    def __init__(self, inputdata, allsols=True):
        self.id = MinionSol.__count
        MinionSol.__count += 1
        self.inputfilename = config.minionpath + "input_minion%s" % self.id
        print self.inputfilename

        try:
            os.mkfifo(self.inputfilename)
        except OSError:
            pass

        minionargs = ["-printsolsonly"] 
        if allsols:
            minionargs += ["-findallsols"]
        minionargs += [self.inputfilename]

        self.minionapp = sp.Popen([config.minionpath + "minion"] + minionargs, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        writefile(self.inputfilename, inputdata)
        self.buffer = ""
        self.EOF = False
        self.values = []

        self.__read()  # primer lectura
        self.__parsebuffer()  # primer parseo
        # TODO en el futuro habria que manejar pausas al proceso, por si se adelanta muy mucho y se hace muy grande

    def __parsebuffer(self):
        if self.buffer:
            buf = self.buffer.split("\n")
            if self.buffer[-1] != "\n":  # no era el ultimo
                self.buffer = buf[-1]
            else:
                self.buffer = ""  # lo vacio porque era el ultimo

            del buf[-1]  # porque o habia parte de otra solucion, o era [] porque siempre hay un \n al final

            for fila in buf:
                sol = map(int, fila.strip().split(" "))
                if sol not in self.values: # no quiero soluciones dobles, (culpa de que la inversa es distinta)
                    self.values.append(sol)

    def __read(self, size=1024):
        if not self.EOF:
            self.buffer += self.minionapp.stdout.readline()
            self.buffer += self.minionapp.stdout.read(size)
            if not self.buffer:
                self.EOF = True
                self.minionapp.terminate()
                try:
                    os.remove(self.inputfilename)
                except OSError:
                    pass

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
    # def getitem TODO SE PODRIA AGREGAR

    def __len__(self):
        if not self.EOF:
            self.__readall()  # yo no queria, pero me veo obligado a leer todo
            self.__parsebuffer()
        return len(self.values)

    def __del__(self):
        self.minionapp.kill()
        del self.minionapp
        try:
            os.remove(self.inputfilename)
        except OSError:
            pass


def t_op(st):
    """
    Traduce los nombres de las operaciones/relaciones
    """
    # Minion accepts only letters for first character of names
    if st.isalpha():
        return st
        
    ops = {"^": "m", "+": "p", "-": "s", "*": "t", "<=": "leq"}
    if st in ops:
        return ops[st]
    else:
        st += " " * ((3-len(st))%3) # le agrego espacios para evitar los = que mete b64
        return st.encode("base64")[:-1]


def input_homo(A, B, inj=False, surj=False):
    """
    Genera un string para darle a Minion para tener los homomorfismos de A en B
    """
    result = "MINION 3\n\n"
    result += "**VARIABLES**\n"
    result += "DISCRETE f[%s]{0..%s}\n\n" % (A.cardinality, B.cardinality - 1)
    result += "**TUPLELIST**\n"
    for op in B.operations:
        result += B.operations[op].minion_table(t_op(op)) + "\n"
    for rel in B.relations:
        result += B.relations[rel].minion_table(t_op(rel), relation=True) + "\n"
    result += "**CONSTRAINTS**\n"
    if inj:
        result += "alldiff(f)\n"  # exige que todos los valores de f sean distintos
    if surj:
        for i in range(B.cardinality):
            result += "occurrencegeq(f, " + str(i) + ", 1)\n"  # exige que i aparezca al menos una vez en el "vector" f

    for op in A.operations:
        cons = A.operations[op].table()
        for row in cons:
            result += "table([f[" + "],f[".join(map(str, row)) + "]],%s)\n" % t_op(op)
        result += "\n"
    for rel in A.relations:
        cons = A.relations[rel].table(relation=True)
        for row in cons:
            result += "table([f[" + "],f[".join(map(str, row)) + "]],%s)\n" % t_op(rel)
        result += "\n"
    result += "**EOF**\n"
    return result

def input_embedd(A, B, inj=True, surj=False):
    """
    Genera un string para darle a Minion para tener los embeddings de A en B
    """
    
    result = "MINION 3\n\n"
    result += "**VARIABLES**\n"
    result += "DISCRETE f[%s]{0..%s}\n\n" % (A.cardinality, B.cardinality - 1)
    result += "DISCRETE g[%s]{0..%s}\n\n" % (B.cardinality, A.cardinality - 1)
    result += "**SEARCH**\n"
    result += "PRINT [f]\n\n" # para que no me imprima los valores de g
    result += "**TUPLELIST**\n"
    
    for op in B.operations:
        result += B.operations[op].minion_table("b"+t_op(op)) + "\n"
    for rel in B.relations:
        result += B.relations[rel].minion_table("b"+t_op(rel), relation=True) + "\n"
    for op in A.operations:
        result += A.operations[op].minion_table("a"+t_op(op)) + "\n"
    for rel in A.relations:
        result += A.relations[rel].minion_table("a"+t_op(rel), relation=True) + "\n"
        
    result += "**CONSTRAINTS**\n"
    if inj:
        result += "alldiff(f)\n"  # exige que todos los valores de f sean distintos
    if surj:
        for i in range(B.cardinality):
            result += "occurrencegeq(f, " + str(i) + ", 1)\n"  # exige que i aparezca al menos una vez en el "vector" f

    for op in A.operations:
        cons = A.operations[op].table()
        for row in cons:
            result += "table([f[" + "],f[".join(map(str, row)) + "]],%s)\n" % ("b"+t_op(op))
        result += "\n"
    for rel in A.relations:
        cons = A.relations[rel].table(relation=True)
        for row in cons:
            result += "table([f[" + "],f[".join(map(str, row)) + "]],%s)\n" % ("b"+t_op(rel))
        result += "\n"
    for op in B.operations:
        cons = B.operations[op].table()
        for row in cons:
            result += "table([g[" + "],g[".join(map(str, row)) + "]],%s)\n" % ("a"+t_op(op))
        result += "\n"
    for rel in B.relations:
        cons = B.relations[rel].table(relation=True)
        for row in cons:
            result += "table([g[" + "],g[".join(map(str, row)) + "]],%s)\n" % ("a"+t_op(rel))
        result += "\n"
    for i in range(A.cardinality):
        result += "element(g, f[%s], %s)\n" % (i,i) # g(f(x))=X

    result += "**EOF**\n"
    return result

def Hom(A, B):
    """
    call Minion to calculate all homomorphisms from A to B
    """
    st = input_homo(A, B)
    return MinionSol(st)

def Iso(A, B):
    """
    call Minion to calculate all homomorphisms from A to B
    """
    st = input_embedd(A, B, surj=True)
    return MinionSol(st)

def End(A):
    """
    call Minion to calculate all endomorphisms of A
    """
    return Hom(A, A)


def Embeddings(A, B):
    """
    call Minion to calculate all embeddings of A into B
    """
    st = input_embedd(A, B)
    return MinionSol(st)


def Aut(A):
    """
    call Minion to calculate all automorphisms of A
    """
    return Embeddings(A, A)


def is_hom_image(A, B):
    """return true if B is a homomorphic image of A (uses Minion)"""
    st = input_homo(A, B, surj=True)
    return len(MinionSol(st,allsols=False)) > 0


def is_subalgebra(A, B):
    """
    return true if A is a subalgebra of B (uses Minion)
    """
    st = input_embedd(A, B)
    return len(MinionSol(st,allsols=False)) > 0


def is_isomorphic(A, B):
    """
    return true if A is isomorphic to B (uses Minion)
    """
    st = input_embedd(A, B,surj=True)
    return len(MinionSol(st,allsols=False)) > 0


def minion_hom_bin_rel(A, B):
    # TODO PARECE QUE DEBERIA IRSE
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
    # TODO NO TENGO IDEA QUE ES, PARECE QUE DEBERIA IRSE
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
