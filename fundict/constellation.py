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
        #agrega un planeta
        self.planets[len(planet)].append(planet)
        self.graph.add_node(planet)

    def add_satellite(self, satellite, inclusion, planet):
        #agrega un satellite y una funcion de inclusion
        self.satellite[len(satellite)].append(satellite)
        self.graph.add_node(satellite)
        self.add_arrow(inclusion)
    
    def add_arrow(self,arrow):
        assert self.graph.has_node(arrow.source) and self.graph.has_node(arrow.target)
        duplicate = self.__find_arrow(arrow)
        if duplicate:
            print "esa flecha ya estaba! capaz con otro tipo?"
            if type(arrow) < type(duplicate): # el min es el tipo de morfismo mas restrictivo
                print "queda el %s" % type(arrow)
                self.graph.remove_edge(duplicate.source,duplicate.target,hash(duplicate))
                self.graph.add_edge(arrow.source,arrow.target,key=hash(arrow),arrow=arrow)
        else:
            self.graph.add_edge(arrow.source,arrow.target,key=hash(arrow),arrow=arrow)
    
    def add_arrows(self,arrows):
        for arrow in arrows:
            self.add_arrow(arrow)
            
    def __find_arrow(self,arrow):
        if self.graph.has_edge(arrow.source,arrow.target,key=hash(arrow)):
            return self.graph[arrow.source][arrow.target][hash(arrow)]["arrow"]
        else:
            return None
        
    def find_arrows(self, source, target, morphtype=None):
        if self.graph.has_edge(source,target):
            result = [x["arrow"] for x in self.graph[source][target].values()]
            if morphtype:
                result = filter(lambda x: isinstance(x,morphtype),result)
            return result
        else:
            return []
        
        
    def show(self):
        import networkx as nx
        G = self
        archivo = "constellation"
        pos=nx.graphviz_layout(G,prog='dot',args='')
        plt.figure(figsize=(8,8))
        #nombres = {tuple(k):back(na[k][1]) for k in na}
        #edge_labels=nx.draw_networkx_edge_labels(G,pos,edge_labels=nombres,label_pos=0.8)
        nx.draw(G,pos,node_size=200,alpha=1,node_color="white", with_labels=True)
        plt.axis('equal')
        plt.savefig('%s.png' % archivo)
        plt.show()

