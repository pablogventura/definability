#!/usr/bin/env python
# -*- coding: utf8 -*-

# Minion interface code Peter Jipsen 2011-03-26 alpha version
# requires sage.chapman.edu/sage/minion_20110326.spkg

import subprocess as sp
from itertools import product

from morphisms import *
import config
import files


class MinionSol(object):
    __count = 0
    def __init__(self, input_data, allsols=True, fun=lambda x: x):
        self.id = MinionSol.__count
        self.fun = fun
        MinionSol.__count += 1
        self.input_filename = config.minion_path + "input_minion%s" % self.id
        print self.input_filename

        files.create_pipe(self.input_filename)

        minionargs = ["-printsolsonly"] 
        if allsols:
            minionargs += ["-findallsols"]
        minionargs += [self.input_filename]

        self.minionapp = sp.Popen([config.minion_path + "minion"] + minionargs,
                                  stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        files.write(self.input_filename, input_data)
        self.EOF = False
        self.solutions = []

    def __parse_solution(self):
        str_sol = self.minionapp.stdout.readline()
        if str_sol:
            str_sol = str_sol[:-1] # borro el \n
            result = map(int, str_sol.strip().split(" "))
            return result
        else:
            self.EOF = True
            self.__terminate()

    def __iter__(self):
        for solution in self.solutions:
            yield self.fun(solution)

        while not self.EOF:
            solution = self.__parse_solution()
            if solution:
                self.solutions.append(solution)
                yield self.fun(solution)
            
    def __getitem__(self, index):
        try:
            return self.fun(self.solutions[index])
        except IndexError:
            for i,solution in enumerate(self):
                if i==index:
                    return solution # no hace falta aplicar self.fun porque esta llamando a __iter__
            raise IndexError("There aren't so many solutions.")
                
    def __nonzero__(self):
        if self.solutions or self.EOF:
            return bool(self.solutions)
        else:
            solution = self.__parse_solution()
            if solution:
                self.solutions.append(solution)
                return True
            else:
                return False
                
    def __len__(self):
        if not self.EOF:
            for i in self:
                pass
        return len(self.solutions)

    def __terminate(self):
        self.minionapp.kill()
        del self.minionapp
        files.remove(self.input_filename)









class MorphMinionSol(MinionSol):
    def __init__(self, morph_type, subtype, source, target, inj=None, surj=None, allsols=True):
        self.morph_type = morph_type
        self.subtype = subtype
        self.source = source
        self.target = target
        self.inj = inj
        self.surj = surj
        
        if self.morph_type == Homomorphism:
            input_data = self.__input_homo()
        elif self.morph_type == Embedding:
            self.inj = True
            input_data = self.__input_embedd()
        elif self.morph_type == Isomorphism:
            self.inj = True
            self.surj = True
            input_data = self.__input_embedd()
        else:
            raise IndexError("Morphism unknown")

        self.fun = lambda x: self.morph_type(x,
                                             self.source,
                                             self.target,
                                             self.subtype,
                                             self.inj,
                                             self.surj) # funcion que tipa los morfismos
        print input_data
        super(MorphMinionSol, self).__init__(input_data, allsols,fun=self.fun)

    def __minion_name(self, oprel):
        """
        Traduce los nombres de las operaciones/relaciones
        """
        # Minion accepts only letters for first character of names
        if oprel.isalpha():
            return oprel
            
        ops = {"^": "m", "+": "p", "-": "s", "*": "t", "<=": "leq"}
        if oprel in ops:
            return ops[oprel]
        else:
            oprel += " " * ((3-len(oprel))%3) # le agrego espacios para evitar los = que mete b64
            return oprel.encode("base64")[:-1]

    def __oprel_table(self, oprel, prefix=""):
        """
        Devuelve un string con la tabla que representa a la relacion/operacion en minion
        """
        table = oprel.table()
        table_name = prefix + self.__minion_name(oprel.symbol)
        height = len(table)
        width = len(table[0])
        result = ""
        for row in table:
            result += " ".join(map(str, row)) + "\n"
        result = "%s %s %s\n" % (table_name, height, width) + result
        return result

    def __input_homo(self):
        """
        Genera un string para darle a Minion para tener los homomorfismos de source en target
        """
        A = self.source
        B = self.target
        
        result = "MINION 3\n\n"
        result += "**VARIABLES**\n"
        result += "DISCRETE f[%s]{0..%s}\n\n" % (A.cardinality, B.cardinality - 1)
        result += "**TUPLELIST**\n"
        for op in self.subtype.operations:
            result += self.__oprel_table(B.operations[op]) + "\n"
        for rel in self.subtype.relations:
            result += self.__oprel_table(B.relations[rel]) + "\n"
        result += "**CONSTRAINTS**\n"
        if self.inj:
            result += "alldiff(f)\n"  # exige que todos los valores de f sean distintos
        if self.surj:
            for i in range(B.cardinality):
                result += "occurrencegeq(f, " + str(i) + ", 1)\n"  # exige que i aparezca al menos una vez en el "vector" f

        for op in self.subtype.operations:
            cons = A.operations[op].table()
            for row in cons:
                result += "table([f[" + "],f[".join(map(str, row)) + "]],%s)\n" % self.__minion_name(op)
            result += "\n"
        for rel in self.subtype.relations:
            cons = A.relations[rel].table()
            for row in cons:
                result += "table([f[" + "],f[".join(map(str, row)) + "]],%s)\n" % self.__minion_name(rel)
            result += "\n"
        result += "**EOF**\n"
        return result

    def __input_embedd(self):
        """
        Genera un string para darle a Minion para tener los embeddings de A en B
        """
        A = self.source
        B = self.target
        
        result = "MINION 3\n\n"
        result += "**VARIABLES**\n"
        result += "DISCRETE f[%s]{0..%s}\n\n" % (A.cardinality, B.cardinality - 1)
        result += "DISCRETE g[%s]{-1..%s}\n\n" % (B.cardinality, A.cardinality - 1)
        result += "**SEARCH**\n"
        result += "PRINT [f]\n\n" # para que no me imprima los valores de g
        result += "**TUPLELIST**\n"
        
        for op in self.subtype.operations:
            result += self.__oprel_table(B.operations[op],prefix="b") + "\n"
        for rel in self.subtype.relations:
            result += self.__oprel_table(B.relations[rel],prefix="b") + "\n"
        for rel in self.subtype.relations:
            result += self.__oprel_table(A.relations[rel],prefix="a") + "\n"
            
        result += "**CONSTRAINTS**\n"
        if self.inj:
            result += "alldiff(f)\n"  # exige que todos los valores de f sean distintos
        if self.surj:
            for i in range(B.cardinality):
                result += "occurrencegeq(f, " + str(i) + ", 1)\n"  # exige que i aparezca al menos una vez en el "vector" f

        for op in self.subtype.operations:
            cons =A.operations[op].table()
            for row in cons:
                result += "table([f[" + "],f[".join(map(str, row)) + "]],%s)\n" % ("b"+self.__minion_name(op))
            result += "\n"
        for rel in self.subtype.relations:
            cons = A.relations[rel].table()
            for row in cons:
                result += "table([f[" + "],f[".join(map(str, row)) + "]],%s)\n" % ("b"+self.__minion_name(rel))
            result += "\n"
        for rel in self.subtype.relations:
            cons = B.relations[rel].table()
            for row in cons:
                result += "watched-or({"
                for i in row:
                    result += "element(g, %s, -1)," % i
                result += "table([g[" + "],g[".join(map(str, row)) + "]],%s)})\n" % ("a"+self.__minion_name(rel))
            result += "\n"
        for i in range(A.cardinality):
            result += "element(g, f[%s], %s)\n" % (i,i) # g(f(x))=X
        result += "occurrencegeq(g, -1, %s)\n" % (B.cardinality - A.cardinality)
        result += "**EOF**\n"
        return result

def Hom(A, B, inj=False, surj=False):
    """
    call Minion to calculate all homomorphisms from A to B
    """
    st = input_homo(A, B,inj,surj)
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
    return (ListWithArity(emb) for emb in MinionSol(st))

def Embeddingsfiltrando(A, B):
    """
    call Minion to calculate all embeddings of A into B
    """
    for h in Hom(A,B,inj=True):
        if em_check(A,B,h):
            yield h

def Aut(A):
    """
    call Minion to calculate all automorphisms of A
    """
    return Embeddings(A, A)


def is_hom_image(A, B):
    """return true if B is a homomorphic image of A (uses Minion)"""
    st = input_homo(A, B, surj=True)
    return bool(MinionSol(st,allsols=False))


def is_substructure(A, B):
    """
    return true if A is a substructure of B (uses Minion)
    """
    st = input_embedd(A, B)
    return bool(MinionSol(st,allsols=False))


def is_isomorphic(A, B):
    """
    return true if A is isomorphic to B (uses Minion)
    """
    st = input_embedd(A, B,surj=True)
    return bool(MinionSol(st,allsols=False))



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
