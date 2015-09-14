#!/usr/bin/env python
# -*- coding: utf8 -*-

from itertools import product

from misc import indent, powerset
from morphisms import Embedding
from fofunctions import FO_Relation, FO_Operation
import minion

class FO_Model(object):
    """
    Modelos de algun tipo de primer orden.
    """
    def __init__(self,fo_type, universe, operations, relations):
        self.fo_type = fo_type
        assert not isinstance(universe,int)
        self.universe = universe
        self.cardinality = len(universe)
        assert set(operations.keys()) >= set(fo_type.operations.keys()), "Estan mal definidas las funciones"
        assert set(relations.keys()) >= set(fo_type.relations.keys()), "Estan mal definidas las relaciones"
        self.operations = operations
        self.relations = relations
        
    def __repr__(self):
        result = "FO_Model(\n"
        result += indent(repr(self.fo_type) + ",\n")
        result += indent(repr(self.universe) + ",\n")
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

    def is_isomorphic_to_any(self, targets, subtype):
        """
        Si lo es, devuelve el primer isomorfismo encontrado desde este modelo a alguno en targets, en el subtype;
        Si no, devuelve False
        """
        return minion.is_isomorphic_to_any(self,targets,subtype)

    def subuniverse(self,subset,subtype):
        """
        Devuelve el subuniverso generado por subset para el subtype
        y devuelve una lista con otros conjuntos que tambien hubieran
        generado el mismo subuniverso
        
        >>> from examples import *
        >>> retrombo.subuniverse([1],tiporet)
        ([1], [[1]])
        >>> retrombo.subuniverse([2,3],tiporet)
        ([0, 1, 2, 3], [[2, 3], [1, 2, 3], [0, 1, 2, 3]])
        >>> retrombo.subuniverse([2,3],tiporet.subtype(["^"],[]))
        ([0, 2, 3], [[2, 3], [0, 2, 3]])
        """
        result = subset
        result.sort()
        partials = [list(subset)]
        increasing = True
        while increasing:
            increasing = False
            for op in subtype.operations:
                for x in product(result, repeat=self.operations[op].arity()):
                    elem = self.operations[op](*x)
                    if elem not in result and elem in self.universe:
                        result.append(elem)
                        result.sort()
                        partials.append(list(result))
                        increasing = True

        return (result,partials)
                    
    def subuniverses(self,subtype):
        """
        NO DEVUELVE EL SUBUNIVERSO VACIO
        Generador que va devolviendo los subuniversos.
        Intencionalmente no filtra por isomorfismos.

        >>> from examples import *
        >>> list(retrombo.subuniverses(tiporet))
        [[0], [1], [2], [3], [0, 1], [0, 2], [1, 2], [0, 3], [1, 3], [0, 1, 2, 3], [0, 1, 2], [0, 1, 3]]
        >>> list(posetcadena2.subuniverses(tipoposet)) # debe dar el conjunto de partes sin el vacio, porque no tiene ops
        [[0], [1], [0, 1]]
        """
        result = []
        subsets = powerset(self.universe)
        for subset in subsets:
            if subset:
                subuniverse,partials = self.subuniverse(subset,subtype)
                for partial in partials:
                    try:
                        subsets[subsets.index(partial)]=None
                    except ValueError:
                        pass
                if subuniverse not in result:
                    result.append(subuniverse)
                    yield subuniverse
    def restrict(self,subuniverse, subtype):
        """
        Devuelve la restriccion del modelo al subuniverso que se supone que es cerrado en en subtype
        """
        return FO_Model(subtype,subuniverse,{op:self.operations[op].restrict(subuniverse) for op in self.operations}
                                           ,{rel:self.relations[rel].restrict(subuniverse) for rel in self.relations})
    def substructures(self,subtype):
        """
        Generador que va devolviendo las subestructuras.
        Intencionalmente no filtra por isomorfismos.
        Devuelve una subestructura y un embedding.
        
        >>> from examples import *
        >>> len(list(retrombo.substructures(tiporet)))
        12
        >>> len(list(retrombo.substructures(tiporet.subtype(["v"],[])))) # debe dar uno mas por el triangulo de arriba
        13
        >>> len(list(retrombo.substructures(tiporet.subtype([],[])))) # debe dar (2**cardinalidad)-1
        15
        """

        for sub in self.subuniverses(subtype):
            # parece razonable que el modelo de una subestructura conserve todas las relaciones y operaciones
            # independientemente de el subtipo del que se buscan embeddings.
            substructure = self.restrict(sub,subtype)
            emb = Embedding({(k,):k for k in sub},substructure,self,subtype)
            yield (emb,substructure)

    def __eq__(self,other):
        """
        Para ser iguales tienen que tener el mismo tipo
        y el mismo comportamiento en las operaciones/relaciones del tipo
        """
        if self.fo_type != other.fo_type:
            return False
        for op in self.fo_type.operations:
            if self.operations[op] != other.operations[op]:
                return False
        for rel in self.fo_type.relations:
            if self.relations[rel] != other.relations[rel]:
                return False
        return True
    def __ne__(self,other):
        """
        Triste necesidad para la antiintuitiva logica de python
        'A==B no implica !(A!=B)'
        """
        return not self.__eq__(other)
    def __len__(self):
        return self.cardinality

    def join_to_le(self):
        """
        Genera una relacion <= a partir de v
        
        >>> from examples import retrombo
        >>> del retrombo.relations["<="]
        >>> retrombo.join_to_le()
        >>> retrombo.relations["<="]
        Relation(
          [0, 0],
          [0, 1],
          [0, 2],
          [0, 3],
          [1, 1],
          [2, 1],
          [2, 2],
          [3, 1],
          [3, 3],
        )
        """
        assert "<=" not in self.relations
        result = {}
        for t in self.operations["v"].domain():
            if self.operations["v"](*t) == t[1]:
                result[t] = 1
            else:
                result[t] = 0
        self.relations["<="] = FO_Relation(result)
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
