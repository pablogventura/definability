#!/usr/bin/env python
# -*- coding: utf8 -*-

import networkx
from examples import *

class Constellation():
    """
    Maneja una coleccion de modelos relacionados por flechas
    """
    def __init__(self, models):
        self.graph = networkx.DiGraph()
        
        self.planets = {} # diccionario con key de len(planet)
        self.satellites = {} # diccionario con key de len(satellite)
        for model in models:
            self.add_planet(model)

    def add_planet(self, planet):
        """un planeta es un modelo padre de subestructuras a revisar"""
        self.graph.add_node(planet)
        try:
            self.planets[len(planet)].append(planet)
        except:
            self.planets[len(planet)] = [planet]

    def add_satellite(self, satellite, planet):
        """un satellite es una subestructura"""
        self.graph.add_node(satellite)
        try:
            self.satellites[len(satellite)].append(satellite)
        except:
            self.satellites[len(satellite)] = [satellite]

    def generate(self,subtype):
        """
        Ordeno planetas por tamaño de mayor a menor
        Recorro subestructuras de menor a mayor haciendo 'lo de siempre',
            si son del mismo tamaño que que un planeta no revisado me fijo si es isomorfo y preserva*, y en ese caso se borra ese planeta
                * es muy posible que no haga falta revisar si preserva ya que es isomorfo, y mediante automorfismos de la original basta.
        Lo de siempre:
            Revisar automorfismos de la subestructrura, y revisar un solo isomorfismo contra las subestructuras isomorfas.
        """
        for len_planet in sorted(self.planets.keys(), reverse=True):
            for planet in self.planets[len_planet]:
                for proto_satellite, embbedding in planet.substructures(subtype):
                    iso = proto_satellite.is_isomorphic(self.satellites,subtype)
                    if iso:
                        # hay isomorfismo, solo agrego embedding
                        emb = iso.inverted().compone(embedding) # no queda claro el tipo de este embedding
                        self.add_arrow(emb)
                    else:
                        # agrego el satelite
                        self.add_satellite(proto_satellite,planet)
                    


