r"""
Universal algebra
"""
#*****************************************************************************
#    Peter Jipsen 2010, 2011 <jipsen@chapman.edu>,
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
#
# Python/Sage interface to Prover9/Mace4 (prover9.org)
# Universal Algebra Calculator (uacalc.org)
# and Minion (minion.sourceforge.net)
#
# This file defines a Python class for finite first-order models
# and various operations on such models.
#
# Version of 2011-03-27
#

import os
import sys
import tempfile
import subprocess
import timeit

from sage.functions.trig import cos, sin
from sage.functions.other import sqrt

import config

from proof import ProverMaceSol, getops
from misc import readfile, writefile
from model import Model
from display import opstr
from fo import FOclass
import fotheories

# TODO emprolijar lo que sigue, seria mejor que estuvieran adentro del modelo directamente
import minion
Model.is_congruence_closed = minion.is_congruence_closed
Model.is_hom_image = minion.is_hom_image
Model.is_subalgebra = minion.is_subalgebra
Model.is_isomorphic = minion.is_isomorphic

def checkSubalgebra(A, sub):  # sub is a partial subalgebra
    """Check that sub is closed under the operations of A"""
    for x in range(A.cardinality):
        for r in A.operations:
            op = A.operations[r]
            if sub[x] == 1:
                if type(op) == list:
                    if type(op[0]) != list:
                        if sub[op[x]] == 0:
                            return False
                    else:
                        for y in range(A.cardinality):
                            if sub[y] == 1 and sub[op[x][y]] == 0:
                                return False
    return True


def completeSubalgebra(A, sub, i, subl):
    # find next i where sub[i]=2=undefined; for each val=0 or 1
    # set sub[i]=val, check closure
    # restore and return if no completetion,
    # else call completeSubalgebra(rel,i+1)
    ok = True
    while ok and i < len(sub) and sub[i] != 2:
        i += 1
    if i < len(sub):
        ok = False
    if ok:
        subl.append([j for j in range(len(sub)) if sub[j] == 1])
    else:
        for val in range(2):
            sub[i] = val
            ok = checkSubalgebra(A, sub)
            if ok:
                completeSubalgebra(A, sub, i + 1, subl)
            sub[i] = 2





def linExt(U):
    """Listing 11.3 Freese-Jezek-Nation, a-<b => a in U[b] => a<=b"""
    P = range(len(U))
    S = []
    Z = []
    I = [0 for i in P]
    for a in P:
        for b in U[a]:
            if b != a:
                I[b] = I[b] + 1
    for a in P:
        if I[a] == 0:
            Z.append(a)
    while Z != []:
        a = Z.pop()
        S.append(a)
        for b in U[a]:
            if b != a:
                I[b] = I[b] - 1
                if I[b] == 0:
                    Z.append(b)
    return S


def permutedleq(le, S):
    n = len(S)
    T = range(n)
    for i in range(len(S)):
        T[S[i]] = i
    return [[le[T[x]][T[y]] for y in range(n)] for x in range(n)]


def invPermutedPo(P, S):
    T = range(len(S))
    for i in range(len(S)):
        T[S[i]] = i
    P = Posetuc([sorted(T[y] for y in P.uc[x]) for x in S])
    P.perm = S
    return P


def topological(P):
    return invPermutedPo(P, linExt(P.uc))


def leq2uc(le):  # assumes le[x][y] => x <= y (topologically sorted)
    n = len(le)
    uc = []
    for a in range(n):
        S = []   # accumulate upper covers of a
        for x in range(a + 1, n):
            if le[a][x] == 1:
                y = len(S) - 1
                while y >= 0 and le[S[y]][x] == 0:
                    y = y - 1
                if y < 0:
                    S.append(x)
        uc.append(S)
    return uc


def meet2uc(m):  # also assumes topologically sorted
    n = len(m)
    uc = []
    for a in range(n):
        S = []
        for x in range(a + 1, n):
            if m[a][x] == a:
                y = len(S) - 1
                while y >= 0 and m[S[y]][x] != S[y]:
                    y = y - 1
                if y < 0:
                    S.append(x)
        uc.append(S)
    return uc


def Posetuc(uppercovers, leq=None):
    """
    Genera un poset con la upper covers, y opcionalmente la relacion <=
    """
    mdl = Model(cardinality=len(uppercovers), operations={}, relations={})
    mdl.uc = dict([(x, uppercovers[x]) for x in range(len(uppercovers))])
    if leq != None:
        mdl.relations = {"<=": leq}
    return mdl


def isofilter(li):
    """
    Saca los isomorfismos de una lista de modelos.
    """
    # TODO EN REALIDAD MODEL LO USA, PERO TODAVIA NO LO TIENE IMPORTADO
    st = "\n".join([x.mace4format() for x in li])
    writefile('tmpiso.in', st)
    os.system(config.uapth + 'interpformat standard -f tmpiso.in | ' +
              config.uapth + 'isofilter |' + config.uapth + 'interpformat portable >tmpiso.out')
    st = readfile('tmpiso.out')
    l = eval(st.replace("\\", "\\\\"))
    models = []
    for m in l:
        models += [Model(m[0], m[1][0][9:-1], getops(m[2], 'function'), getops(m[2], 'relation'))]
    return models



