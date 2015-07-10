import networkx
from model import Model
from misc import *

class Constellation():
    """
    Maneja una coleccion de modelos relacionados por homomorfismos
    """
    def __init__(self, models):
        self.graph = networkx.DiGraph()
        self.graph.add_nodes_from(models)
    def calculate_substructures(self):
        for model in self.graph.nodes_iter():
            pass
            #TODO VOY POR ACA
