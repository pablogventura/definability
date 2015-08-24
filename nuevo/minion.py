#!/usr/bin/env python
# -*- coding: utf8 -*-

# Minion interface code Peter Jipsen 2011-03-26 alpha version
# requires sage.chapman.edu/sage/minion_20110326.spkg

import subprocess as sp
from itertools import product

import config
import files


class MinionSol():
    __count = 0
    def __init__(self, input_data, allsols=True):
        self.id = MinionSol.__count
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
            yield solution

        while not self.EOF:
            solution = self.__parse_solution()
            if solution:
                self.solutions.append(solution)
                yield solution
            
    # def getitem TODO SE PODRIA AGREGAR
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
    result += "DISCRETE g[%s]{-1..%s}\n\n" % (B.cardinality, A.cardinality - 1)
    result += "**SEARCH**\n"
    result += "PRINT [f]\n\n" # para que no me imprima los valores de g
    result += "**TUPLELIST**\n"
    
    for op in B.operations:
        result += B.operations[op].minion_table("b"+t_op(op)) + "\n"
    for rel in B.relations:
        result += B.relations[rel].minion_table("b"+t_op(rel), relation=True) + "\n"
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
    for rel in B.relations:
        cons = B.relations[rel].table(relation=True)
        for row in cons:
            result += "watched-or({"
            for i in row:
                result += "element(g, %s, -1)," % i
            result += "table([g[" + "],g[".join(map(str, row)) + "]],%s)})\n" % ("a"+t_op(rel))
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