#############################################
# Conversions

def Monoid2ISeqAat(A):
    base = range(len(A))
    return Model(cardinality=len(A), operations={},
                 relations={'C': [[[1 if A.operations['*'][i][j] == k else 0
                                    for k in base] for j in base] for i in base]})


def exclusions(m, n):
    return ["-C(" + str(i) + "," + str(j) + "," + str(k) + ")" for i in range(m)
            for j in range(m) for k in range(m, n)]


def check_relative_embedding(A, k):
    m = len(A) + (len(A) - len(invertibles(A))) + k
    return prover9(IRAat1.axioms + Monoid2ISeqAat(A).diagram("") +
                   exclusions(len(A), m), [], 10000, 0, m, one=True)


def invertibles(A):
    return [x for x in range(len(A)) if
            any(A.operations['*'][x][y] == 1 for y in range(len(A)))]

#a=Mon.find_models(3); check_relative_embedding(a[0],1)
#a=Mon.find_models(4);[i for i in range(len(a)) if check_relative_embedding(a[i],1)==[]]
#a=Mon.find_models(4);[i for i in [2, 3, 11, 12, 13, 14, 15, 17, 18, 20, 22, 23, 25, 26, 27, 28, 31, 32, 33] if check_relative_embedding(a[i],2)==[]]


def ring2model(R):
    x = R.list()
    op = {}
    op["+"] = [[x.index(x[i] + x[j]) for j in range(len(x))] for i in range(len(x))]
    if hasattr(x[0], "list"):
        op["*"] = [[x.index(vector([x[i][k] * x[j][k] for
                                    k in range(len(x[0]))])) for j in range(len(x))] for i in range(len(x))]
    else:
        op["*"] = [[x.index(x[i] * x[j]) for j in range(len(x))] for i in range(len(x))]
    op["-"] = [x.index(-x[i]) for i in range(len(x))]
    return Model(cardinality=len(x), operations=op, relations={})


def Reduct(A, li):  # Compute the reduct of an algebra
    B = Model(cardinality=A.cardinality, index=A.index, operations=A.operations.copy(), relations={})
    if type(li) == 'str':
        li = [li]
    for st in li:
        if st in B.operations:
            del B.operations[st]
    return B


def checkRelation(A, R):  # R is a partial binary relation
    # Check that rel is transitive and compatible with the operations of A
    n = A.cardinality
    for x in range(n):
        for y in range(n):
            if R[x][y] == 1 and x != y:
                for z in range(x + 1, n):
                    if R[y][z] == 1 and R[x][z] == 0:
                        return False  # not transitive
                for f in A.operations.values():
                    if type(f) == list:
                        if type(f[0]) != list:  # unary op
                            if R[f[x]][f[y]] == 0:
                                return False
                        else:
                            for z in range(n):  # binary op
                                if R[f[x][z]][f[y][z]] == 0:
                                    return False
                                if R[f[z][x]][f[z][y]] == 0:
                                    return False
    return True


def completeRelation(A, R, i, j):
    # find next i,j where rel[i][j]=2=undefined; for each val=0 or 1
    # set rel[i][j]=val, check transitivity and compatibility
    # restore and return if no completetion,
    # else call completeRelation(rel,i,j+1)
    global congl
    ok = True
    while ok and i < len(R):
        while j < len(R) and R[i][j] != 2:
            j = j + 1
        if j >= len(R):
            j = 0
            i = i + 1
        else:
            ok = False
    if ok:
        congl.append([R[i][:] for i in range(len(R))])
    else:
        for val in range(2):
            R[i][j] = val
            R[j][i] = val
            ok = checkRelation(A, R)
            if ok:
                completeRelation(A, R, i, j + 1)
            R[i][j] = 2
            R[j][i] = 2


def congruences_slow(A):
    # A is a finite algebra
    global congl
    congl = []
    R = [[1 if i == j else 2 for j in range(A.cardinality)] for i in range(A.cardinality)]
    completeRelation(A, R, 0, 0)
    return congl


def isTransitiveRel(R):
    for x in range(n):
        for y in range(n):
            if R[x][y] == 1 and x != y:
                for z in range(n):
                    if R[y][z] == 1 and R[x][z] == 0:
                        return False  # not transitive
    return True


def isSubrelationSym(R, S):  # assumes symmetry of relations
    n = len(R)
    for i in range(n):
        for j in range(i + 1, n):
            if R[i][j] > S[i][j]:
                return False
    return True


def cong_leq(cl):  # input list of symmetric 0-1-relations
    return [[i == j or isSubrelationSym(cl[i], cl[j]) for j in range(len(cl))]
            for i in range(len(cl))]


