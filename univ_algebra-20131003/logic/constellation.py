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
    def generate(self):
        # asumo que hay un solo modelo original
        model = self.graph.nodes()[0]
        subs = list(model.substructures())
        subs.sort(key=lambda x:len(x[0]))
        subs.pop(-1) # es el mismo "model"
        for substr,emb in subs:
            self.graph.add_edge(substr, model, arrow_type = "embedding", arrow=emb) # agrego el embbeding original
            
                
            
            
    def calculate_substructures(self):
        for model in self.graph.nodes():
            for substr,emb in model.substructures():
                self.graph.add_edge(substr, model, arrow_type = "embedding", arrow=emb)

