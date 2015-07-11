import networkx
from model import Model
from misc import *
import minion

class Constellation():
    """
    Maneja una coleccion de modelos relacionados por homomorfismos
    """
    def __init__(self, models):
        self.graph = networkx.DiGraph()
        self.graph.add_nodes_from(models)
    def calculate_substructures(self):
        for model in self.graph.nodes():
            for substr,emb in model.substructures():
                self.graph.add_edge(substr, model, arrow_type = "embedding", arrow=emb)

