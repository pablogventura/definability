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

from proof import prover9
from misc import readfile, writefile
from model import Model
from display import opstr, oprelstr


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



def getops(li, st):
    # TODO , PARECIERA QUE DEBERIA SER UN METODO INTERNO DE LOS MODELOS QUE DEVUELVE MACE4
    """extract operations/relations from the Prover9 model, se usa en isofilter y prover9"""
    result = {}
    for op in li:
        if op[0] == st:
            result[op[1]] = op[3]
    return result

##################### TODO TODO TODO POR ACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
##################### TODO TODO TODO POR ACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
##################### TODO TODO TODO POR ACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA



FOclasses = []
FirstOrderClasses = []


class FOclass():

    def __init__(self, abbr, name, axioms, results=[], options=[], syntax='Prover9'):
        """
        Define a first-order class of models by a list of first-order axioms

        INPUT:
            abbr    -- a short string without spaces abbreviating the name
            name    -- a string giving the name of the class
            axioms  -- list of strings in the given syntax
            results -- list of strings in the given syntax
            options -- list of strings defining the syntax
            syntax  -- a string indicating which program can parse the 
                       axioms, results and options
        """
        self.abbr = abbr
        self.name = name
        self.syntax = syntax
        self.axioms = axioms
        self.results = results
        self.options = options
        FOclasses.append(abbr)
        FOclasses.sort(key=str.lower)
        FirstOrderClasses.append(name + " (" + abbr + ")")
        FirstOrderClasses.sort(key=str.lower)

    def __repr__(self):
        """
        Display a first-order class in a way that can be parsed by Python
        """
        st = 'FOclass(\"' + self.name + '\", syntax=\"' + self.syntax +\
             '\"' + ', axioms=[ \n\"' + '\",\n\"'.join(self.axioms) + '\"]'
        if self.options != []:
            st += ',\noptions=[ \n\"' + '\",\n\"'.join(self.options) + '\"]'
        if self.results != []:
            st += ',\nresults=[ \n\"' + '\",\n\"'.join(self.results) + '\"]'
        return st + ')'

    def subclass(self, abbr, name, arg, results=[], options=[]):
        """
        Add a list of axioms or another FO class to the current one.

        INPUT:
            abbr -- a short name (string) for the new FO subclass
            name -- a string naming the new FO subclass
            arg -- a list of axioms or an existing FOclass using same syntax
        """
        if type(arg) != list:
            arg = arg.axioms  # assume its another FOclass
        newaxioms = self.axioms + [a for a in arg if a not in self.axioms]
        return FOclass(abbr, name, newaxioms, results, options)

    def is_subclass(self, cls, seconds=60):
        """
        Return True if every axiom of cls is provable in self (in given time)
        """
        proofs = []
        for ax in cls.axioms:
            p = pr9(self.axioms, [ax], seconds, self.options)
            if type(p) == list:
                print ax, "proved"
            else:
                print ax, p
                return False, 'No conclusions'
            proofs.append(p)
        return True, proofs

    def is_not_subclass(self, cls, seconds=60):
        """
        Return True if some model of self is not a model of cls (in given time)
        """
        st = '(' + ') & ('.join(cls.axioms) + ')'
        m = prover9(self.axioms, [st], seconds, 1, options=self.options)
        if type(m) == list:
            return True, m[0]
        else:
            return False, m

    def tfae(self, lst):
        """
        Return True if all statements in lst are equivalent given self.axioms
        """
        s = lst + [lst[0]]
        for i in range(len(lst)):
            p = pr9(self.axioms + [s[i]], [s[i + 1]], seconds, self.options)
            if type(p) == list:
                print i, "->", i + 1, ":", s[i + 1], "proved"
            else:
                print i, "->", i + 1, ":", p
                return False, 'No conclusions'
            proofs.append(p)
        return True, proofs

    def find_models(self, cardinality, seconds=60):
        """
        Find models of given (finite) cardinality for the axioms 
        of the FOclass self.
        """
        if self.syntax == 'Prover9':
            return prover9(self.axioms, [], seconds, 0, cardinality, False, self.options)
        else:
            return "Don't know how to handle the syntax of " + self.syntax

    def count_models(self, upto=20, seconds=60000):
        """
        Find number of nonisomorphic models for the axioms of the FOclass self.
        """
        m = []
        for i in range(2, upto + 1):
            m.append(len(self.find_models(i)))
        return m

    def find_joint_extension(self, modelb, modelc, mace_time=10, prover_time=60):
        """
        Find models that extend the two given models in the FOclass self.
        """
        n = modelb.cardinality
        ne = ['b' + str(x) + '!=b' + str(y) for x in range(n) for y in range(x + 1, n)]
        n = modelc.cardinality
        ne += ['c' + str(x) + '!=c' + str(y) for x in range(n) for y in range(x + 1, n)]
        return prover9(self.axioms + ne + modelb.positive_diagram('b') +
                       modelc.positive_diagram('c'), [], mace_time, prover_time)

    def check_results(self, seconds=60, indices=None):
        if indices == None:
            indices = range(len(self.results))
        proofs = []
        for i in indices:
            p = pr9(self.axioms, [self.results[i]], seconds, self.options)
            if type(p) == list:
                print i + 1, ":", self.results[i], "proved"
            else:
                print i + 1, ":", self.results[i], p
            proofs.append(p)
        return proofs

    def check_irredundance(self, seconds=60, indices=None):
        ax = self.axioms
        ml = []
        if indices == None:
            indices = range(len(ax))
        for i in indices:
            m = prover9(ax[:i] + ax[i + 1:], [ax[i]], seconds, 0, options=self.options)
            if type(m) == str:
                print ax[i], "is redundant"
                return False
            else:
                ml.append(m)
        return True, ml


