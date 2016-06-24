#!/usr/bin/env python
# -*- coding: utf8 -*-

from itertools import product, chain

from ..misc.misc import indent, powerset
from ..functions.morphisms import Embedding
from ..first_order.fofunctions import FO_Relation
from ..interfaces import minion


class FO_Model(object):

    """
    Modelos de algun tipo de primer orden.
    """

    def __init__(self, fo_type, universe, operations, relations):
        self.fo_type = fo_type
        assert not isinstance(universe, int)
        self.universe = universe
        self.cardinality = len(universe)
        assert set(operations.keys()) >= set(
            fo_type.operations.keys()), "Estan mal definidas las funciones"
        assert set(relations.keys()) >= set(
            fo_type.relations.keys()), "Estan mal definidas las relaciones"
        self.operations = operations
        self.relations = relations
        self.supermodel = self

    def __repr__(self):
        result = "FO_Model(\n"
        result += indent(repr(self.fo_type) + ",\n")
        result += indent(repr(self.universe) + ",\n")
        result += indent(repr(self.operations) + ",\n")
        result += indent(repr(self.relations))
        return result + ")"

    def homomorphisms_to(self, target, subtype, inj=None, surj=None, without=[]):
        """
        Genera todos los homomorfismos de este modelo a target, en el subtype.
        """
        return minion.homomorphisms(self, target, subtype, inj=inj, surj=surj, without=without)

    def embeddings_to(self, target, subtype, without=[]):
        """
        Genera todos los embeddings de este modelo a target, en el subtype.
        """
        return minion.embeddings(self, target, subtype, without=without)

    def automorphisms(self, subtype, without=[]):
        """
        Genera todos los automorfismos de este modelo, en el subtype.
        """
        return self.isomorphisms_to(self, subtype, without=without)

    def isomorphisms_to(self, target, subtype, without=[]):
        """
        Genera todos los isomorfismos de este modelo a target, en el subtype.
        """
        return minion.isomorphisms(self, target, subtype, without=without)

    def is_homomorphic_image(self, target, subtype, without=[]):
        """
        Si existe, devuelve un homomorfismo de este modelo a target, en el subtype;
        Si no, devuelve False
        """
        return minion.is_homomorphic_image(self, target, subtype, without=without)

    def is_substructure(self, target, subtype, without=[]):
        """
        Si existe, devuelve un embedding de este modelo a target, en el subtype;
        Si no, devuelve False
        """
        return minion.is_substructure(self, target, subtype, without=without)

    def is_isomorphic(self, target, subtype, without=[]):
        """
        Si existe, devuelve un isomorfismo de este modelo a target, en el subtype;
        Si no, devuelve False
        """
        return minion.is_isomorphic(self, target, subtype, without=without)

    def is_isomorphic_to_any(self, targets, subtype, without=[]):
        """
        Si lo es, devuelve el primer isomorfismo encontrado desde este modelo a alguno en targets, en el subtype;
        Si no, devuelve False
        """
        return minion.is_isomorphic_to_any(self, targets, subtype, without=without)

    def subuniverse(self, subset, subtype):
        """
        Devuelve el subuniverso generado por subset para el subtype
        y devuelve una lista con otros conjuntos que tambien hubieran
        generado el mismo subuniverso

        >>> from definability.examples.examples import *
        >>> retrombo.subuniverse([1],tiporet)
        ([1], [[1]])
        >>> retrombo.subuniverse([2,3],tiporet)[0]
        [0, 1, 2, 3]
        >>> retrombo.subuniverse([2,3],tiporet.subtype(["^"],[]))[0]
        [0, 2, 3]
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

        return (result, partials)

    def subuniverses(self, subtype):
        """
        NO DEVUELVE EL SUBUNIVERSO VACIO
        Generador que va devolviendo los subuniversos.
        Intencionalmente no filtra por isomorfismos.

        >>> from definability.examples.examples import *
        >>> list(retrombo.subuniverses(tiporet))
        [[0, 1, 2, 3], [0, 1, 2], [0, 1, 3], [0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [0], [1], [2], [3]]
        >>> list(posetrombo.subuniverses(tipoposet)) # debe dar el conjunto de partes sin el vacio, porque no tiene ops
        [[0, 1, 2, 3], [0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3], [0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3], [0], [1], [2], [3]]
        >>> list(retcadena2.subuniverses(tiporetacotado)) # debe dar todo entero, por las constantes
        [[0, 1]]
        """
        result = []
        subsets = powerset(self.universe)
        checked = [[]]
        for subset in subsets:
            if subset not in checked:
                subuniverse, partials = self.subuniverse(subset, subtype)
                for partial in partials:
                    checked.append(partial)
                if subuniverse not in result:
                    result.append(subuniverse)
                    yield subuniverse

    def restrict(self, subuniverse, subtype):
        """
        Devuelve la restriccion del modelo al subuniverso que se supone que es cerrado en en subtype
        """
        return FO_Submodel(subtype, subuniverse, {op: self.operations[op].restrict(subuniverse) for op in self.operations}, {rel: self.relations[rel].restrict(subuniverse) for rel in self.relations}, self)

    def substructure(self, subuniverse, subtype):
        """
        Devuelve una subestructura y un embedding.
        """
        substructure = self.restrict(subuniverse, subtype)
        emb = Embedding(
            {(k,): k for k in subuniverse}, substructure, self, subtype)
        return (emb, substructure)

    def substructures(self, subtype, without=[]):
        """
        Generador que va devolviendo las subestructuras.
        Intencionalmente no filtra por isomorfismos.
        Devuelve una subestructura y un embedding.
        No devuelve las subestructuras cuyos universos estan en without.

        >>> from definability.examples.examples import *
        >>> len(list(retrombo.substructures(tiporet)))
        12
        >>> len(list(retrombo.substructures(tiporet.subtype(["v"],[])))) # debe dar uno mas por el triangulo de arriba
        13
        >>> len(list(retrombo.substructures(tiporet.subtype([],[])))) # debe dar (2**cardinalidad)-1
        15
        """
        without = list(map(set, without))
        for sub in self.subuniverses(subtype):
            if set(sub) not in without:
                # parece razonable que el modelo de una subestructura conserve todas las relaciones y operaciones
                # independientemente de el subtipo del que se buscan
                # embeddings.
                yield self.substructure(sub, subtype)

    def __eq__(self, other):
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

    def __ne__(self, other):
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
        Solo si no tiene ninguna relacion "<="

        >>> from definability.examples.examples import retrombo
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
        if "<=" not in self.relations:
            result = {}
            for t in self.operations["v"].domain():
                if self.operations["v"](*t) == t[1]:
                    result[t] = 1
                else:
                    result[t] = 0
            self.relations["<="] = FO_Relation(result, self.universe)

    def to_sage_lattice(self):
        """
        Devuelve un reticulado de Sage.
        """
        from sage.combinat.posets.lattices import LatticePoset
        self.join_to_le()
        return LatticePoset((self.universe, self.relations["<="].table()))

    def to_sage_poset(self):
        """
        Devuelve un poset de Sage.
        """
        from sage.combinat.posets.posets import Poset
        return Poset((self.universe, self.relations["<="].table()))

    def diagram(self, c, s=0):
        """
        Devuelve el diagrama de la estructura con el prefijo c y con un
        shift de s.
        """
        result = []
        for x, y in product(self.universe, repeat=2):
            result += ["-(%s%s=%s%s)" % (c, x + s, c, y + s)]
        for op in self.operations:
            if self.operations[op].arity() == 0:
                result += ["(%s=%s%s)" % (op, c, self.operations[op]() + s)]
            else:
                for x, y, z in iter(self.operations[op].table()):
                    result += ["%s%s %s %s%s = %s%s" %
                               (c, x + s, op, c, y + s, c, z + s)]
        for rel in self.relations:
            for x, y in product(self.universe, repeat=2):
                if self.relations[rel](x, y):
                    result += ["(%s%s %s %s%s)" % (c, x + s, rel, c, y + s)]
                else:
                    result += ["-(%s%s %s %s%s)" % (c, x + s, rel, c, y + s)]
        return result

    def __hash__(self):
        """
        Hash para los modelos de primer orden

        >>> from definability.examples.examples import *
        >>> hash(retrombo)==hash(retrombo2)
        False
        >>> from definability.first_order.fotheories import DiGraph
        >>> s=[hash(g) for g in DiGraph.find_models(3)]
        >>> (len(s),len(set(s))) # nunca se repitio un hash
        (103, 103)
        """
        return hash(frozenset(chain([self.fo_type], self.universe, self.operations.items(), self.relations.items())))


class FO_Submodel(FO_Model):

    """
    Submodelos de algun tipo de primer orden.
    """

    def __init__(self, fo_type, universe, operations, relations, supermodel):
        super(FO_Submodel, self).__init__(
            fo_type, universe, operations, relations)
        self.supermodel = supermodel

    def __repr__(self):
        result = "FO_Submodel(\n"
        result += indent(repr(self.fo_type) + ",\n")
        result += indent(repr(self.universe) + ",\n")
        result += indent(repr(self.operations) + ",\n")
        result += indent(repr(self.relations) + ",\n")
        result += indent("supermodel= " + repr(self.supermodel) + "\n")
        return result + ")"

if __name__ == "__main__":
    import doctest
    doctest.testmod()
