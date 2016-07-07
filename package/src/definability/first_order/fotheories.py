#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
>>> len(DLat.find_models(5))
3
"""
from ..first_order.fotheory import FO_Theory

#########################
# Properties of operations


def assoc(s):
    return '(x' + s + 'y)' + s + 'z = x' + s + '(y' + s + 'z)'


def comm(s):
    return 'x' + s + 'y = y' + s + 'x'


def idem(s):
    return 'x' + s + 'x = x'


def absorption(s, t):
    return '(x' + s + 'y)' + t + 'x = x'


def distr(s, t):
    return 'x' + s + '(y' + t + 'z) = (x' + s + 'y)' + t + '(x' + s + 'z)'


def rdistr(s, t):
    return '(x' + t + 'y)' + s + 'z = (x' + s + 'z)' + t + '(y' + s + 'z)'

#########################
# Properties of relations


def refl(r):
    return "x " + r + " x"


def irrefl(r):
    return "-(x " + r + " x)"


def symm(r):
    return "x " + r + " y -> y " + r + " x"


def asymm(r):
    return "x " + r + " y -> -(y " + r + " x)"


def antisymm(r):
    return "x " + r + " y & y " + r + " x -> x = y"


def trans(r):
    return "x " + r + " y & y " + r + " z -> x " + r + " z"


def linear(r):
    return "(x " + r + " y) | (y " + r + " x)"
#########################
# Graphs

DiGraph = FO_Theory("DiGraph", "Directed Graphs", ["exists x exists y (x e y)"], options=["op(400, infix, e)"])

Graph = DiGraph.subclass("Graph", "Undirected Graphs", [symm("e")])

AsymmGraph = DiGraph.subclass("AsymmGraph", "Asymmetric Graphs", [asymm("e")])

LinearGraph = DiGraph.subclass("LGraph", "Linear Graphs", [linear("e")])

#########################
# (Semi) groups and rings

Sgrp = FO_Theory("Sgrp", "Semigroups", [assoc("*")])

CSgrp = FO_Theory("CSgrp", "Commutative semigroups", [assoc("+"), comm("+")])

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

Mon = FO_Theory("Mon", "Monoids", [assoc("*"), "x*1 = x", "1*x = x"])

CMon = CSgrp.subclass("CMon", "Commutative monoids", ["x+0 = x"])

InMon = Mon.subclass("InMon", "Involutive monoids",
                     ["(x*y)' = y'*x'", "x'' = x"])

Grp = FO_Theory("Grp", "Groups", [assoc("*"), "x*1 = x", "x*x' = 1"],
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

Slat = FO_Theory("Slat", "Semilattices", [assoc("*"), comm("*"), "x*x = x"])

Lat = FO_Theory("Lat", "Lattices",
                [assoc(" v "), comm(" v "), assoc("^"), comm("^"),
                 absorption(" v ", "^"), absorption("^", " v ")],
                results=["x v x = x", "x^x = x"])

DLat = Lat.subclass("DLat", "Distributive lattices", [distr("^", " v ")],
                    results=[distr(" v ", "^"),
                             "((x v y)^(x v z))^(y v z) = ((x^y)v(x^z))v(y^z)"])

MLat = Lat.subclass(
    "MLat", "Modular lattices", ["x^(y v (x^z)) = (x^y) v (x^z)"])

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

FL_eo = CRL.subclass(
    "FL_eo", "Full Lambek algebras with bottom", ["x v 0 = x"])

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

DInFL = InFL.subclass(
    "DInFL", "Distributive involutive FL-algebras", [distr("^", " v ")])

CyInFL = LMon.subclass("CyInFL", "Cyclic involutive FL-algebras", ["~~x = x", "0 = ~1",
                                                                   "~(x^y)=~x v ~y", "(x*~(~z*x))v z = z", "(~(y*~z)*y) v z = z",
                                                                   "y = y^(~(~(x*y)*x))", "x = x^(~(y*~(x*y)))"],
                       options=['op(350, prefix, "~")'],
                       results=["(x*y) v z = z -> y^~(~z*x) = y"])

MTL = FL_ew.subclass(
    "MTL", "Monoidal t-norm logic algebras", ["(x->y)v(y->x) = 1"])

HA = BDLat.subclass("HA", "Heyting algebras", ["(x->x) = 1", "(x->y)^y = y",
                                               "x^(x->y) = x^y", "(x->(y^z)) = (x->y)^(x->z)",
                                               "((x v y)->z) = (x->z)^(y->z)"],
                    results=["x = x^(y->((y^x) v z))", "(y^(y->x)) v x = x"])

GodelA = HA.subclass("GodelA", "Goedel algebras", ["x/y v y/x = 1"])

MValg = CMon.subclass("MValg", "MV-algebras", ["~~x = x", "x+~0 = ~0",
                                               "~(~x+y)+y = ~(~y+x)+x"],
                      results=["~(~x+x)+x = x"])

BLalg = MTL.subclass("BLalg", "Basic logic algebras", ["x^y = x*(x->y)"])

# defined above OLat = BLat.subclass("", "Ortholattices", ["x v x' = 1",
# "x^x'=0"])

# OMLat =

# MOLat


#########################################
# Sequent calculi (quasi-equational form)

RLseq = FO_Theory("RLseq", "Residuated lattice sequent calculus", ["(x*y)*z = x*(y*z)",
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

FL_oseq = FO_Theory(
    "FL_oseq", "FL-algebras with bottom sequent calculus", ["(x*0)*y = z"])


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

KAseq = FO_Theory("KAseq", "Kleene algebra sequent calculus", ["(x;y);z = x;(y;z)",
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
                                                         idem(
                                                             "^"), "(x^y)'=x'^y'", "(x*(y^z)) ^ (x*y) = x*(y^z)",
                                                         "(x*y)^z = ((x^(z*y'))*y)^z"])

##########################
# Other equational classes

Qdl = FO_Theory("Qdl", "Quandels",
                [idem("*"), "(x*y)/y = x", "(x/y)*y = x", rdistr("*", "*")])

Band = FO_Theory("Band", "Bands", [assoc("*"), idem("*")])

RectBand = Band.subclass("RectBand", "Rectangular bands", ["(x*y)*z = x*z"])

Qgrp = FO_Theory("Qgrp", "Quasigroups",
                 ["(x*y)/y = x", "(x/y)*y = x", "x\\(x*y) = y", "x*(x\\y) = y"])

Loop = Qgrp.subclass("Loop", "Loops", ["x*1 = x", "1*x = x"])

STS = Qgrp.subclass("STS", "Steiner triple systems", [idem("*"), comm("*")])


#####################
# First-order classes

PreOrd = FO_Theory("PreOrd", "Preordered sets", [refl("<="), trans("<=")])

Pos = PreOrd.subclass("Pos", "Partially ordered sets", [antisymm("<=")])

StrPos = FO_Theory(
    "StrPos", "Strict partially ordered sets", [irrefl("<"), trans("<")])

Chains = Pos.subclass("Chains", "Linearly ordered sets", ["x<=y | y<=x"])

####################
# Ordered structures

poGrpoid = Pos.subclass("poGrpoid", "Partially ordered groupoids",
                        ["x<=y -> x*z<=y*z", "x<=y -> z*x<=z*y"])

poCGrpoid = Pos.subclass("poCGrpoid", "Partially ordered commutative groupoids",
                         [comm("*"), "x<=y -> x*z<=y*z"])

oGrpoid = Chains.subclass("oGrpoid", "Linearly ordered groupoids",
                          ["x<=y -> x*z<=y*z", "x<=y -> z*x<=z*y"])

oCGrpoid = oGrpoid.subclass(
    "oCGrpoid", "Linearly ordered commutative groupoids", [comm("*")])

poSgrp = poGrpoid.subclass("poSgrp", "po-semigroups", Sgrp)

poCSgrp = poSgrp.subclass(
    "poCSgrp", "Partially ordered commutative semigroups", [comm("*")])

oSgrp = oGrpoid.subclass("oSgrp", "Linearly ordered semigroups", Sgrp)

oCSgrp = oSgrp.subclass(
    "oCSgrp", "Linearly ordered commutative semigroups", [comm("*")])

poMon = poGrpoid.subclass("poMon", "po-monoids", Mon)

poCMon = poMon.subclass(
    "poCMon", "Partially ordered commutative monoids", [comm("*")])

oMon = oGrpoid.subclass("oMon", "Linearly ordered monoids", Mon)

oCMon = oMon.subclass(
    "oCMon", "Linearly ordered commutative monoids", [comm("*")])

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

roSgrp = roGrpoid.subclass(
    "roSgrp", "Residuated linearly ordered semigroups", Sgrp)

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

irpoSgrp = irpoGrpoid.subclass(
    "irpoSgrp", "Integral residuated po-semigroups", Sgrp)

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

NAat = FO_Theory("NAat", "Nonassociative relation algebra atomstructures",
                 ["C(x,y,z) -> C(x',z,y)", "C(x,y,z) -> C(z,y',x)",
                  "x=y <-> exists u(E(u) & C(x,u,y))"])

INAat = FO_Theory("INAat", "Integral nonassociative relation algebra atomstructures",
                  ["C(x,y,z) -> C(x',z,y)", "C(x,y,z) -> C(z,y',x)",
                   "C(x,0,y) <-> x=y"],
                  results=["C(x',z,y) -> C(x,y,z)", "C(z,y',x) -> C(x,y,z)",
                           "x''=x", "C(0,x,y) <-> x=y"])

INAat1 = FO_Theory("INAat1", "Integral nonassociative relation algebra atomstructures",
                   ["C(x,y,z) -> C(x',z,y)", "C(x,y,z) -> C(z,y',x)",
                    "C(x,1,y) <-> x=y"],
                   results=["C(x',z,y) -> C(x,y,z)", "C(z,y',x) -> C(x,y,z)",
                            "x''=x", "C(1,x,y) <-> x=y"])

SNAat = FO_Theory("SNAat", "Symmetric nonassociative relation algebra atomstructures",
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

SeqAat = FO_Theory("SeqAat", "Sequential algebra atomstructures",
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

BK = FO_Theory("BK", "BK logic,  reduct of FL_w", [Bb, Kk, MP,
                                                   "P(y) & P(x->(y->z)) -> P(x->z)"])

BCK = FO_Theory("BCK", "BCK logic, -> reduct of FL_ew", [Bb, Cc, Kk, MP])

BCKP = FO_Theory(
    "BCKP", "BCK logic + Pierce law, -> reduct of CL", [Bb, Cc, Kk, Pierce, MP])

BCI = FO_Theory("BCI", "BCI logic, -> reduct of FL_e", [Bb, Cc, Ii, MP])

BCIS = FO_Theory(
    "BCIS", "BCIS=BCIW logic, -> reduct of FL_ec", [Bb, Cc, Ii, Ss, MP])

SK = FO_Theory(
    "SK", "Hilbert logic, -> reduct of intuitionistic logic", [Ss, Kk, MP])

CL = FO_Theory("CL", "Classical logic", [Ss, Kk, DN, CP, MP])

if __name__ == "__main__":
    import doctest
    doctest.testmod()