def leq2uppercovers(R):
    n = len(R)
    uc = [[] for i in range(n)]
    for i in range(n):
        for j in range(n):
            if R[i][j] and i != j:
                k = 0
                while k < n and not(R[i][k] and i != k and R[k][j] and k != j):
                    k += 1
                if k == n:
                    uc[i].append(j)
    return uc


def part2str(P):
    return "|".join(",".join(str(i) for i in x) for x in P)


def str2part(s):
    return [[int(c) for c in t.split(',')] for t in s[1:-1].split('|')]


def eqrelblock(co, i):
    block = []
    for j in range(len(co)):
        if co[i][j] == 1:
            block.append(j)
    return block


def eqrel2part(co):
    part = []
    flag = [False for i in range(len(co))]
    for i in range(len(co)):
        if not flag[i]:
            cb = eqrelblock(co, i)
            for j in range(len(cb)):
                flag[cb[j]] = True
            part.append(cb)
    return part


def part2eqrel(P):  # P is a list of blocks on [0..n-1]
    n = max(max(block) for block in P) + 1
    R = [n * [0] for i in range(n)]
    for block in P:
        for i in block:
            for j in block:
                R[i][j] = 1
    return R


def showCongruences(A):
    return [part2str(eqrel2part(co)) for co in congruences_slow(A)]


def ConLat(A):
    cl = congruences_slow(A)  # slow non-UA calculator backtracking
    return Model(cardinality=len(cl), index=A.index,
                 uc=leq2uppercovers(cong_leq(cl)))


def ConL(A):
    from sage.combinat.posets.lattices import LatticePoset
    le = cong_leq([part2eqrel(str2part(x)) for x in Con(A)])
    return LatticePoset((range(len(le)), lambda x, y: le[x][y]))


def Con(A):
    print A
    print type(A)
    """
    Return a list of strings that represent congruences of A as partitions
    """
    return A.ConUACalc()


def JCon(A): return A.JConUACalc()


def MCon(A): return A.MConUACalc()


def Sub(A):
    """
    Return a list of lists that contain the elements of subalgebras of A
    """
    return A.SubUACalc()

#
# Enumerate lattices with a Python implementation of the algorithm from
#    J. Heitzig and J. Reinhold, Counting finite lattices,
#    Algebra Universalis 48 (2002) 43-53.
#
# Author:  Peter Jipsen (2009-08-20): initial version
#
# Note:    This file is Python code with no Sage dependencies but usable in Sage
#
# Example: Find all nonisomorphic lattices of cardinality 5:
#
#         all_lattices(5)
#
#         The output is a list of adjacency lists giving the upper cover relation
#         on the set {0,...,n-3} for L without bottom and top element
#         E.g. the 5 element nonmodular lattice is [[], [], [0]]
#
#         The algorithm also enumerates finite (meet or join) semilattices
#         (add only the top or bottom element)
#
#*****************************************************************************
#           Copyright (C) 2009 Peter Jipsen <jipsen@chapman.edu>
#
# Distributed  under  the  terms  of  the  GNU  General  Public  License (GPL)
#                         http://www.gnu.org/licenses/
#*****************************************************************************

#from UA import *
#import psyco
# psyco.full()


def permutations(m, n):
    # return list of all permutations of {m,...,n-1}
    p = [m + i for i in range(n - m)]
    ps = [p]
    n = len(p)
    j = 1
    while j >= 0:
        q = range(n)
        j = n - 2
        while j >= 0 and p[j] > p[j + 1]:
            j = j - 1
        if j >= 0:
            for k in range(j):
                q[k] = p[k]
            k = n - 1
            while p[j] > p[k]:
                k = k - 1
            q[j] = p[k]
            i = n - 1
            while i > j:
                q[i] = p[j + n - i]
                i = i - 1
            q[j + n - k] = p[j]
            p = q
            ps.append(q)
    return ps


def inverse_permutation(p):  # assumes permutation is on {0,...,len(p)-1}
    q = range(len(p))
    for i in range(len(p)):
        q[p[i]] = i
    return q


def achains0(A, x, B):
    # find disjoint subsets of A U [x] U B (if it intersects blevs)
    # A is a set of pairwise disjoint elements, each a in A is disjoint
    # from x and from all elements of B
    A1 = A + [x]
    u = [y for y in range(0, m) if any([le[c][y] for c in A1])]
    if sum([2**j for j in A1]) >= wm1 and all([all([any([le[c][u[i]] and le[c][u[j]] for c in A1]) or not any([le[c][u[i]] and le[c][u[j]] for c in Zc]) for j in range(i)]) for i in range(len(u))]):
        As.append(A1[:])
    if B != []:
        if blevs.intersection(A + B) != []:
            achains0(A, B[0], B[1:])
        B1 = []
        C = [c for c in Zc if le[c][x]]
        for b in B:
            #(for antichains) if not(le[x][b] or le[b][x]): B1.append(b)
            if not any([le[c][b] for c in C]):
                B1.append(b)
        if B1 != []:
            achains0(A1, B1[0], B1[1:])


