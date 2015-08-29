from itertools import imap

import minion
from morphisms import Embedding
from misc import indent


class FO_Substructure(object):
    def __init__(self, model, embedding):
        
        self.model = model
        self.embedding = embedding
        self.inverseembedding = embedding.inverse()
        
    def __repr__(self):
        result = "FO_Substructure(\n"
        result += indent(repr(self.model) + ",\n")
        result += indent(repr(self.embedding))
        return result + ")"
        
    def universe(self):
        """
        Un generador del subuniverso que genera esta subestructura
        """
        return iter(self.embedding)
        
    def homomorphisms_to(self, target, subtype):
        """
        Genera todos los homomorfismos de este modelo a target, en el subtype.
        """
        return imap(lambda g: g.composition(self.inverseembedding), minion.homomorphisms(self.model,target,subtype))
    
    def embeddings_to(self, target, subtype):
        """
        Genera todos los embeddings de este modelo a target, en el subtype.
        """
        return imap(lambda g: g.composition(self.inverseembedding), minion.embeddings(self.model,target,subtype))
        
    def isomorphisms_to(self, target, subtype):
        """
        Genera todos los isomorfismos de este modelo a target, en el subtype.
        """
        return imap(lambda g: g.composition(self.inverseembedding), minion.isomorphisms(self.model,target,subtype))

    def is_homomorphic_image(self, target, subtype):
        """
        Si existe, devuelve un homomorfismo de este modelo a target, en el subtype;
        Si no, devuelve False
        """
        result = minion.is_homomorphic_image(self.model, target, subtype)
        if result:
            return result.composition(self.inverseembedding) 
        else:
            return result
        
    def is_substructure(self, target, subtype):
        """
        Si existe, devuelve un embedding de este modelo a target, en el subtype;
        Si no, devuelve False
        """
        result = minion.is_substructure(self.model, target, subtype)
        if result:
            return result.composition(self.inverseembedding) 
        else:
            return result
        
    def is_isomorphic(self, target, subtype):
        """
        Si existe, devuelve un isomorfismo de este modelo a target, en el subtype;
        Si no, devuelve False
        """
        result = minion.is_isomorphic(self.model, target, subtype)
        if result:
            return result.composition(self.inverseembedding) 
        else:
            return result