def assoc(s): return '(x' + s + 'y)' + s + 'z = x' + s + '(y' + s + 'z)'


def comm(s): return 'x' + s + 'y = y' + s + 'x'


def idem(s): return 'x' + s + 'x = x'


def absorption(s, t): return '(x' + s + 'y)' + t + 'x = x'


def distr(s, t): return 'x' + s + '(y' + t + 'z) = (x' + s + 'y)' + t + '(x' + s + 'z)'


def rdistr(s, t): return '(x' + t + 'y)' + s + 'z = (x' + s + 'z)' + t + '(y' + s + 'z)'

#########################
# (Semi) groups and rings

Sgrp = FOclass("Sgrp", "Semigroups", [assoc("*")])

CSgrp = FOclass("CSgrp", "Commutative semigroups", [assoc("+"), comm("+")])

UnSgrp = Sgrp.subclass("UnSgrp", "Semigroups with order-2 unary operation",
                       ["x'' = x"])

InSgrp = UnSgrp.subclass("InSgrp", "Involutive semigroups", ["(x*y)' = y'*x'"])

ISgrp = UnSgrp.subclass("ISgrp", "I-Semigroups", ["(x*x')*x = x"])

CompRSgrp = ISgrp.subclass("CompRSgrp", "Completely regular semigroups",
                           ["x'*x = x*x'"])

InvSgrp = ISgrp.subclass("InvSgrp", "Inverse semigroups",
                         ["(x*x')*(y*y') = (y*y')*(x*x')"])

CliffSgrp = InvSgrp.subclass("CliffSgrp", "Clifford semigroups",
                             ["x'*x = x*x'"])

Mon = FOclass("Mon", "Monoids", [assoc("*"), "x*1 = x", "1*x = x"])

CMon = CSgrp.subclass("CMon", "Commutative monoids", ["x+0 = x"])

InMon = Mon.subclass("InMon", "Involutive monoids",
                     ["(x*y)' = y'*x'", "x'' = x"])

Grp = FOclass("Grp", "Groups", [assoc("*"), "x*1 = x", "x*x' = 1"],
              results=["1*x = x", "x'*x = 1", "x'' = x", "(x*y)' = y'*x'"])

AbGrp = CMon.subclass("AbGrp", "Abelian groups", ["x + -x = 0"])

Ring = AbGrp.subclass("Ring", "Rings",
                      [assoc("*"), distr("*", "+"), rdistr("*", "+")],
                      results=["0*x = 0", "x*0 = 0"])

VNRRing = Ring.subclass("VNRRing", "Von Neumann regular rings",
                        ["exists y (x*y)*x = x"])

URing = AbGrp.subclass("URing", "Unital rings", Mon.axioms +
                       [distr("*", "+"), rdistr("*", "+")])

CRing = Ring.subclass("CRing", "Commutative rings", [comm("*")])

CURing = URing.subclass("CURing", "Commutative unital rings", [comm("*")])

BRing = URing.subclass("BRing", "Boolean rings",
                       ["x*x = x"], results=["x*y = y*x"])


###########################
# (Semi) lattice subclasses

Slat = FOclass("Slat", "Semilattices", [assoc("*"), comm("*"), "x*x = x"])

Lat = FOclass("Lat", "Lattices",
              [assoc(" v "), comm(" v "), assoc("^"), comm("^"),
               absorption(" v ", "^"), absorption("^", " v ")],
              results=["x v x = x", "x^x = x"])

DLat = Lat.subclass("DLat", "Distributive lattices", [distr("^", " v ")],
                    results=[distr(" v ", "^"),
                             "((x v y)^(x v z))^(y v z) = ((x^y)v(x^z))v(y^z)"])

MLat = Lat.subclass("MLat", "Modular lattices", ["x^(y v (x^z)) = (x^y) v (x^z)"])

SDjLat = Lat.subclass("SDjLat", "Join-semidistributive lattices",
                      ["x v y = x v z -> x v y = x v(y^z)"])

SDmLat = Lat.subclass("SDmLat", "Meet-semidistributive lattices",
                      ["x ^ y = x ^ z -> x ^ y = x^(y v z)"])

SDLat = SDjLat.subclass("SDLat", "Semidistributive lattices", SDmLat)


####################
# Lattice expansions

BLat = Lat.subclass("BLat", "Bounded lattices", ["0 v x = x", "1 v x = 1"])

BDLat = BLat.subclass("BDLat", "Bounded distributive lattices",
                      [distr("^", " v ")])

BA = DLat.subclass("BA", "Boolean algebras", ["x v x' = 1", "x ^ x' = 0"],
                   ["x'' = x", "(x v y)' = x' ^ y'", "(x ^ y)' = x' v y'",
                       "0' = 1"])

DmLat = BLat.subclass("DmLat", "De Morgan lattices",
                      ["x''=x", "(x v y)' = x' ^ y'"])

DmA = BDLat.subclass("DmA", "De Morgan algebras",
                     ["x''=x", "(x v y)' = x' ^ y'"])

