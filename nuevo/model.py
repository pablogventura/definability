#!/usr/bin/env python
# -*- coding: utf8 -*-

from misc import indent
import minion

class FO_Model(object):
    """
    Modelos de algun tipo de primer orden.
    """
    def __init__(self,fo_type, cardinality, operations, relations, universe=None):
        self.fo_type = fo_type
        self.cardinality = cardinality
        self.universe = universe # TODO en el futuro universe podria manejar renombres, para que los elementos puedan ser cualquier cosa
        assert sorted(operations.keys()) == sorted(fo_type.operations.keys()), "Estan mal definidas las funciones"
        assert sorted(relations.keys()) == sorted(fo_type.relations.keys()), "Estan mal definidas las relaciones"
        self.operations = operations
        self.relations = relations
        
    def __repr__(self):
        result = "FO_Model(\n"
        result += indent(repr(self.fo_type) + ",\n")
        result += indent(repr(self.cardinality) + ",\n")
        result += indent(repr(self.operations) + ",\n")
        result += indent(repr(self.relations))
        return result + ")"
        
    def homomorphisms_to(self, target, subtype):
        """
        Genera todos los homomorfismos de este modelo a target, en el subtype.
        """
        return minion.homomorphisms(self,target,subtype)
    
    def embeddings_to(self, target, subtype):
        """
        Genera todos los embeddings de este modelo a target, en el subtype.
        """
        return minion.embeddings(self,target,subtype)
        
    def isomorphisms_to(self, target, subtype):
        """
        Genera todos los isomorfismos de este modelo a target, en el subtype.
        """
        return minion.isomorphisms(self,target,subtype)

    def is_homomorphic_image(self, target, subtype):
        """
        Si existe, devuelve un homomorfismo de este modelo a target, en el subtype;
        Si no, devuelve False
        """
        return minion.is_homomorphic_image(self, target, subtype)
        
    def is_substructure(self, target, subtype):
        """
        Si existe, devuelve un embedding de este modelo a target, en el subtype;
        Si no, devuelve False
        """
        return minion.is_substructure(self, target, subtype)
        
    def is_isomorphic(self, target, subtype):
        """
        Si existe, devuelve un isomorfismo de este modelo a target, en el subtype;
        Si no, devuelve False
        """
        return minion.is_isomorphic(self, target, subtype)
        
        
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
