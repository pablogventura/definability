#!/usr/bin/env python
# -*- coding: utf8 -*-
from networkx import MultiDiGraph
from examples import *
from collections import defaultdict

class TipedMultiDiGraph(object):
    """
    Maneja una coleccion de modelos relacionados por flechas
    """
    def __init__(self):
        self.graph = MultiDiGraph()
        self.planets = defaultdict(list) # diccionario con key de len(planet)
        self.satellites = defaultdict(list) # diccionario con key de len(satellite)

    def add_planet(self, planet):
        """
        Agrega un planeta, solo si no esta.
        """
        if planet not in self.planets[len(planet)]:
            self.planets[len(planet)].append(planet)
            self.graph.add_node(planet)

    def add_satellite(self, satellite, inclusion, planet):
        """
        Agrega un satellite y una funcion de inclusion
        """
        self.satellites[len(satellite)].append(satellite)
        self.graph.add_node(satellite)
        self.add_arrow(inclusion)

    def degrade(self, explanet, inclusion, planet):
        """
        Degrada un planeta a satelite.
        """
        self.planets[len(explanet)].remove(explanet)
        self.satellites[len(explanet)].append(explanet)
        self.add_arrow(inclusion)

    def add_arrow(self,arrow):
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
        assert self.graph.has_node(arrow.source) and self.graph.has_node(arrow.target)
        duplicate = self.__find_arrow(arrow)
        if duplicate:
            #print "esa flecha ya estaba! capaz con otro morphtype, o fotype?"
            #print "%s de %s y %s de %s" % (type(arrow),arrow.subtype,type(duplicate),duplicate.subtype)
            if issubclass(type(arrow),type(duplicate)): # el hijo es el tipo de morfismo mas restrictivo
                #print "queda el %s" % type(arrow)
                self.graph.remove_edge(duplicate.source,duplicate.target,hash(duplicate))
                self.graph.add_edge(arrow.source,arrow.target,key=hash(arrow),arrow=arrow)
        else:
            self.graph.add_edge(arrow.source,arrow.target,key=hash(arrow),arrow=arrow)
    
    def add_arrows(self,arrows):
        """
        Agrega flechas llamando varias veces a add_arrow
        """
        for arrow in arrows:
            self.add_arrow(arrow)
            
    def __find_arrow(self,arrow):
        """
        Busca si hay una flecha entre los mismos nodos, con el mismo comportamiento y la devuelve.
        """
        if self.graph.has_edge(arrow.source,arrow.target,key=hash(arrow)):
            return self.graph[arrow.source][arrow.target][hash(arrow)]["arrow"]
        else:
            return None
        
    def find_arrows(self, source, target, morphtype=None):
        """
        Busca las flechas entre source y target, del tipo morphtype
        """
        if self.graph.has_edge(source,target):
            result = [x["arrow"] for x in self.graph[source][target].values()]
            if morphtype:
                result = filter(lambda x: isinstance(x,morphtype),result)
            return result
        else:
            return []
        
        
    def show(self):
        """
        Dibuja la constelacion
        """
        import networkx as nx
        import matplotlib.pyplot as plt
        import os
        from PIL import Image
        os.system("rm multi.png")
        nx.write_dot(self.graph,'multi.dot')
        os.system("rm multi.png;dot -T png multi.dot > multi.png")
        img = Image.open('multi.png')
        plt.imshow(img)
        plt.show()
    def arrows(self, source, target):
        """
        Devuelve la lista de flechas desde source a target
        """
        try:
            result = self.graph[source][target]
        except KeyError:
            result = []
        if result:
            result = [e['arrow'] for e in result.values()]
        return result
        
    def add_check_arrows(self, arrows, subtype, supertype):
        """
        Agrega flechas y chequea que preserven.
        Devuelve la primera que encuentre que no preserva, sino None.
        """
        for arrow in arrows:
            ce = self.add_check_arrow(arrow,subtype,supertype)
            if ce:
                return ce
                
    def add_check_arrow(self, arrow, subtype, supertype):
        """
        Agrega una flecha y chequea que preserve.
        Si no preserva, la devuelve, sino None.
        """
        assert subtype.is_subtype_of(arrow.subtype) # checkeo por las dudas
        
        if arrow.preserves_type(supertype):
            self.add_arrow(arrow)
        else:
            return arrow

    def iter_satellites(self, cardinality, without=[]):
        """
        Itera sobre los satelites de largo cardinality, quitando los que estan en without
        """
        for satellite in self.satellites[cardinality]:
            if satellite not in without:
                yield satellite

    def iter_planets(self, cardinality, without=[]):
        """
        Itera sobre los planetas de largo cardinality, quitando los que estan en without
        """
        for planets in self.planets[cardinality]:
            if planets not in without:
                yield planets

    def satellites_of(self, planet, cardinality=None):
        """
        Devuelve una lista con los satelites de planet, ordenados de mayor a menor en cardinalidad.
        """
        result = sorted(self.graph.predecessors(planet),reverse=True, key=len)
        if not cardinality:
            return result
        else:
            return filter(lambda x: len(x) == cardinality, result)