OLat = DmLat.subclass("OLat", "Ortholattices", ["x v x' = 1"],
                      results=["x^x' = 0", "0' = 1"])

pLat = BLat.subclass("pLat", "pseudocomplemented lattices", ["-0 = 1",
                                                             "-1 = 0", "x^-(x^y) = x^-y"])

pOLat = OLat.subclass("pOLat", "p-ortholattices", pLat)

StpLat = pLat.subclass("StpLat", "Stonian p-lattices", ["-(x^y) = -x v -y"])

StpOLat = OLat.subclass("StpOLat", "Stonian p-ortholattices", ["-0 = 1",
                                                               "x^-(x^y) = x^-y", "-(x^y) = -x v -y"])

ModalLat = BLat.subclass("ModalLat", "Modal lattices",
                         ["f(x v y) = f(x) v f(y)", "f(0) = 0"])

ModalA = BA.subclass("ModalA", "Modal algebras",
                     ["f(x v y) = f(x) v f(y)", "f(0) = 0"])

CloA = ModalA.subclass("CloA", "Closure algebras",
                       ["f(x) ^ x = x", "f(f(x)) = f(x)"])

MonA = CloA.subclass("MonA", "Monadic algebras", ["f(x') = f(x)'"])

RA = BA.subclass("RA", "Relation algebras",
                 ["(x*y)*z=x*(y*z)", "x*e = x", "(x v y)*z = (x*z) v (y*z)", "c(c(x))=x",
                     "c(x v y)=c(x) v c(y)", "c(x*y)=c(y)*c(x)", "(c(x)*((x*y)'))v y'=y'"])

qRA = BLat.subclass("qRA", "Relation algebras",
                    ["(x*y)*z=x*(y*z)", "x*e = x", "(x v y)*z = (x*z) v (y*z)", "c(c(x))=x",
                     "c(x v y)=c(x) v c(y)", "c(x*y)=c(y)*c(x)", "(c(x)*((x*y)'))v y'=y'"])


##########################
# Lattice-ordered algebras

LGrpoid = Lat.subclass("LGrpoid", "Lattice-ordered groupoids",
                       [distr("*", " v "), rdistr("*", " v ")])

ULGrpoid = LGrpoid.subclass("ULGrpoid", "Unital l-groupoids",
                            ["x*1 = x", "1*x = x"])

ILGrpoid = ULGrpoid.subclass("ILGrpoid", "Integral l-groupoids", ["x v 1 = 1"])

BILGrpoid = ILGrpoid.subclass("BILGrpoid", "Bounded integral l-groupoids",
                              ["x v 0 = x", "x*0 = 0", "0*x = 0"])

LMon = ULGrpoid.subclass("LMon", "Lattice-ordered monoids", [assoc("*")])

BLMon = LMon.subclass("BLMon", "Bounded l-monoids",
                      ["x v 0 = x", "x*0 = 0", "0*x = 0"])

ILMon = LMon.subclass("LMon", "Integral l-monoids", ["x v 1 = 1"])

BILMon = ILMon.subclass("ILMon", "Bounded integral l-monoids",
                        ["x v 0 = x", "x*0 = 0", "0*x = 0"])

LGrp = LGrpoid.subclass("LGrp", "Lattice-ordered groups", Grp,
                        results=[distr("^", " v ")])

LGrp1 = Grp.subclass("LGrp1", "Lattice-ordered groups",
                     [assoc(" v "), comm(" v "), idem(" v "),
                      distr("*", " v "), rdistr("*", " v "), "x^y = (x' v y')'"],
                     results=[assoc("^"), comm("^"), idem("^"),
                              "x v (x^y) = x", "x^(x v y) = x",
                              rdistr("^", " v ")])

RL = LMon.subclass("RL", "Residuated lattices",
                   ["x = x^(((x*y) v z)/y)", "x = x^(y\\((y*x) v z))",
                       "((x/y)*y) v x = x", "(y*(y\\x)) v x = x"])

CRL = LMon.subclass("CRL", "Commutative residuated lattices", [comm("*"),
                                                               "x = x^(y->((y*x) v z))", "(y*(y->x)) v x = x"])

DRL = RL.subclass("DRL", "Distributive residuated lattices",
                  [distr("^", " v ")])

CDRL = CRL.subclass("CDRL", "Commutative distributive residuated lattices",
                    [distr("^", " v ")])

RCRL = CRL.subclass("RCRL", "Representable commmutative residuated lattices",
                    ["(x/y v y/x)^1 = 1"])

IRL = RL.subclass("IRL", "Integral residuated lattices", ["x v 1 = 1"])

CIRL = CRL.subclass("CIRL", "Commutative integral residuated lattices",
                    ["x v 1 = 1"])

DIRL = DRL.subclass("DIRL", "Distributive integral residuated lattices",
                    ["x v 1 = 1"])

CDIRL = CDRL.subclass("CDIRL", "Commutative distributive integral residuated lattices",
                      ["x v 1 = 1"])

FL_o = RL.subclass("FL_o", "Full Lambek algebras with bottom", ["x v 0 = x"])

FL_eo = CRL.subclass("FL_eo", "Full Lambek algebras with bottom", ["x v 0 = x"])

FL_w = FL_o.subclass("FL_w", "Full Lambek algebras with weakening",
                     ["x v 1 = 1"])

FL_ew = FL_eo.subclass("FL_ew", "FL-algebras with exchange and weakening",
                       ["x v 1 = 1"])