def lattice_antichains(L, lev, dep):
    # find subsets A of L-{0} such that a,b in up(A) implies a^b in {0} U up(A)
    # and A intersects lev(k-1) U lev(k) where k = dep(n-1)
    # and sum(2^j for j in A) >= w(n-1)
    global wm1, m, blevs, As, Zc
    wm1 = sum([2**j for j in L[-1]])
    m = len(L)
    k = dep[m - 1]
    blevs = set(lev[k - 1] + lev[k])  # bottom two levels
    As = []
    Zc = set(range(m)).difference(reduce(lambda x, y: set(x) | set(y), L))  # minimal elements
    achains0([], 0, range(1, m))
    if len(lev) == 1:
        return [[]] + As
    return As


def is_canonical_lattice(L, lev):
    # let k=dep(n), m=max(lev[k-1])+1 and Lm = L|{0..m-1}.
    # generate all level-preserving permutations
    perms = [permutations(l[0], l[-1] + 1) for l in lev]
    ps = perms[0]
    for i in range(1, len(lev)):
        newps = []
        for p in ps:
            for q in perms[i]:
                newps.append(p + q)
        ps = newps
    w = [sum([2**j for j in u]) for u in L]  # weight of L
    for p in ps[1:]:
        pw = [sum([2**p[j] for j in u]) for u in L]
        q = inverse_permutation(p)
        pw = [pw[i] for i in q]
        if w > pw:
            return False
    return True


def next_lattice(L, lev, dep, n, count):
    global lat_count, lat_list
    m = len(L)  # new element to be added
    if m < n:
        for A in lattice_antichains(L, lev, dep):
            L_A = L + [A]  # add covers of new element
            if A != [] and A[-1] in lev[-1]:
                lev_A = lev + [[m]]  # update level
            else:
                lev_A = lev[:-1] + [lev[-1] + [m]]
            if is_canonical_lattice(L_A, lev_A):
                for j in range(m):  # update less_or_equal relation
                    le[m][j] = any([le[i][j] for i in A])
                if A != [] and A[-1] in lev[-1]:
                    dep_A = dep + [len(lev)]  # update depth
                else:
                    dep_A = dep + [len(lev) - 1]
                next_lattice(L_A, lev_A, dep_A, n, count)
    elif count:
        lat_count = lat_count + 1
    # else: lat_list.append([c[:] for c in L])
    else:
        lat_list.append(addbounds(L))


def addbounds(L):
    # add top and bottom element and relabel so that i <= j if le[i][j]
    m = len(L)
    p = range(m, 0, -1)
    Lp = [[m + 1] if u == [] else sorted([p[j] for j in u]) for u in L]
    Lp.reverse()
    Lp.append([])
    M = set(range(1, m + 1)) - reduce(lambda x, y: set(x) | set(y), Lp)  # minimal elements
    return Posetuc([list(M)] + Lp)


def all_lattices(n, count=False):
    # construct (or count) all lattices of cardinality n
    global le, lat_count, lat_list
    lat_list = []
    lat_count = 0
    # initialize less_or_equal relation
    le = [[True if i == j else False for j in range(n - 2)] for i in range(n - 2)]
    next_lattice([[]], [[0]], [0], n - 2, count)
    return lat_count if count else lat_list

from time import *


def tlat(n):
    t = clock()
    return all_lattices(n, True), clock() - t


def Chain(n):
    c = [[x + 1] for x in range(n)]
    c[n - 1] = []
    return Posetuc(c)


def Antichain(n):
    c = [[] for x in range(n)]
    return Posetuc(c)


def Pentagon():
    p = Posetuc([[1, 2], [4], [3], [4], []])
    p.pos = [[2, 0], [0, 2], [3, 1], [3, 3], [2, 4]]
    return p


def Diamond(n):
    c = [[n - 1] for x in range(n)]
    c[0] = [x for x in range(1, n - 1)]
    c[n - 1] = []
    return Posetuc(c)


def is_automorphism(p, m):  # p[m[i][j]] == m[p[i]][p[j]]
    n = len(m)
    for i in range(n):
        for j in range(n):
            if p[m[i][j]] != m[p[i]][p[j]]:
                return False
    return True


def closed_sets(Y):
    n = max(max(b) for b in Y if b != []) + 1
    top = frozenset(range(n))
    B = [frozenset(b) for b in Y]
    C = set([frozenset(range(n + 1))]) if top in B else set([top])
    for b in B:
        C = C.union(set(b.intersection(a) for a in C))
    return list(C)


class GaloisStr():

    def __init__(self, X, Y, num=None):
        self.X = X
        self.Y = Y  # basic closed sets
        if num != None:
            self.num = num

    def __repr__(self):
        return "\nGaloisStr(X=range(%s), " % len(self.X) + ("num = %s," % self.num if hasattr(self, 'num') else "") + "Y=%s)" % self.Y

    def lattice(self):
        C = closed_sets(self.Y)
        n = len(C)
        #f = dict([C[i],i] for i in range(n))
        le = [[(1 if s.issubset(t) else 0) for s in C] for t in C]
        U = [[j for j in range(n) if le[i][j]] for i in range(n)]
        # print U,linExt(U)
        return Posetuc(leq2uc(permutedleq(le, linExt(U))))





