#!/usr/bin/env python
# -*- coding: utf8 -*-

def limpiar_isos(algebras):
    """
    Dado un cojunto de álgebras, devuelve el conjunto que deja un representante
    por álgebras isomórficas

    >>> from definability.fotheories import Lat
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

    >>> from definability.fotheories import Lat
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
                sub.append(s[1])
    algebras = limpiar_isos(sub)
    alg = algebras.copy()
    for a in algebras:
        if a in alg:
            F = set()
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
    """
    algebras = conj_rsi(algebras)
    if a in algebras:
        return True
    else:
        F = set()
        ker = {(x, y) for x in a.universe for y in a.universe}
        mincon = {(x, x) for x in a.universe}
        for b in algebras:
            for f in a.homomorphisms_to(b, a.fo_type, surj=True):
                F.add(f)
        for f in F:
            ker = ker & {tuple(t) for t in f.kernel().table()}
            if ker == mincon:
                return True
    return False