GBL = RL.subclass("GBL", "Generalized BL-algebras", ["x ^ y = y*(y\\(x ^ y))",
                                                     "x ^ y = ((x ^ y)/y)*y"])

GMV = RL.subclass("GMV", "Generalized MV-algebras", ["x v y = x/((x v y)\\x)",
                                                     "x v y = (x/(x v y))\\x"])

InFL = LMon.subclass("InFL", "Involutive FL-algebras", ["(x*~(-z*x))v z = z",
                                                        "(-(y*~z)*y) v z = z", "y = y^(~(-(x*y)*x))",
                                                        "x = x^(-(y*~(x*y)))", "~-x = x", "-~x = x",
                                                        "0 = ~1", "0 = -1", "~(x^y) = ~x v ~y", "-(x^y) = -x v -y"],
                     options=['op(350, prefix, "~")'],
                     results=["(x*y) v z = z -> y^-(~z*x) = y"])

DInFL = InFL.subclass("DInFL", "Distributive involutive FL-algebras", [distr("^", " v ")])

CyInFL = LMon.subclass("CyInFL", "Cyclic involutive FL-algebras", ["~~x = x", "0 = ~1",
                                                                   "~(x^y)=~x v ~y", "(x*~(~z*x))v z = z", "(~(y*~z)*y) v z = z",
                                                                   "y = y^(~(~(x*y)*x))", "x = x^(~(y*~(x*y)))"],
                       options=['op(350, prefix, "~")'],
                       results=["(x*y) v z = z -> y^~(~z*x) = y"])

MTL = FL_ew.subclass("MTL", "Monoidal t-norm logic algebras", ["(x->y)v(y->x) = 1"])

HA = BDLat.subclass("HA", "Heyting algebras", ["(x->x) = 1", "(x->y)^y = y",
                                               "x^(x->y) = x^y", "(x->(y^z)) = (x->y)^(x->z)",
                                               "((x v y)->z) = (x->z)^(y->z)"],
                    results=["x = x^(y->((y^x) v z))", "(y^(y->x)) v x = x"])

GodelA = HA.subclass("GodelA", "Goedel algebras", ["x/y v y/x = 1"])

MValg = CMon.subclass("MValg", "MV-algebras", ["~~x = x", "x+~0 = ~0",
                                               "~(~x+y)+y = ~(~y+x)+x"],
                      results=["~(~x+x)+x = x"])

BLalg = MTL.subclass("BLalg", "Basic logic algebras", ["x^y = x*(x->y)"])

# defined above OLat = BLat.subclass("", "Ortholattices", ["x v x' = 1", "x^x'=0"])

# OMLat =

# MOLat


#########################################
# Sequent calculi (quasi-equational form)

RLseq = FOclass("RLseq", "Residuated lattice sequent calculus", ["(x*y)*z = x*(y*z)",
                                                                 "x*1 = x", "1*x = x", "x <= x",
                                                                 "x <= y  &  y <= x  ->  x = y",
                                                                 "u <= x  ->  u <= x v y",
                                                                 "u <= y  ->  u <= x v y",
                                                                 "(u*x)*v <= z & (u*y)*v <= z  ->  (u*(x v y))*v <= z",
                                                                 "x <= z & y <= z  ->  x v y <= z",
                                                                 "u <= x & v <= y  ->  u*v <= x*y",
                                                                 "u <= x & u <= y  ->  u <= x^y",
                                                                 "(u*x)*v <= z  ->  (u*(x^y))*v <= z",
                                                                 "(u*y)*v <= z  ->  (u*(x^y))*v <= z",
                                                                 "u*y <= x  ->  u <= x/y",
                                                                 "v <= y  &  (u*x)*w <= z  ->  (u*(x/y))*(v*w) <= z",
                                                                 "y*u <= x  ->  u <= y\\x",
                                                                 "v <= y  &  (u*x)*w <= z  ->  (u*v)*((y\\x)*w) <= z"],
                results=["x v x <= x", "x <= x v x",
                         "x*(y v z) <= (x*y)v(x*z)", "(x*y)v(x*z) <= x*(y v z)"])

FL_oseq = FOclass("FL_oseq", "FL-algebras with bottom sequent calculus", ["(x*0)*y = z"])


###################################
# Semigroup and semiring expansions

DSgrp = Sgrp.subclass("DSgrp", "Domain semigroups", ["d(x)*x = x", "d(x*y) = d(x*d(y))",
                                                     "d(d(x)*y) = d(x)*d(y)", "d(x)*d(y) = d(y)*d(x)"],
                      results=["d(d(x)) = d(x)", "d(x)*d(x) = d(x)"])

RSgrp = Sgrp.subclass("RSgrp", "Range semigroups", ["x*r(x) = x", "r(x*y) = r(r(x)*y)",
                                                    "r(x*r(y)) = r(x)*r(y)", "r(x)*r(y) = r(y)*r(x)"],
                      results=["r(r(x)) = r(x)", "r(x)*r(x) = r(x)"])

DRSgrp = DSgrp.subclass("DRSgrp", "Domain-range semigroups",
                        ["x*r(x) = x", "r(x*y) = r(r(x)*y)",
                         "r(x*r(y)) = r(x)*r(y)", "r(x)*r(y) = r(y)*r(x)",
                         "d(r(x)) = r(x)", "r(d(x)) = d(x)"],
                        results=["r(r(x)) = r(x)", "r(x)*r(x) = r(x)"])