def SI(As):
    """
    Filter the subdirectly irreducible algebras out of a list of algebras
    """
    return [A for A in As if A.is_SI()]


def Simple(As):
    """
    Filter the simple algebras out of a list of algebras
    """
    return [A for A in As if A.is_simple()]


def depth_setsW(self):
    """
    Returns a list l such that l[i+1] is the set of maximal elements of
    the poset obtained by removing the elements in l[0], l[1], ...,
    l[i].

    EXAMPLES::

        sage: P = Poset({0:[1,2],1:[3],2:[3],3:[]})
        sage: [len(x) for x in P.depth_sets()]
        [1, 2, 1]

    ::

        sage: Q = Poset({0:[1,2], 1:[3], 2:[4], 3:[4]})
        sage: [len(x) for x in Q.depth_sets()]
        [1, 1, 2, 1]
    """
    return [map(self._vertex_to_element, depth) for depth in
            self._hasse_diagram.depth_sets()]


def depth_setsM(self):
    """
    Returns a list l such that l[i+1] is the set of maximal elements of
    the poset obtained by removing the elements in l[0], l[1], ...,
    l[i].

    EXAMPLES::

        sage: from sage.combinat.posets.hasse_diagram import HasseDiagram
        sage: H = HasseDiagram({0:[1,2],1:[3],2:[3],3:[]})
        sage: [len(x) for x in H.depth_sets()]
        [1, 2, 1]

    ::

        sage: from sage.combinat.posets.hasse_diagram import HasseDiagram
        sage: H = HasseDiagram({0:[1,2], 1:[3], 2:[4], 3:[4]})
        sage: [len(x) for x in H.depth_sets()]
        [1, 1, 2, 1]
    """
    G = self.copy()
    depths = []
    while G.vertices() != []:
        outdegs = G.out_degree(labels=True)
        new_depth = [x for x in outdegs if outdegs[x] == 0]
        depths.append(new_depth)
        G.delete_vertices(new_depth)
    return depths

"""
Graph Theory Cython functions

AUTHORS:
    -- Robert L. Miller   (2007-02-13): initial version
    -- Robert W. Bradshaw (2007-03-31): fast spring layout algorithms
"""

#*****************************************************************************
#           Copyright (C) 2007 Robert L. Miller <rlmillster@gmail.com>
#                         2007 Robert W. Bradshaw <robertwb@math.washington.edu>
#
# Distributed  under  the  terms  of  the  GNU  General  Public  License (GPL)
#                         http://www.gnu.org/licenses/
#*****************************************************************************
from random import random


def spring_layout(G, iterations=50, dim=2, vpos=None, rescale=True, height=False, vfix=None):
    """
    Spring force model layout

    This function primarily acts as a wrapper around run_spring, 
    converting to and from raw c types. 

    This kind of speed cannot be achieved by naive pyrexification of the 
    function alone, especially if we require a function call (let alone
    an object creation) every time we want to add a pair of doubles. 

    EXAMPLE:
        sage: G = graphs.DodecahedralGraph()
        sage: for i in range(10): G.add_cycle(range(100*i, 100*i+3))
        sage: from sage.graphs.graph_fast import spring_layout_fast
        sage: spring_layout_fast(G)
        {0: [..., ...], ..., 502: [..., ...]}

    """
    G = G.to_undirected()
    vlist = G.vertices()  # this defines a consistent order

    n = G.order()
    if n == 0:
        return {}

    pos = [0] * (n * dim)

    # convert or create the starting positions as a flat list of doubles
    if vpos is None:  # set the initial positions randomly in 1x1 box
        for i in range(n * dim):  # from 0 <= i < n*dim:
            pos[i] = random()
    else:
        for i in range(n):  # from 0 <= i < n:
            loc = vpos[vlist[i]]
            for x in range(dim):  # from 0 <= x <dim:
                pos[i * dim + x] = loc[x]

    # here we construct a lexicographically ordered list of all edges
    # where elist[2*i], elist[2*i+1] represents the i-th edge
    elist = [0] * (2 * len(G.edges()) + 2)

    cur_edge = 0

    for i in range(n):  # from 0 <= i < n:
        for j in range(i + 1, n):  # from i < j < n:
            if G.has_edge(vlist[i], vlist[j]):
                elist[cur_edge] = i
                elist[cur_edge + 1] = j
                cur_edge += 2

    # finish the list with -1, -1 which never gets matched
    # but does get compared against when looking for the "next" edge
    elist[cur_edge] = -1
    elist[cur_edge + 1] = -1

    # here we construct a True/False list of fixed vertices
    fixed = [False] * n
    if not vfix is None:
        for i in range(n):  # from 0 <= i < n:
            fixed[i] = vlist[i] in vfix

    run_spring(iterations, dim, pos, elist, n, height, fixed)

    # recenter
    max_r2 = 0
    if rescale:
        cen = [0] * dim
        for i in range(n):  # from 0 <= i < n:
            for x in range(dim):  # from 0 <= x < dim:
                cen[x] += pos[i * dim + x]
        for x in range(dim):  # from 0 <= x < dim:
            cen[x] /= n
        for i in range(n):  # from 0 <= i < n:
            r2 = 0
            for x in range(dim):  # from 0 <= x < dim:
                pos[i * dim + x] -= cen[x]
                r2 += pos[i * dim + x] * pos[i * dim + x]
            if r2 > max_r2:
                max_r2 = r2
        r = 1 if max_r2 == 0 else sqrt(max_r2)
        for i in range(n):  # from 0 <= i < n:
            for x in range(dim):  # from 0 <= x < dim:
                pos[i * dim + x] /= r

    # put the data back into a position dictionary
    vpos = {}
    for i in range(n):
        vpos[vlist[i]] = [pos[i * dim + x] for x in range(dim)]

    return vpos


