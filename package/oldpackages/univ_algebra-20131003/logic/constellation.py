#!/usr/bin/env python
# -*- coding: utf8 -*-

import networkx
from model import Model
from misc import *
import minion

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
            
    def remove_planet(self, planet):
        """un planeta es un modelo padre de subestructuras a revisar"""
        self.graph.remove_node(planet)
        self.planets[len(planet)] = filter(lambda p: p!=planet, self.planets[len(planet)])
            
    def generate(self):
        # asumo que hay un solo modelo original
        # TODO NO SE ROMPERIA CON LOS ISOMORFISMOS?
        model = self.graph.nodes()[0]
        subs = list(model.substructures())
        subs.sort(key=lambda x:len(x[0])) # ordeno por tamanno
        subs.pop(-1) # es el mismo "model"
        for substr,emb in subs:
            self.graph.add_edge(substr, model, arrow_type = "embedding", arrow=emb) # agrego el embbeding original
            auts = substr.Aut() # busco los automorfismos
            for aut in auts:
                self.graph.add_edge(substr, model, arrow_type = "embedding", arrow=emb.composition(aut)) # agrego las composiciones
    def generate2(self):
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
                for satellite, embbedding in planet.substructures():
                    # substructures los devuelve de menor a mayor
                    pass
                
    def add_arrow(self, source, destination, arrow_type, function, dif_rel):
        """
        Agrega una flecha, pero tiene que preservar dif_rel para ser agregada
        """
        for t in dif_rel.table(relation=True):
            ft = map(function, t)
            if dif_rel(*ft):
                # Preserva! se puede agregar efectivamente
                self.graph.add_edge(source, destination, arrow_type, arrow=function)
            else:
                raise ValueError
            
    def calculate_substructures(self):
        for model in self.graph.nodes():
            for substr,emb in model.substructures():
                self.graph.add_edge(substr, model, arrow_type = "embedding", arrow=emb)

