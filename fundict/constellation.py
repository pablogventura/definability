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
        Agrega un planeta
        """
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


class Constellation(TipedMultiDiGraph):
    """
    
    >>> from examples import *
    >>> from constellation import *
    >>> c = Constellation()
    >>> c.add_planet(retrombo)
    >>> c.is_open_definable(tiporet,tiporet+tipoposet)
    (True, None)
    >>> c.is_open_definable(tiporet,tiporet+tipotest)
    (False, Isomorphism(
      [2] -> 0,
    ,
      FO_Type({'v': 2, '^': 2},{})
    ,
      Injective,
      Surjective,
    ))
    """
    def is_open_definable(self,subtype,supertype):
        """
        Busca isomorfismos internos en subtype para saber si preservan supertype-subtype
        Devuelve una tupla (booleano, contraejemplo)
        """
        for len_planets in sorted(self.planets.iterkeys()):
            for planet in self.planets[len_planets]:
                for (inc,protosatellite) in planet.substructures(subtype):
                    iso = protosatellite.is_isomorphic_to_any(self.satellites[len(protosatellite)],subtype)
                    if iso:
                        if not iso.preserves_type(supertype):
                            return (False,iso)
                        self.add_arrow(inc.composition(iso.inverse())) #agregar embedding desde satellite a planet
                    else:
                        self.add_satellite(protosatellite,inc,planet) # merece ser un satellite
                        self.add_arrows(protosatellite.isomorphisms_to(protosatellite,subtype)) # le busco automorfismos
        return (True,None)
        
        
        
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
