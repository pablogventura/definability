#!/usr/bin/env python
# -*- coding: utf8 -*-

from ..first_order.model import FO_Product
from ..functions.morphisms import Homomorphism

def limpiar_isos(algebras):
    """
    Dado un cojunto de álgebras, devuelve el conjunto que deja un representante
    por álgebras isomórficas

    >>> from definability.first_order.fotheories import Lat
    >>> B = limpiar_isos(Lat.find_models(5))
    >>> len(B)
    5
    >>> B.append(B[1])
    >>> B = limpiar_isos(B)
    >>> len(B)
    5
    """

    if not isinstance(algebras, list):
        alg = []
        for a in algebras:
            alg.append(a)
        algebras = alg.copy()
    alg = algebras.copy()
    elim = []
    for i in range(len(algebras)):
        alg.remove(algebras[i])
        for j in range(len(alg)):
            if algebras[i].is_isomorphic(alg[j], algebras[i].fo_type):
                elim.append(algebras[i])
                break
    for a in elim:
        algebras.remove(a)
    return algebras

def conj_rsi(algebras):
    """
    Dada un conjunto de álgebras, devuelve el conjunto de álgebras relativamente
    subdirectamente irreducibles para la cuasivariedad generada.

    >>> from definability.first_order.fotheories import Lat
    >>> B = conj_rsi(Lat.find_models(5))
    >>> len(B)
    3
    """

    algebras = limpiar_isos(algebras)
    sub = []
    for a in algebras:
        suba = a.substructures(a.fo_type)
        for s in suba:
            if not len(s[1]) == 1:
                b = s[1].continous()[0]
                sub.append(b)
    algebras = limpiar_isos(sub)
    alg = algebras.copy()
    for a in algebras:
        if a in alg:
            ker = {(x, y) for x in a.universe for y in a.universe}
            mincon = {(x, x) for x in a.universe}
            t = False
            for b in alg:
                if not a == b:
                    for f in a.homomorphisms_to(b, a.fo_type, surj=True):
                        ker = ker & {tuple(t) for t in f.kernel().table()}
                        if ker == mincon:
                            alg.remove(a)
                            t = True
                            break
                    if t:
                        break
    return alg

def pertenece_rsi(a, algebras):
    """
    Dada un algebra a, se fija si a pertenece a la cuasivariedad generada por el
    conjunto algebras

    >>> from definability.first_order.fotheories import Lat
    >>> from definability.functions.morphisms import Homomorphism
    >>> B = Lat.find_models(5)
    >>> F = pertenece_rsi(B[3],B[0:3])
    >>> type(F) == Homomorphism
    True
    """
    algebras = conj_rsi(algebras)
    if a in algebras:
        return "El álgebra está en el conjunto"
    else:
        F = set()
        ker = {(x, y) for x in a.universe for y in a.universe}
        mincon = {(x, x) for x in a.universe}
        t = False
        for b in algebras:
            for f in a.homomorphisms_to(b, a.fo_type, surj=True):
                ker = ker & {tuple(t) for t in f.kernel().table()}
                F.add(f)
                if ker == mincon:
                    t = True
                    break
            if t:
                break
    if t:
        target = FO_Product([f.target for f in F])
        d = {}
        for x in a.universe:
            d[(x,)] = tuple([f(x,) for f in F])
        return Homomorphism(d, a, target, a.fo_type)
    else:
        return False
