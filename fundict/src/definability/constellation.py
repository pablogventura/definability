#!/usr/bin/env python
# -*- coding: utf8 -*-
import networkx
from examples import *
from collections import defaultdict
from itertools import product, chain
from minion import GroupMinionSol
from morphisms import Embedding


def check_history(func):
    """
    Decorador para llevar la historia y no recalcular
    """

    def f(self, subtype, supertype):
        param = (func.func_name, subtype, supertype)
        if param in self.history:
            return self.history[param]
        else:
            result = func(self, subtype, supertype)
            self.history[param] = result
            return result
    f.func_doc = func.func_doc
    return f


class TipedMultiDiGraph(object):

    """
    Maneja una coleccion de modelos relacionados por flechas
    """

    def __init__(self, planets=[]):
        self.graph = networkx.MultiDiGraph()
        self.planets = defaultdict(list)  # diccionario con key de len(planet)
        # diccionario con key de len(satellite)
        self.satellites = defaultdict(list)
        self.history = {}
        try:
            for planet in iter(planets):
                self.add_planet(planet)
        except TypeError:
            self.add_planet(planets)

    def add_planet(self, planet):
        """
        Agrega un planeta, solo si no esta.
        """
        if planet not in self.planets[len(planet)]:
            self.planets[len(planet)].append(planet)
            self.graph.add_node(planet)

    def add_satellite(self, satellite, inclusion):
        """
        Agrega un satellite y una funcion de inclusion
        """
        self.satellites[len(satellite)].append(satellite)
        self.graph.add_node(satellite)
        self.add_arrow(inclusion)

    def degrade(self, explanet, inclusion):
        """
        Degrada un planeta a satelite.
        """
        self.planets[len(explanet)].remove(explanet)
        self.satellites[len(explanet)].append(explanet)
        self.add_arrow(inclusion)

    def add_arrow(self, arrow):
        """
        Agrega una flecha, si ya habia una flecha con comportamiento igual, se queda con la
        que tiene mas informacion (i.e. entre embedding y homomorfismo se queda con embedding)

        >>> from morphisms import *
        >>> from examples import retrombo
        >>> c = TipedMultiDiGraph()
        >>> c.add_planet(retrombo)
        >>> c.add_arrow(Homomorphism([0,1,2,3],retrombo,retrombo,tiporet))
        >>> c.add_arrow(Embedding([0,1,2,3],retrombo,retrombo,tiporet))
        >>> c.add_arrow(Isomorphism([0,1,2,3],retrombo,retrombo,tiporet))
        >>> c.add_arrow(Embedding([0,1,2,3],retrombo,retrombo,tiporet))
        >>> c.add_arrow(Homomorphism([0,1,2,3],retrombo,retrombo,tiporet))
        >>> c.graph[retrombo][retrombo].values()
        [{'arrow': Automorphism(
          [0] -> 0,
          [1] -> 1,
          [2] -> 2,
          [3] -> 3,
        ,
          FO_Type({'v': 2, '^': 2},{})
        ,
          Injective,
          Surjective,
        )}]
        """
        assert self.graph.has_node(
            arrow.source) and self.graph.has_node(arrow.target)
        duplicate = self.__find_arrow(arrow)
        if duplicate:
            # print "esa flecha ya estaba! capaz con otro morphtype, o fotype?"
            # print "%s de %s y %s de %s" %
            # (type(arrow),arrow.subtype,type(duplicate),duplicate.subtype)
            # el hijo es el tipo de morfismo mas restrictivo
            if issubclass(type(arrow), type(duplicate)):
                # print "queda el %s" % type(arrow)
                self.graph.remove_edge(
                    duplicate.source, duplicate.target, hash(duplicate))
                self.graph.add_edge(
                    arrow.source, arrow.target, key=hash(arrow), arrow=arrow)
        else:
            self.graph.add_edge(
                arrow.source, arrow.target, key=hash(arrow), arrow=arrow)

    def add_arrows(self, arrows):
        """
        Agrega flechas llamando varias veces a add_arrow
        """
        for arrow in arrows:
            self.add_arrow(arrow)

    def __find_arrow(self, arrow):
        """
        Busca si hay una flecha entre los mismos nodos, con el mismo comportamiento y la devuelve.
        """
        if self.graph.has_edge(arrow.source, arrow.target, key=hash(arrow)):
            return self.graph[arrow.source][arrow.target][hash(arrow)]["arrow"]
        else:
            return None

    def show(self):
        """
        Dibuja la constelacion
        """
        import matplotlib.pyplot as plt
        import os
        from PIL import Image
        os.system("rm multi.png")
        networkx.write_dot(self.graph, 'multi.dot')
        os.system("rm multi.png;dot -T png multi.dot > multi.png")
        img = Image.open('multi.png')
        plt.imshow(img)
        plt.show()

    def arrows(self, source, target, morphtype=None, subtype=None):
        """
        Devuelve la lista de flechas desde source a target
        del tipo de morfismo en morphtype, del subtype
        """
        try:
            result = self.graph[source][target]
        except KeyError:
            result = []
        if result:
            result = [e['arrow'] for e in result.values()]
        if morphtype:
            result = filter(lambda x: isinstance(x, morphtype), result)
        if subtype:
            result = filter(lambda x: subtype.is_subtype_of(x.subtype), result)
        return result

    def add_check_arrows(self, arrows, subtype, supertype):
        """
        Agrega flechas y chequea que preserven.
        Devuelve la primera que encuentre que no preserva, sino None.
        """
        for arrow in arrows:
            ce = self.add_check_arrow(arrow, subtype, supertype)
            if ce:
                return ce

    def add_check_arrow(self, arrow, subtype, supertype):
        """
        Agrega una flecha y chequea que preserve.
        Si no preserva, la devuelve, sino None.
        """
        assert subtype.is_subtype_of(arrow.subtype)  # checkeo por las dudas

        self.add_arrow(arrow)
        if not arrow.preserves_type(supertype):
            return arrow

    def iter_satellites(self, subtype, cardinality=None, without=[]):
        """
        Itera sobre los satelites de largo cardinality, quitando los que estan en without
        """
        # TODO iter_satellite trata diferente al subtype, comparado con satellites_of
        # esto es muy poco intuitivo y puede ser peligroso
        assert not isinstance(subtype, int), subtype
        if cardinality:
            for satellite in self.satellites[cardinality]:
                if satellite.fo_type.is_subtype_of(subtype) and satellite not in without:
                    yield satellite
        else:
            for lensat in sorted(self.satellites.keys(), reverse=True):
                for satellite in self.satellites[lensat]:
                    if satellite.fo_type.is_subtype_of(subtype) and satellite not in without:
                        yield satellite

    def iter_arrows(self, subtype, morphtype=None):
        for source, target in product(chain(self.iter_planets(), self.iter_satellites(subtype)), repeat=2):
            for arrow in self.arrows(source, target, morphtype, subtype):
                yield arrow

    def iter_planets(self, cardinality=None, without=[]):
        """
        Itera sobre los planetas de largo cardinality, quitando los que estan en without
        """
        if cardinality:
            for planet in self.planets[cardinality]:
                if planet not in without:
                    yield planet
        else:
            for lenplanet in sorted(self.planets.keys(), reverse=True):
                for planet in self.planets[lenplanet]:
                    if planet not in without:
                        yield planet

    def satellites_of(self, planet, subtype, cardinality=None):
        """
        Devuelve una lista con los satelites de planet, ordenados de mayor a menor en cardinalidad.
        """
        result = sorted(self.graph.predecessors(planet), reverse=True, key=len)

        result = filter(
            lambda s: bool(self.arrows(s, planet, Embedding, subtype)), result)

        if not cardinality:
            return result
        else:
            return filter(lambda x: len(x) == cardinality, result)

    def main_satellite_of(self, planet, subtype):
        """
        Devuelve el satelite principal, o sea el que tiene el mismo universo que planet.
        """
        return self.satellites_of(planet, subtype, len(planet))[0]

    def main_satellites(self, subtype):
        """
        Devuelve los satelites principales de todos los planetas.
        """
        return (self.main_satellite_of(planet, subtype) for planet in self.iter_planets())

    def is_isomorphic(self, other):
        """
        Busca un isomorfismo entre constellations
        No esta muy probado, es mas que nada para usar en testing
        """
        return networkx.is_isomorphic(self.graph, other.graph)