def run_spring(iterations, dim, pos, edges, n, height, fixed):
    """
    Find a locally optimal layout for this graph, according to the 
    constraints that neighboring nodes want to be a fixed distance 
    from each other, and non-neighboring nodes always repel. 

    This is not a true physical model of mutually-repulsive particles 
    with springs, rather it is more a model of such things traveling, 
    without any inertia, through an (ever thickening) fluid. 

    TODO: The inertial model could be incorporated (with F=ma)
    TODO: Are the hard-coded constants here optimal? 

    INPUT:
        iterations -- number of steps to take
        dim        -- number of dimensions of freedom
        pos        -- already initialized initial positions
                      Each vertex is stored as [dim] consecutive doubles.
                      These doubles are then placed consecutively in the array. 
                      For example, if dim=3, we would have
                      pos = [x_1, y_1, z_1, x_2, y_2, z_2, ... , x_n, y_n, z_n]
        edges      -- List of edges, sorted lexicographically by the first 
                      (smallest) vertex, terminated by -1, -1.
                      The first two entries represent the first edge, and so on. 
        n          -- number of vertices in the graph
        height     -- if True, do not update the last coordinate ever
        fixed      -- if fixed[i] True, do not update pos[i] ever

    OUTPUT: 
        Modifies contents of pos.

    AUTHOR: 
        Robert Bradshaw
    """
    t = 1
    dt = t / (1e-20 + iterations)
    k = sqrt(1.0 / n)
    delta = [0] * dim

    if height:
        update_dim = dim - 1
    else:
        update_dim = dim

    for cur_iter in range(iterations):
        cur_edge = 1  # offset by one for fast checking against 2nd element first
        disp = [[0] * dim for i in range(n)]
        for i in range(n):  # from 0 <= i < n:
            for j in range(i + 1, n):
                for x in range(dim):
                    delta[x] = pos[i * dim + x] - pos[j * dim + x]

                square_dist = delta[0] * delta[0]
                for x in range(1, dim):
                    square_dist += delta[x] * delta[x]

                if square_dist < 0.01:
                    square_dist = 0.01

                # they repel according to the (capped) inverse square law
                force = k * k / square_dist

                # and if they are neighbors, attract according to Hooke's law
                if edges[cur_edge] == j and edges[cur_edge - 1] == i:
                    force -= sqrt(square_dist) / k
                    cur_edge += 2

                # add this factor into each of the involved points
                for x in range(dim):
                    disp[i][x] += delta[x] * force
                    disp[j][x] -= delta[x] * force

        # now update the positions
        for i in range(n):
            if not fixed[i]:
                square_dist = disp[i][0] * disp[i][0]
                for x in range(1, dim):
                    square_dist += disp[i][x] * disp[i][x]

                scale = t / (1 if square_dist < 0.01 else sqrt(square_dist))
                # if i == 1:print scale,square_dist
                for x in range(update_dim):
                    pos[i * dim + x] += disp[i][x] * scale

        t -= dt
    # print pos[3:6]

# used to save SI lattice lists Dec 2010
# time saveSIlat(12)


def savelistinfile(fn, li):
    fh = open(fn, 'w')
    fh.write('[\n' + ',\n'.join([str(x.uc) for x in li]) + ']')
    fh.close()


def saveSIlat(n):
    li = all_lattices(n)
    k = len(li)
    li = SI(li)
    savelistinfile("silat" + str(n) + "." + str(len(li)), li)
    return k, len(li)


def readlistfromfile(st):
    import gzip
    f = gzip.open(config.datapth + st + '.gz', 'rb')
    li = f.read()
    f.close()
    return li


def readSIlattices(n=None):
    li = eval(readlistfromfile('silat2_11'))
    if n != None:
        li = li[:n]
    return [Posetuc(x) for x in li]