AFSys = Sgrp.subclass("AFSys", "Abstract function systems",
                      ["d(x)*x = x", "x*r(x) = x",
                       "d(x*y) = d(x*d(y))", "r(x*y) = r(r(x)*y)",
                       "d(x)*r(y) = r(y)*d(x)", "x*d(y) = d(x*y)*x",
                       "d(r(x)) = r(x)", "r(d(x)) = d(x)"],
                      results=["r(x*r(y)) = r(x)*r(y)",
                               "r(x)*r(y) = r(y)*r(x)",
                               "r(r(x)) = r(x)", "r(x)*r(x) = r(x)"])

RCSgrp = Sgrp.subclass("RCSgrp", "Right closure semigroups", ["d(x)*x = x",
                                                              "d(x)*d(y) = d(y)*d(x)",
                                                              "d(d(x)) = d(x)", "d(x)*d(x*y) = d(x*y)"],
                       results=["d(x)*d(x) = d(x)", "d(d(x)*y) = d(x)*d(y)"])

tRCSgrp = RCSgrp.subclass("tRCSgrp", "Twisted RC-semigroups", ["x*d(y) = d(x*d(y))*x",
                                                               "d(x*y) = d(x*d(y))"],
                          results=["d(d(x)*y) = d(x)*d(y)"])

DMon = DSgrp.subclass("DMon", "Domain monoids", ["x*1 = x", "1*x = x"],
                      results=["d(1) = 1"])

RMon = RSgrp.subclass("RMon", "Range monoids", ["x*1 = x", "1*x = x"],
                      results=["r(1) = 1"])

BDMon = Mon.subclass("BDMon", "Boolean domain monoids", ["x*0=0", "x'*x=0",
                                                         "x'*y'=y'*x'", "x''*x=x", "x'=(x*y)'*(x*y')'"],
                     results=["0' = 1"])

BDRMon = Mon.subclass("BDRMon", "Boolean domain-range monoids", ["x*0=0", "x'*x=0",
                                                                 "x'*y'=y'*x'", "x''*x=x", "x'=(x*y)'*(x*y')'",
                                                                 "x*(-x)=0", "-x*(-y)=-y*(-x)", "x*(- -x)=x",
                                                                 "-y=-(-x*y)*-(x*y)", "(-x)''=-x", "- -(x')=x'"],
                      #                      options=['op(350, prefix, "~")'],
                      results=["0' = 1", "0*x=0"])

DRMon = DRSgrp.subclass("DRMon", "Domain-range monoids", ["x*1 = x", "1*x = x"],
                        results=["r(1) = 1"])

Sring = Mon.subclass("Sring", "Semirings", [assoc("+"), comm("+"), "x+0 = x",
                                            distr("*", "+"), rdistr("*", "+"), "x*0 = 0", "0*x = 0"])

IdSring = Sring.subclass("IdSring", "Idempotent semirings", [idem("+")])

DSring = IdSring.subclass("DSring", "Domain semirings", ["d(x)*x = x",
                                                         "d(x*y) = d(x*d(y))", "d(x+y) = d(x)+d(y)",
                                                         "d(x)+1 = 1", "d(0) = 0"])

BDSring = IdSring.subclass("BDSring", "Boolean domain semiring", ["a(x)*x = 0",
                                                                  "a(x*y) = a(x*a(a(y)))", "a(x)+a(a(x)) = 1"])

ExpSring = Sring.subclass("ExpSring", "Exponential semirings", ["1^x = 1",
                                                                "(x*y)^z = (x^z)*(y^z)", "x^0 = 1", "x^1 = x",
                                                                "x^(y+z) = (x^y)*(x^z)", "x^(y*z) = (x^y)^z"])

KA = CMon.subclass("KA", "Kleene algebras", ["x+x = x", assoc(";"),
                                             "x;1 = x", "1;x = x", "x;(y + z) = x;y + x;z",
                                             "(x + y);z = x;z + y;z", "x;0 = 0", "0;x = 0",
                                             "1 + x;x* = x*", "1 + x*;x = x*",
                                             "y;x + x = x  ->  y*;x + x = x",
                                             "x;y + x = x  ->  x;y* + x = x"],
                   results=["x*;x* = x*"],
                   options=["op(300, postfix, *)", "op(400, infix_left, ;)"])

KAseq = FOclass("KAseq", "Kleene algebra sequent calculus", ["(x;y);z = x;(y;z)",
                                                             "x;1 = x", "1;x = x", "x <= x", "x;0;y <= z",
                                                             "u <= x  ->  u <= x+y",
                                                             "u <= y  ->  u <= x+y",
                                                             "u;x;v <= z & u;y;v <= z  ->  u;(x+y);v <= z",
                                                             "u <= x & v <= y  ->  u;v <= x;y",
                                                             "u <= 1  ->  u <= x*",
                                                             "u <= x  ->  u <= x*",
                                                             "u <= x* & v <= x*  ->  u;v <= x*",
                                                             "u <= y & x;y <= y  ->  x*;u <= y",
                                                             "u <= y & y;x <= y  ->  u;x* <= y"],
                results=["x <= x*", "x*;x* <= x*", "x <= x*;x*", "x** <= x*",
                         "x* <= x**", "x*;(y;x*)* <= (x+y)*",
                         "(x+y)* <= x* ;(y;x*)*"],
                options=["op(300, postfix, *)", "op(400, infix_left, ;)"])