class Constellation(TipedMultiDiGraph):

    """

    >>> from examples import *
    >>> from constellation import *
    >>> from minion import MinionSol
    >>> c = Constellation()
    >>> c.add_planet(retrombo)
    >>> c.is_open_definable(tiporet,tiporet+tipoposet)
    (True, None)
    >>> c.is_open_definable(tiporet,tiporet+tipotest)
    (False, Embedding(
      [0] -> 2,
    ,
      FO_Type({'v': 2, '^': 2},{})
    ,
      antitype= ['P']
    ,
      Injective,
    ))
    >>> old = MinionSol.count
    >>> c.is_open_definable(tiporet,tiporet+tipotest)
    (False, Embedding(
      [0] -> 2,
    ,
      FO_Type({'v': 2, '^': 2},{})
    ,
      antitype= ['P']
    ,
      Injective,
    ))
    >>> old == MinionSol.count
    True
    """

    def __open_check_protosatellite(self, protosatellite, inc, planet, subtype, supertype):
        """
        Calcula el lugar que le toca al protosatellite y lo coloca ahi.
        Si encuentra un contraejemplo para definir por formulas abiertas, lo devuelve.
        Si no encuentra contraejemplo devuelve None
        """
        iso = protosatellite.is_isomorphic_to_any(
            self.iter_satellites(subtype, len(protosatellite)), subtype)
        if iso:
            # agregar embedding de satellite a planet
            ce = self.add_check_arrow(
                inc.composition(iso.inverse()), subtype, supertype)
            if ce:
                return ce
        else:
            iso = protosatellite.is_isomorphic_to_any(
                self.iter_planets(len(protosatellite), [planet]), subtype)
            if iso:
                if not iso.preserves_type(supertype):
                    return iso
                explanet = iso.target
                self.degrade(explanet, inc.composition(iso.inverse()))
                ce = self.add_check_arrows(
                    explanet.isomorphisms_to(explanet, subtype), subtype, supertype)
                if ce:
                    return ce
            else:
                # merece ser un satellite
                self.add_satellite(protosatellite, inc)
                ce = self.add_check_arrows(protosatellite.isomorphisms_to(
                    protosatellite, subtype), subtype, supertype)  # autos
                if ce:
                    return ce

    @check_history
    def is_existential_definable(self, subtype, supertype):
        """
        Busca automorfismos en subtype para saber si preservan supertype-subtype
        Devuelve una tupla (booleano, contraejemplo)
        """
        for len_planets in sorted(self.planets.iterkeys(), reverse=True):  # desde el planeta mas grande
            for planet in self.planets[len_planets]:
                inc, protosatellite = planet.substructure(
                    planet.universe, subtype)  # satellite principal
                ce = self.__open_check_protosatellite(
                    protosatellite, inc, planet, subtype, supertype)
                if ce:
                    return (False, ce)
        return (True, None)

    @check_history
    def is_open_definable(self, subtype, supertype):
        """
        Busca isomorfismos internos en subtype para saber si preservan supertype-subtype
        Devuelve una tupla (booleano, contraejemplo)
        """

        (b, ce) = self.is_existential_definable(subtype, supertype)
        if not b:
            return (b, ce)  # no llego ni a ser definible

        # desde el planeta mas grande
        for len_planets in sorted(self.planets.iterkeys(), reverse=True):
            for planet in self.planets[len_planets]:
                for (inc, protosatellite) in planet.substructures(subtype, without=[planet.universe]):
                    ce = self.__open_check_protosatellite(
                        protosatellite, inc, planet, subtype, supertype)
                    if ce:
                        return (False, ce)
        return (True, None)

    @check_history
    def is_existential_positive_definable(self, subtype, supertype):
        """
        Busca endomorfismos en subtype para saber si preservan supertype-subtype
        Devuelve una tupla (booleano, contraejemplo)
        """
        (b, ce) = self.is_open_definable(subtype, supertype)
        if not b:
            # no llego ni a ser definible por una formula abierta
            return (b, ce)

        # homomorfismos entre planetas
        homos = GroupMinionSol()
        for a, b in product(self.main_satellites(subtype), repeat=2):
            homos.append(
                a.homomorphisms_to(b, subtype, without=self.arrows(a, b)))
        ce = self.add_check_arrows(homos, subtype, supertype)
        if ce:
            return (False, ce)
        return (True, None)

    @check_history
    def is_positive_open_definable(self, subtype, supertype):
        """
        Busca homomorfismos internos en subtype para saber si preservan supertype-subtype
        Devuelve una tupla (booleano, contraejemplo)
        """

        (b, ce) = self.is_existential_positive_definable(subtype, supertype)
        if not b:
            # no llego ni a ser definible por una formula existencial positiva
            return (b, ce)

        homos = GroupMinionSol()
        for a, b in product(self.iter_satellites(subtype), repeat=2):
            homos.append(
                a.homomorphisms_to(b, subtype, without=self.arrows(a, b)))
        ce = self.add_check_arrows(homos, subtype, supertype)
        if ce:
            return (False, ce)
        return (True, None)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
