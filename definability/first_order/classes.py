#!/usr/bin/env python
# -*- coding: utf8 -*-

from ..first_order.model import FO_Model, FO_Product
from ..functions.morphisms import Homomorphism
from ..first_order.fofunctions import FO_Operation, FO_Constant
from ..first_order.fotype import FO_Type
from ..functions.congruence import mincon, maxcon, minorice
from ..definability.relationalmodels import check_isos
import itertools


class Quasivariety(object):
    """
    Cuasivariedad generada por un conjunto de algebras finitas.
    """

    def __init__(self, generators, name=""):
        self.fo_type = generators[0].fo_type
        for i in range(len(generators)):
            assert generators[i].fo_type == self.fo_type, "Los generadores no tienen el mismo tipo"
        self.generators = limpiar_isos(generators)
        self.name = name

    def rsi(self):
        """
        Dada un conjunto de álgebras, devuelve el conjunto de álgebras relativamente
        subdirectamente irreducibles para la cuasivariedad generada.

        >>> from definability.first_order.fotheories import Lat
        >>> len(Quasivariety(Lat.find_models(5)).rsi())
        3
        """

        sub = []
        for a in self.generators:
            suba = a.substructures(a.fo_type)
            for s in suba:
                if len(s[1]) != 1 and not check_isos(s[1], sub, self.fo_type):
                    sub.append(s[1].continous()[0])
        n = len(sub)
        for i in range(n - 1, -1, -1):
            ker = {(x, y) for x in sub[i].universe for y in sub[i].universe}
            mincon = {(x, x) for x in sub[i].universe}
            t = False
            for j in range(0, len(sub)):
                if i != j:
                    for f in sub[i].homomorphisms_to(sub[j], self.fo_type, surj=True):
                        ker = ker & {tuple(t) for t in f.kernel().table()}
                        if ker == mincon:
                            sub.pop(i)
                            t = True
                            break
                if t:
                    break
        return sub

    def contiene(self, a):
        """
        Dada un algebra a, se fija si a pertenece a la cuasivariedad

        >>> from definability.first_order.fotheories import Lat
        >>> from definability.functions.morphisms import Homomorphism
        >>> type(Quasivariety(list(Lat.find_models(5))[0:3]).contiene(list(Lat.find_models(5))[3])) == Homomorphism
        True
        """
        rsi = self.rsi()
        if check_isos(a, rsi, self.fo_type):
            return "El álgebra es relativamente subirectamente irreducible"
        else:
            F = set()
            ker = {(x, y) for x in a.universe for y in a.universe}
            mincon = {(x, x) for x in a.universe}
            t = False
            for b in rsi:
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

    def cmi(self, a):
        """
        Dada un algebra a que pertenece a Q devuelve el conjunto de las
        congruencias completamente meet irreducibles.
        """
        f = self.contiene(a)
        if type(f) == bool:
            return "El álgebra no pertenece a Q"
        elif type(f) == Homomorphism:
            result = []
            for i in f.target.indices():
                result.append(f.target.projection(i).composition(f).kernel())
            return result
        return [mincon(a)]

    def congruence_lattice(self, a):
        """
        Dada un algebra a que pertenece a Q devuelve ConQ(a).
        """
        cmi = self.cmi(a)
        if type(cmi) == list:
            subs = []
            univ = [maxcon(a)]
            for n in range(len(cmi) + 1):
                for s in itertools.combinations(cmi, n):
                    subs.append(s)
            for s in subs:
                e = maxcon(a)
                for x in s:
                    e = e & x
                if e not in univ:
                    univ.append(e)
            tiporetacotado = FO_Type({"^": 2, "v": 2, "Max": 0, "Min": 0}, {})
            lat = FO_Model(tiporetacotado, univ, {
                     'Max': FO_Constant(maxcon(a)),
                     'Min': FO_Constant(mincon(a)),
                     '^': FO_Operation({(x,y): x & y for x in univ for y in univ}),
                     'v': FO_Operation({(x,y): supQ(cmi, x, y) for x in univ for y in univ})}, {})
            return lat
        return "El álgebra no pertenece a Q"


def limpiar_isos(algebras):
    """
    Dado un cojunto de álgebras, devuelve el conjunto que deja un representante
    por álgebras isomórficas

    >>> from definability.first_order.fotheories import Lat
    >>> len(limpiar_isos(Lat.find_models(5)))
    5
    >>> len(limpiar_isos( list(Lat.find_models(5)) + [Lat.find_models(5)[1]] ))
    5
    """
    n = len(algebras)
    for i in range(n - 1, 0, -1):
        if check_isos(algebras[i], algebras[0:i], algebras[i].fo_type):
            algebras.pop(i)
    return algebras


def supQ(cmi, x, y):
    xcmi = {c for c in cmi if set(x.d) <= set(c.d)}
    ycmi = {c for c in cmi if set(y.d) <= set(c.d)}
    xycmi = xcmi & ycmi
    e = maxcon(x.model)
    for r in xycmi:
        e = e & r
    return e


def atoms(lat, model):
    mc = mincon(model)
    return minorice([x for x in lat.universe if x != mc])

if __name__ == "__main__":
    import doctest
    doctest.testmod()