Alleg = InMon.subclass("Alleg", "Unisorted allegories", [assoc("^"), comm("^"),
                                                         idem("^"), "(x^y)'=x'^y'", "(x*(y^z)) ^ (x*y) = x*(y^z)",
                                                         "(x*y)^z = ((x^(z*y'))*y)^z"])

##########################
# Other equational classes

Qdl = FOclass("Qdl", "Quandels",
              [idem("*"), "(x*y)/y = x", "(x/y)*y = x", rdistr("*", "*")])

Band = FOclass("Band", "Bands", [assoc("*"), idem("*")])

RectBand = Band.subclass("RectBand", "Rectangular bands", ["(x*y)*z = x*z"])

Qgrp = FOclass("Qgrp", "Quasigroups",
               ["(x*y)/y = x", "(x/y)*y = x", "x\\(x*y) = y", "x*(x\\y) = y"])

Loop = Qgrp.subclass("Loop", "Loops", ["x*1 = x", "1*x = x"])

STS = Qgrp.subclass("STS", "Steiner triple systems", [idem("*"), comm("*")])


#####################
# First-order classes

def refl(r): return "x" + r + "x"


def irrefl(r): return "-(x" + r + "x)"


def symm(r): return "x" + r + "y -> y" + r + "x"


def asymm(r): return "x" + r + "y -> -(y" + r + "x)"


def antisymm(r): return "x" + r + "y & y" + r + "x -> x = y"


def trans(r): return "x" + r + "y & y" + r + "z -> x" + r + "z"


def linear(r): return "x" + r + "y || y" + r + "x"

PreOrd = FOclass("PreOrd", "Preordered sets", [refl("<="), trans("<=")])

Pos = PreOrd.subclass("Pos", "Partially ordered sets", [antisymm("<=")])

StrPos = FOclass("StrPos", "Strict partially ordered sets", [irrefl("<"), trans("<")])

Chains = Pos.subclass("Chains", "Linearly ordered sets", ["x<=y | y<=x"])

####################
# Ordered structures

poGrpoid = Pos.subclass("poGrpoid", "Partially ordered groupoids",
                        ["x<=y -> x*z<=y*z", "x<=y -> z*x<=z*y"])

poCGrpoid = Pos.subclass("poCGrpoid", "Partially ordered commutative groupoids",
                         [comm("*"), "x<=y -> x*z<=y*z"])

oGrpoid = Chains.subclass("oGrpoid", "Linearly ordered groupoids",
                          ["x<=y -> x*z<=y*z", "x<=y -> z*x<=z*y"])

oCGrpoid = oGrpoid.subclass("oCGrpoid", "Linearly ordered commutative groupoids", [comm("*")])

poSgrp = poGrpoid.subclass("poSgrp", "po-semigroups", Sgrp)

poCSgrp = poSgrp.subclass("poCSgrp", "Partially ordered commutative semigroups", [comm("*")])

oSgrp = oGrpoid.subclass("oSgrp", "Linearly ordered semigroups", Sgrp)

oCSgrp = oSgrp.subclass("oCSgrp", "Linearly ordered commutative semigroups", [comm("*")])

poMon = poGrpoid.subclass("poMon", "po-monoids", Mon)

poCMon = poMon.subclass("poCMon", "Partially ordered commutative monoids", [comm("*")])

oMon = oGrpoid.subclass("oMon", "Linearly ordered monoids", Mon)

oCMon = oMon.subclass("oCMon", "Linearly ordered commutative monoids", [comm("*")])

proGrp = poMon.subclass("proGrp", "Protogroups", ["f(x)*x <= 1", "1 <= x*f(x)"],
                        results=["f(x*y) = f(y)*f(x)", "(x*f(x))*x = x"])

prGrp = poMon.subclass("prGrp", "Pregroups", ["f(x)*x <= 1", "1 <= x*f(x)",
                                              "x*g(x) <= 1", "1 <= g(x)*x"],
                       results=["f(g(x)) = x", "g(f(x)) = x",
                                "f(x*y) = f(y)*f(x)", "g(x*y) = g(y)*g(x)",
                                "(x*f(x))*x = x", "(x*g(x))*x = x"])

LprGrp = LMon.subclass("LprGrp", "Lattice-ordered pregroups",
                       ["(f(x)*x) v 1 = 1",
                        "1 = 1 ^ (x*f(x))", "(x*g(x)) v 1 = 1", "1 = 1 ^ (g(x)*x)"],
                       results=["f(g(x)) = x", "g(f(x)) = x",
                                "f(x*y) = f(y)*f(x)", "g(x*y) = g(y)*g(x)",
                                "(x*f(x))*x = x", "(x*g(x))*x = x"])

###############################
# Residuated ordered structures

rpoGrpoid = poGrpoid.subclass("rpoGrpoid", "Residuated partially ordered groupoids",
                              ["x<=y -> x/z<=y/z", "x<=y -> z\\x<=z\\y",
                               "x*(x\\y)<=y", "y<=x\\(x*y)",
                               "(y/x)*x<=y", "y<=(y*x)/x"],
                              results=["x*(x\\x) = x"])

rpoCGrpoid = poCGrpoid.subclass("rpoCGrpoid", "Residuated partially ordered commutative groupoids",
                                ["x<=y -> (z->x)<=(z->y)",
                                 "x*(x->y)<=y", "y<=(x->(x*y))"],
                                results=["x*(x->x) = x"])