class Constellation(TipedMultiDiGraph):
    """
    
    >>> from examples import *
    >>> from constellation import *
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
      Injective,
    ))
    """

    def __open_check_protosatellite(self,protosatellite, inc, planet, subtype, supertype):
        """
        Calcula el lugar que le toca al protosatellite y lo coloca ahi.
        Si encuentra un contraejemplo para definir por formulas abiertas, lo devuelve.
        Si no encuentra contraejemplo devuelve None
        """
        iso = protosatellite.is_isomorphic_to_any(self.iter_satellites(len(protosatellite)),subtype)
        if iso:
            ce = self.add_check_arrow(inc.composition(iso.inverse()),subtype,supertype) #agregar embedding de satellite a planet
            if ce:
                return ce
        else:
            iso = protosatellite.is_isomorphic_to_any(self.iter_planets(len(protosatellite),[planet]),subtype)
            if iso:
                if not iso.preserves_type(supertype):
                    return iso
                explanet = iso.target
                self.degrade(explanet,inc.composition(iso.inverse()),planet)
                ce = self.add_check_arrows(explanet.isomorphisms_to(explanet,subtype), subtype, supertype)
                if ce:
                    return ce
            else:
                self.add_satellite(protosatellite,inc,planet) # merece ser un satellite
                ce = self.add_check_arrows(protosatellite.isomorphisms_to(protosatellite,subtype), subtype, supertype)#autos
                if ce:
                    return ce
    
    def is_existential_definable(self, subtype, supertype):
        """
        Busca automorfismos en subtype para saber si preservan supertype-subtype
        Devuelve una tupla (booleano, contraejemplo)
        """
        for len_planets in sorted(self.planets.iterkeys(),reverse=True): # desde el planeta mas grande
            for planet in self.planets[len_planets]:
                inc,protosatellite = planet.substructure(planet.universe, subtype)
                ce = self.__open_check_protosatellite(protosatellite, inc, planet, subtype, supertype)
                if ce:
                    return (False, ce)
        return (True,None)
        
    def is_open_definable(self,subtype,supertype):
        """
        Busca isomorfismos internos en subtype para saber si preservan supertype-subtype
        Devuelve una tupla (booleano, contraejemplo)
        """

        (b,ce)=self.is_existential_definable(subtype,supertype)
        if not b:
            return (b,ce) # no llego ni a ser definible

        for len_planets in sorted(self.planets.iterkeys(),reverse=True): # desde el planeta mas grande
            for planet in self.planets[len_planets]:
                for (inc,protosatellite) in planet.substructures(subtype, without=[planet.universe]):
                    ce = self.__open_check_protosatellite(protosatellite, inc, planet, subtype, supertype)
                    if ce:
                        return (False, ce)
        return (True,None)

    def is_existential_positive_definable(self, subtype, supertype):
        """
        Busca automorfismos en subtype para saber si preservan supertype-subtype
        Devuelve una tupla (booleano, contraejemplo)
        """
        (b,ce)=self.is_open_definable(subtype,supertype)
        if not b:
            return (b,ce) # no llego ni a ser definible por una formula abierta
        print (len(self.graph.nodes()), len(self.graph.edges()))
        for len_planets in sorted(self.planets.iterkeys(),reverse=True): # desde el planeta mas grande
            for planet in self.planets[len_planets]:
                satellite = self.satellites_of(planet, len_planets)[0] # satelite principal
                ce = self.add_check_arrows(satellite.homomorphisms_to(satellite,
                                                                      subtype,
                                                                      without=self.arrows(satellite,
                                                                                          satellite)),
                                           subtype,
                                           supertype)
                if ce:
                    return (False, ce)
        print (len(self.graph.nodes()), len(self.graph.edges()))
        return (True,None)
        
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