def subalgPoset(a, fn):
    # a is a list of nonisomorphic algebras ordered by increasing cardinality
    # return a poset P on [0..len(a)] s.t. P.leq[j][i] iff a[j].inS(a[i])
    n = len(a)
    fh = open(fn, 'w')
    fh.write('{')
    lc = {}
    for i in range(n):
        lc[i] = []
    ideal = [set([i]) for i in range(n)]
    for i in range(1, n):  # add a[i] to P
        for j in range(i - 1, -1, -1):  # search in reverse
            if a[j].cardinality < a[i].cardinality and not j in ideal[i] and \
               a[j].inS(a[i]) != False:
                lc[i].append(j)
                ideal[i] = ideal[i] | ideal[j]
        fh.write(str(i) + ':' + str(lc[i]) + ',\n')
        fh.flush()
    fh.write('}')
    fh.close()
    # return lc


def homsubPoset(a, fn):
    # a is a list of nonisomorphic algebras ordered by increasing cardinality
    # return a poset P on [0..len(a)] s.t. P.leq[j][i] iff a[j].inHS(a[i])
    n = len(a)
    fh = open(fn, 'w')
    fh.write('{')
    lc = {}
    for i in range(n):
        lc[i] = []
    ideal = [set([i]) for i in range(n)]
    for i in range(1, n):  # add a[i] to P
        for j in range(i - 1, -1, -1):  # search in reverse
            # print i,j
            if a[j].cardinality < a[i].cardinality and not j in ideal[i] and \
               a[j].inHS(a[i]) != False:
                lc[i].append(j)
                ideal[i] = ideal[i] | ideal[j]
        fh.write(str(i) + ':' + str(lc[i]) + ',\n')
        fh.flush()
    fh.write('}')
    fh.close()


def lattice_getpos3d(P):
    # moved here to avoid import error
    from sage.combinat.posets.posets import FinitePoset
    FinitePoset.depth_sets = depth_setsW
    from sage.combinat.posets.hasse_diagram import HasseDiagram
    HasseDiagram.depth_sets = depth_setsM
    g = P.hasse_diagram().to_undirected()
    l = P.level_sets()
    height = {}
    for i in range(len(l)):
        for j in l[i]:
            height[j] = i
    d = P.depth_sets()
    depth = {}
    for i in range(len(d)):
        for j in d[i]:
            depth[j] = i
    vpos = {}
    h = 4.0 if P.is_chain() else 1.0
    for i in range(len(l)):
        v = l[i]
        for j in range(len(v)):
            vpos[v[j]] = [cos(j * 6.28 / len(v)), sin(j * 6.28 / len(v)),
                          h * (i + len(l) - depth[v[j]] - 1) / len(l)]
    vpos[g.vertices()[0]] = [0., 0., 0.]
    vpos[g.vertices()[-1]] = [0., 0., h * 2 * (len(l) - 1) / len(l)]
    d = spring_layout(g, dim=3, vpos=vpos, height=True,
                      vfix=[g.vertices()[0], g.vertices()[-1]])
    pos = dict([i, d[i]] for i in d.keys())
    return pos


def lattice_getpos(L, nang, adjust=0):
    p = lattice_getpos3d(L)
    q = [p[i] for i in p]
    bestang = 0.0
    bestsep = 0
    for a in range(nang):
        angle = a * 6.28 / nang
        li = [abs(-q[i][0] * sin(angle) + q[i][1] * cos(angle) - (-q[j][0] * sin(angle) + q[j][1] * cos(angle))) for i in range(len(q)) for j in range(i + 1, len(q)) if abs(q[i][2] - q[j][2]) < 0.4]
        minsep = min(li) if len(li) > 0 else 0
        if minsep > bestsep:
            bestsep = minsep
            bestang = angle
    p = dict([i, [round(-p[i][0] * sin(bestang + adjust) + p[i][1] * cos(bestang + adjust), 2),
                  round(p[i][2], 2)]] for i in p)
    return p


def latticeplot(self, nang=50, adjust=0, label_elements=True, element_labels=None,
                label_font_size=5, label_font_color='black',
                vertex_size=65, vertex_colors="yellow", figsize=2, title="", **kwds):
    from sage.plot.text import text
    if label_elements and element_labels is None:
        element_labels = self._elements
    pos = lattice_getpos(self, nang, adjust)
    return self.hasse_diagram().to_undirected().plot(
        label_elements=label_elements, element_labels=element_labels,
        label_font_size=label_font_size, label_font_color=label_font_color,
        vertex_size=vertex_size, vertex_colors=vertex_colors, pos=pos, **kwds) + text((self.name if hasattr(self, 'name') else title), (0, -.08), axes=False, vertical_alignment='bottom', axis_coords=True)