roGrpoid = oGrpoid.subclass("roGrpoid", "Residuated linearly ordered groupoids",
                            ["x<=y -> x/z<=y/z", "x<=y -> z\\x<=z\\y",
                             "x*(x\\y)<=y", "y<=x\\(x*y)",
                             "(y/x)*x<=y", "y<=(y*x)/x"])

roCGrpoid = roGrpoid.subclass("roCGrpoid", "Residuated linearly ordered commutative groupoids",
                              [comm("*")])

rpoSgrp = rpoGrpoid.subclass("rpoSgrp", "Residuated po-semigroups", Sgrp)

rpoCSgrp = rpoSgrp.subclass("rpoCSgrp", "Residuated partially ordered commutative semigroups",
                            [comm("*")])

roSgrp = roGrpoid.subclass("roSgrp", "Residuated linearly ordered semigroups", Sgrp)

roCSgrp = roSgrp.subclass("roCSgrp", "Residuated linearly ordered commutative semigroups",
                          [comm("*")])

rpoMon = rpoGrpoid.subclass("rpoMon", "Residuated po-monoids", Mon)

rpoCMon = poCMon.subclass("rpoCMon", "Residuated partially ordered commutative monoids",
                          ["x<=y -> (z->x)<=(z->y)",
                           "x*(x->y)<=y", "y<=(x->(x*y))"])

roMon = roGrpoid.subclass("roMon", "Residuated linearly ordered monoids", Mon)

roCMon = rpoCMon.subclass("roCMon", "Residuated linearly ordered commutative monoids",
                          ["x<=y | y<=x"])

# Integral
irpoGrpoid = rpoGrpoid.subclass("irpoGrpoid", "Integral residuated partially ordered groupoids",
                                ["y<=x\\x", "x\\x = y/y"])

irpoCGrpoid = rpoCGrpoid.subclass("irpoCGrpoid", "Integral residuated partially ordered commutative groupoids",
                                  ["y<=x\\x", "x\\x = y/y"])

iroGrpoid = roGrpoid.subclass("iroGrpoid", "Integral residuated linearly ordered groupoids",
                              ["y<=x\\x", "x\\x = y/y"])

iroCGrpoid = roCGrpoid.subclass("iroCGrpoid", "Integral residuated linearly ordered commutative groupoids",
                                ["y<=x\\x", "x\\x = y/y"])

irpoSgrp = irpoGrpoid.subclass("irpoSgrp", "Integral residuated po-semigroups", Sgrp)

irpoCSgrp = rpoCSgrp.subclass("irpoCSgrp", "Integral residuated partially ordered commutative semigroups",
                              ["y<=x\\x", "x\\x = y/y"])

iroSgrp = iroGrpoid.subclass("iroSgrp", "Integral residuated linearly ordered semigroups",
                             Sgrp)

iroCSgrp = roCSgrp.subclass("iroCSgrp", "Integral residuated linearly ordered commutative semigroups",
                            ["y<=x\\x", "x\\x = y/y"])

irpoMon = rpoMon.subclass("irpoMon", "Integral residuated po-monoids",
                          ["x<=1"])
porim = irpoMon

irpoCMon = rpoCMon.subclass("irpoCMon", "Integral residuated partially ordered commutative monoids",
                            ["x<=1"])
pocrim = irpoCMon

iroMon = roMon.subclass("iroMon", "Integral residuated linearly ordered monoids",
                        ["x<=1"])

iroCMon = roCMon.subclass("iroCMon", "Integral residuated linearly ordered commutative monoids",
                          ["x<=1"])


#################
# Atom structures

NAat = FOclass("NAat", "Nonassociative relation algebra atomstructures",
               ["C(x,y,z) -> C(x',z,y)", "C(x,y,z) -> C(z,y',x)",
                "x=y <-> exists u(E(u) & C(x,u,y))"])

INAat = FOclass("INAat", "Integral nonassociative relation algebra atomstructures",
                ["C(x,y,z) -> C(x',z,y)", "C(x,y,z) -> C(z,y',x)",
                 "C(x,0,y) <-> x=y"],
                results=["C(x',z,y) -> C(x,y,z)", "C(z,y',x) -> C(x,y,z)",
                         "x''=x", "C(0,x,y) <-> x=y"])

INAat1 = FOclass("INAat1", "Integral nonassociative relation algebra atomstructures",
                 ["C(x,y,z) -> C(x',z,y)", "C(x,y,z) -> C(z,y',x)",
                  "C(x,1,y) <-> x=y"],
                 results=["C(x',z,y) -> C(x,y,z)", "C(z,y',x) -> C(x,y,z)",
                          "x''=x", "C(1,x,y) <-> x=y"])

SNAat = FOclass("SNAat", "Symmetric nonassociative relation algebra atomstructures",
                ["C(x,y,z) -> C(x,z,y)", "C(x,y,z) -> C(z,y,x)",
                 "C(x,0,y) <-> x=y"])

RAat = NAat.subclass("RAat", "Relation algebra atomstructures",
                     ["exists u(C(x,y,u) & C(u,z,w)) <-> exists v(C(x,v,w) & C(y,z,v))"])

IRAat = INAat.subclass("IRAat", "Integral relation algebra atomstructures",
                       ["exists u(C(x,y,u) & C(u,z,w)) <-> exists v(C(x,v,w) & C(y,z,v))"])

