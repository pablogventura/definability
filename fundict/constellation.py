#!/usr/bin/env python
# -*- coding: utf8 -*-

from networkx import MultiDiGraph
from examples import *
from collections import defaultdict


class Constellation(object):
    """
    Maneja una coleccion de modelos relacionados por flechas
    """
    def __init__(self):
        self.graph = MultiDiGraph()
        self.planets = defaultdict(list) # diccionario con key de len(planet)
        self.satellites = defaultdict(list) # diccionario con key de len(satellite)

    def add_planet(self, planet):
        #agrega un planeta
        self.planets[len(planet)].append(planet)
        self.graph.add_node(planet)

    def add_satellite(self, satellite, inclusion, planet):
        #agrega un satellite y por una funcion de inclusion
        self.satellite[len(satellite)].append(satellite)
        self.graph.add_node(planet)

    def generate(self,subtype):
        """
        Ordeno planetas por tamaño de mayor a menor
        Recorro subestructuras de menor a mayor haciendo 'lo de siempre',
            si son del mismo tamaño que que un planeta no revisado me fijo si es isomorfo y preserva*, y en ese caso se borra ese planeta
                * es muy posible que no haga falta revisar si preserva ya que es isomorfo, y mediante automorfismos de la original basta.
        Lo de siempre:
            Revisar automorfismos de la subestructrura, y revisar un solo isomorfismo contra las subestructuras isomorfas.
        """
    def ppnetwork(na,archivo):
        G = nx.DiGraph()
        G.add_edges_from([tuple(k) for k in na])

        pos=nx.graphviz_layout(G,prog='dot',args='')
        plt.figure(figsize=(8,8))
        nombres = {tuple(k):back(na[k][1]) for k in na}
        edge_labels=nx.draw_networkx_edge_labels(G,pos,edge_labels=nombres,label_pos=0.8)
        nx.draw(G,pos,node_size=200,alpha=1,node_color="white", with_labels=True)
        plt.axis('equal')
        plt.savefig('%s.png' % archivo)
        plt.show()