def latticeshow(self, nang=50, adjust=0, label_elements=True, element_labels=None,
                label_font_size=5, label_font_color='black',
                vertex_size=65, vertex_colors="yellow", figsize=2, **kwds):
    if label_elements and element_labels is None:
        element_labels = self._elements
    pos = lattice_getpos(self, nang, adjust)
    p = self.hasse_diagram().to_undirected().plot(
        label_elements=label_elements, element_labels=element_labels,
        label_font_size=label_font_size, label_font_color=label_font_color,
        vertex_size=vertex_size, vertex_colors=vertex_colors, pos=pos, **kwds)
    dx = (p.xmax() - p.xmin()) / 10
    if dx < .15:
        dx = .15
    dy = (p.ymax() - p.ymin()) / 10
    if dy < .15:
        dy = .15
    return p.show(figsize=figsize,
                  xmin=p.xmin() - dx, xmax=p.xmax() + dx, ymin=p.ymin() - dy, ymax=p.ymax() + dy)


def latticeplot3d(P, frame=False, translate=[0, 0, 0]):
    g = P.hasse_diagram().to_undirected()
    pos = lattice_getpos3d(P)
    return g.plot3d(vertex_size=0.04, edge_size=0.01, frame=frame, pos3d=pos, vertex_colors={(0, 0, 1): [g.vertices()[0]], (0, 1, 0): [g.vertices()[-1]], (1, 0, 0): g.vertices()[1:-1]})


def latticeshow3d(P, frame=False, translate=[0, 0, 0]):
    show(latticeplot3d(P))


def posetplot3d(P, iterations=20, frame=False, translate=[0, 0, 0]):
    g = P.hasse_diagram().to_undirected()
    l = P.level_sets()
    vpos = {}
    h = 3.0 if P.is_chain() else 0.95
    for i in range(len(l)):
        for j in l[i]:
            vpos[j] = [random(), random(), (2. * i) / len(l)]
    vpos[g.vertices()[0]] = [0., 0., 0.]
    d = spring_layout(g, iterations=iterations, dim=3, vpos=vpos, height=True)
    pos = dict([i, [round(d[i][0], 2) + translate[0], round(d[i][1], 2) + translate[1], round(d[i][2], 2) + translate[2]]] for i in d.keys())
    return g.plot3d(edge_size=0.01, frame=frame, pos3d=pos, vertex_colors={(0, 0, 1): [g.vertices()[0]], (1, 0, 0): g.vertices()[1:]})


def posetshow3d(P, iterations=20, frame=False, translate=[0, 0, 0]):
    show3d(posetplot3d(P))

from sage.combinat.posets.posets import FinitePoset
FinitePoset.plot = latticeplot
FinitePoset.show = latticeshow
FinitePoset.plot3d = latticeplot3d
FinitePoset.show3d = latticeshow3d


def to_posets_arrays(list, cols, **kwds):
    from sage.plot.plot import graphics_array
    # moved here to avoid import error
    plist = []
    g_arrays = []
    for i in range(len(list)):
        if (isinstance(list[i], FinitePoset)):
            plist.append(list[i].plot(vertex_size=50, vertex_labels=False, graph_border=True))
        else:
            raise TypeError, 'Param list must be a list of Sage posets.'

    rows = 5
    rc = rows * cols
    num_arrays = len(plist) / rc
    if (len(plist) % rc > 0):
        num_arrays += 1

    for i in range(num_arrays - 1):
        glist = []
        for j in range(rows * cols):
            glist.append(plist[i * rows * cols + j])
        ga = graphics_array(glist, rows, cols)
        ga.__set_figsize__([12, 10])
        g_arrays.append(ga)

    last = len(plist) % rc
    if (last == 0 and len(plist) != 0):
        last = rc
    index = (num_arrays - 1) * rows * cols
    last_rows = last / cols
    if (last % cols > 0):
        last_rows += 1

    glist = []
    for i in range(last):
        glist.append(plist[i + index])
    ga = graphics_array(glist, last_rows, cols)
    ga.__set_figsize__([12, 2 * last_rows])
    g_arrays.append(ga)
    return g_arrays


def show_posets(list, cols=10, **kwds):
    ga_list = to_posets_arrays([x.sage_lattice() if x.is_lattice()
                                else x.sage_poset() for x in list], cols, **kwds)
    for i in range(len(ga_list)):
        (ga_list[i]).show(axes=False)
    return

# Congruence lattices


def con2model(S, index=None):  # S is a list or (frozen)set of partition strings
    le = cong_leq([part2eqrel(str2part(x)) for x in S])
    n = len(le)
    U = [[y for y in range(n) if le[x][y]] for x in range(n)]
    P = Posetuc(U)
    P = topological(P)
    le = [[0 for x in range(n)] for y in range(n)]
    for x in range(n):
        for y in P.uc[x]:
            le[x][y] = 1
    P = Posetuc(leq2uc(le), le)
    P.index = index
    return P


def counts(li):
    """
    Summarise a list with duplicates by counting how often each item appears
    """
    d = {}
    for x in li:
        d[x] = d.get(x, 0) + 1
    return dict(sorted([x, d[x]] for x in d))