IRAat1 = INAat1.subclass("IRAat1", "Integral relation algebra atomstructures",
                         ["exists u(C(x,y,u) & C(u,z,w)) <-> exists v(C(x,v,w) & C(y,z,v))"])

SRAat = SNAat.subclass("SRAat", "Symmetric relation algebra atomstructures",
                       ["exists u(C(x,y,u) & C(u,z,w)) <-> exists v(C(x,v,w) & C(y,z,v))"])

SeqAat = FOclass("SeqAat", "Sequential algebra atomstructures",
                 ["C(x,y,0) <-> C(y,x,0)", "C(x,0,y) <-> x=y", "C(0,x,y) <-> x=y",
                  "exists u(C(x,y,u) & C(u,z,w)) <-> exists v(C(x,v,w) & C(y,z,v))",
                  "exists u(C(x,u,y) & C(u,w,z)) -> exists v(C(x,z,v) & C(y,w,v))"])


#############################################################
# Propositional Logics

MP = "P(x) & P(x->y) -> P(y)"           # Modus pones
Bb = "P((x->y)->((z->x)->(z->y)))"      # Prefixing
Bp = "P((x->y)->((y->z)->(x->z)))"      # Suffixing
Cc = "P((x->(y->z))->(y->(x->z)))"      # Commutativity
Ii = "P(x->x)"                          # Identity
Kk = "P(x->(y->x))"                     # Integrality
Ss = "P((x->(y->z))->((x->y)->(x->z)))"  # Selfdistributivity
Ww = "P((x->(x->y))->(x->y))"           # Contraction
Pierce = "P(((x->y)->x)->x)"             # Pierce's law
DN = "P(--x->x)"                        # Double negation
CP = "P((x->-y)->(y->-x))"              # Contraposition

BK = FOclass("BK", "BK logic,  reduct of FL_w", [Bb, Kk, MP,
                                                 "P(y) & P(x->(y->z)) -> P(x->z)"])

BCK = FOclass("BCK", "BCK logic, -> reduct of FL_ew", [Bb, Cc, Kk, MP])

BCKP = FOclass("BCKP", "BCK logic + Pierce law, -> reduct of CL", [Bb, Cc, Kk, Pierce, MP])

BCI = FOclass("BCI", "BCI logic, -> reduct of FL_e", [Bb, Cc, Ii, MP])

BCIS = FOclass("BCIS", "BCIS=BCIW logic, -> reduct of FL_ec", [Bb, Cc, Ii, Ss, MP])

SK = FOclass("SK", "Hilbert logic, -> reduct of intuitionistic logic", [Ss, Kk, MP])

CL = FOclass("CL", "Classical logic", [Ss, Kk, DN, CP, MP])


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

################################################################
# Minion interface code Peter Jipsen 2011-03-26 alpha version
# requires sage.chapman.edu/sage/minion_20110326.spkg


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
    writefile('tmp.minion', st)
    os.system('minion -noprintsols -findallsols -solsout tmp.txt tmp.minion >tmpout.txt')
    st = readfile('tmp.txt')
    os.system('rm tmp.txt')
    return [[int(y) for y in x.strip().split(" ")] for x in st.split("\n")[:-1]]


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
    writefile('tmp.minion', st)
    os.system('minion -noprintsols -findallsols -solsout tmp.txt tmp.minion >tmpout.txt')
    st = readfile('tmp.txt')
    os.system('rm tmp.txt')
    return [[int(y) for y in x.strip().split(" ")] for x in st.split("\n")[:-1]]


def Aut(A):
    """
    call Minion to calculate all automorphisms of algebra A
    """
    return Embeddings(A, A)


def is_hom_image(A, B):
    """return true if B is a homomorphic image of A (uses Minion)"""
    st = minion_hom_algebras(A, B, surj=True)
    writefile('tmp.minion', st)
    os.system('minion -noprintsols -solsout tmp.txt tmp.minion >tmpout.txt')
    st = readfile('tmp.txt')
    os.system('rm tmp.txt')
    return len(st.split("\n")[:-1]) > 0

Model.is_hom_image = is_hom_image


def is_subalgebra(A, B):
    """
    return true if A is a subalgebra of B (uses Minion)
    """
    st = minion_hom_algebras(A, B, inj=True)
    writefile('tmp.minion', st)
    os.system('minion -noprintsols -solsout tmp.txt tmp.minion >tmpout.txt')
    st = readfile('tmp.txt')
    os.system('rm tmp.txt')
    return len(st.split("\n")[:-1]) > 0

Model.is_subalgebra = is_subalgebra


def is_isomorphic(A, B):
    """
    return true if A is isomorphic to B (uses Minion)
    """
    return A.cardinality == B.cardinality and is_subalgebra(A, B)

Model.is_isomorphic = is_isomorphic


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
    writefile('tmp.minion', st)
    os.system('minion -noprintsols -findallsols -solsout tmp.txt tmp.minion >tmpout.txt')
    st = readfile('tmp.txt')
    os.system('rm tmp.txt')
    return [tuple(int(y) for y in x.strip().split(" ")) for x in st.split("\n")[:-1]]


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

Model.is_congruence_closed = is_congruence_closed


def congruence_closure(parts):
    return Con(ops2alg(Pol_1(parts2relst(parts))))


def monoid_closure(ops):
    return Pol_1(parts2relst(Con(ops2alg(ops))))
