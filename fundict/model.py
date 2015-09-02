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
        >>> list(retrombo.substructures(tiporet))[3]
        FO_Model(
          FO_Type({'v': 2, '^': 2},{}),
          [3],
          {'Max': Constant(
            1
          ), '^': Function(
            [3, 3] -> 3,
          ), 'Min': Constant(
            0
          ), 'v': Function(
            [3, 3] -> 3,
          )},
          {'P': Relation(
            [3],
          ), '<=': Relation(
            [3, 3],
          )}
        )
        >>> list(retrombo.substructures(tiporet))[2]
        FO_Model(
          FO_Type({'v': 2, '^': 2},{}),
          [2],
          {'Max': Constant(
            1
          ), '^': Function(
            [2, 2] -> 2,
          ), 'Min': Constant(
            0
          ), 'v': Function(
            [2, 2] -> 2,
          )},
          {'P': Relation(
            [2],
          ), '<=': Relation(
            [2, 2],
          )}
        )
        >>> len(list(retrombo.substructures(tiporet))[3].embeddings_to(retrombo,tiporet))
        4
        >>> len(list(retrombo.substructures(tiporet))[3].homomorphisms_to(retrombo,tiporet))
        4
        >>> list(retrombo.substructures(tiporet))[3].is_isomorphic(list(retrombo.substructures(tiporet))[2],tiporet)
        Isomorphism(
          [3] -> 2,
        ,
          FO_Type({'v': 2, '^': 2},{})
        ,
          Injective,
          Surjective,
        )
        >>> list(retrombo.substructures(tiporet))[4].is_isomorphic(list(retrombo.substructures(tiporet))[5],tiporet)
        Isomorphism(
          [0] -> 0,
          [1] -> 2,
        ,
          FO_Type({'v': 2, '^': 2},{})
        ,
          Injective,
          Surjective,
        )
        >>> len(list(retrombo.substructures(tiporet))[4].isomorphisms_to(list(retrombo.substructures(tiporet))[5],tiporet))
        1
        >>> len(list(retrombo.substructures(tiporet))[4].homomorphisms_to(list(retrombo.substructures(tiporet))[5],tiporet))
        3
        """

        for sub in self.subuniverses(subtype):
            # parece razonable que el modelo de una subestructura conserve todas las relaciones y operaciones
            # independientemente de el subtipo del que se buscan embeddings.
            substructure = self.restrict(sub,subtype)
            yield substructure

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
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
