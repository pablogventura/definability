#!/usr/bin/env python
# -*- coding: utf8 -*-

from ..first_order.model import FO_Model, FO_Product
from ..functions.morphisms import Homomorphism
from ..first_order.fofunctions import FO_Operation, FO_Constant
from ..first_order.fotype import FO_Type
from ..functions.congruence import minorice, is_system, CongruenceSystem, Congruence, maxcon, mincon
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
        self.generators = generators
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
        self.rsi = sub
        return sub

    def contiene(self, a):
        """
        Dada un algebra a, se fija si a pertenece a la cuasivariedad

        >>> from definability.first_order.fotheories import Lat
        >>> from definability.functions.morphisms import Homomorphism
        >>> type(Quasivariety(list(Lat.find_models(5))[0:3]).contiene(list(Lat.find_models(5))[3])) == Homomorphism
        True
        """
        if type(self.rsi) == list:
            rsi = self.rsi
        else:
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

    def is_rgi(self, a):
        """
        Determina si el algebra a es relativamente subdirectamente
        indescomponible en Q
        """
        cmi = self.cmi(a)
        atomics = gen_atomics(cmi, a)
        for atomic in atomics:
            n = len(atomic)
            atomic = list(atomic)
            for xs in list(itertools.product(*[a.universe for i in list(range(n))])):
                result = False
                if is_system(atomic, xs):
                    CS = CongruenceSystem(atomic, list(xs))
                    if not CS.has_solution():
                        result = True
                        break
            if not result:
                return False
        return True


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
    """
    Devuelve el supremo entre x e y dentro del reticulado de congruencias en Q
    """
    xcmi = {c for c in cmi if set(x.d) <= set(c.d)}
    ycmi = {c for c in cmi if set(y.d) <= set(c.d)}
    xycmi = xcmi & ycmi
    e = maxcon(x.model)
    for r in xycmi:
        e = e & r
    return e


def atoms(lat, model):
    """
    Devuelve los atomos del reticulado lat
    """
    mc = mincon(model)
    return minorice([x for x in lat.universe if x != mc])


def gen_lattice_cmi(universe, cmi, model, delta):
    """
    genera un reticulado apartir de un universo y una congruencia cmi
    """
    tiporetacotado = FO_Type({"^": 2, "v": 2, "Max": 0, "Min": 0}, {})
    univ = universe.copy()
    for c in universe:
        univ.append(c & delta)
    univ = list(set(univ))
    lat = FO_Model(tiporetacotado, univ, {
         'Max': FO_Constant(mincon(model)),
         'Min': FO_Constant(maxcon(model)),
         '^': FO_Operation({(x, y): x & y for x in univ for y in univ}),
         'v': FO_Operation({(x, y): supQ(cmi, x, y) for x in univ for y in univ})}, {})
    return lat


def increasing_lattice(sublat, cmi, model):
    """
    Dado un subreticulado de congruencias, le agrega los elementos para que
    quede un subreticulado creciente
    """
    atomss = set(atoms(sublat, model))
    for delta in cmi:
        if delta not in sublat.universe:
            for atom in atomss:
                if atom <= delta:
                    sublat = gen_lattice_cmi(sublat.universe, cmi, model, delta)
                    atomss = set(atoms(sublat, model))
                    break
    return (sublat, atomss)


def gen_atomics(cmi, model):
    """
    Genera todas las tuplas atómicas a partir del conjunto de las cmi
    """
    result = []
    for delta in cmi:
        lat = gen_lattice_cmi([mincon(model), maxcon(model)], cmi, model, delta)
        s = increasing_lattice(lat, cmi, model)
        if len(s[1]) > 1:
            result.append(s[1])
        iterar(cmi, model, s[0], result)
    return result


def iterar(cmi, model, lat, result):
    for delta in set(cmi) - set(lat.universe):
        lat = gen_lattice_cmi(lat.universe, cmi, model, delta)
        s = increasing_lattice(lat, cmi, model)
        if s[1] in result:
            break
        if len(s[1]) > 1:
            result.append(s[1])
        iterar(cmi, model, s[0], result)

if __name__ == "__main__":
    import doctest
    doctest.testmod()