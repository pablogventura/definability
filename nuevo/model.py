#!/usr/bin/env python
# -*- coding: utf8 -*-

from itertools import product

from misc import indent, powerset
from morphisms import Embedding
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

    def subuniverse(self,subset,subtype):
        """
        Devuelve el subuniverso generado por subset para el subtype
        y devuelve una lista con otros conjuntos que tambien hubieran
        generado el mismo subuniverso
        
        >>> from examples import *
        >>> retrombo.subuniverse([1],tiporet)
        ([1], [[1]])
        >>> retrombo.subuniverse([2,3],tiporet)
        ([2, 3, 1, 0], [[2, 3], [2, 3, 1], [2, 3, 1, 0]])
        >>> retrombo.subuniverse([2,3],tiporet.subtype(["^"],[]))
        ([2, 3, 0], [[2, 3], [2, 3, 0]])
        """
        result = subset
        result.sort()
        partials = [list(subset)]
        increasing = True
        while increasing:
            increasing = False
            for op in subtype.operations:
                for x in product(result, repeat=self.operations[op].arity()):
                    if self.operations[op](*x) not in result:
                        result.append(self.operations[op](*x))
                        result.sort()
                        partials.append(list(result))
                        increasing = True
            for rel in subtype.relations:
                for x in product(result, repeat=self.relations[rel].arity()):
                    if self.relations[rel](*x) not in result:
                        result.append(self.relations[rel](*x))
                        result.sort()
                        partials.append(list(result))
                        increasing = True
        return (result,partials)
                    
    def subuniverses(self,subtype):
        """
        Generador que va devolviendo los subuniversos.
        Intencionalmente no filtra por isomorfismos.
        """
        result = []
        subsets = powerset(range(self.cardinality))
        print subsets
        for subset in subsets:
            if subset:
                subuniverse,partials = self.subuniverse(subset,subtype)
                print partials
                for partial in partials:
                    try:
                        subsets[subsets.index(partial)]=None
                    except ValueError:
                        pass
                if subuniverse not in result:
                    result.append(subuniverse)
                    yield subuniverse
            
    def substructures(self,subtype):
        """
        Generador que va devolviendo las subestructuras.
        Intencionalmente no filtra por isomorfismos.
        Devuelve una subestructura y un embedding.
        """

        for sub in self.subuniverses(subtype):
            substructure = FO_Model(subtype,len(sub),{op: self.operations[op].restrict(sub) for op in subtype.operations},
                                                     {rel: self.relations[rel].restrict(sub) for rel in subtype.relations})
            emb = Embedding(sub, substructure, self, subtype)
            yield (substructure,emb)


    
    def subuniversesviejo(self):
        """
        Generador que va devolviendo los subuniversos.
        Intencionalmente no filtra por isomorfismos.
        """
        result = []

        for s in powerset(range(self.cardinality)):
            if any(self.operations[op](*param) not in s for op in sorted(self.operations,key=lambda x:self.operations[x].arity()) for param in product(s,repeat=self.operations[op].arity())):
                    continue
            if s != []:
                s.sort()
                yield s
                
        
        
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
