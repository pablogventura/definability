from itertools import product, chain

from ..functions.morphisms import Homomorphism, Isomorphism
from ..definability.newconstellation2 import Model_Family
from ..misc.misc import powerset
from ..first_order.fofunctions import FO_Relation
from ..first_order.model import FO_Model
from ..first_order.fotype import FO_Type
from ..definability import morphsgenerators
from datetime import datetime
from ..misc.misc import indent
import itertools

from collections import defaultdict, UserDict

def include_inverses(morphisms):
    """
    Iterador que devuelve cada vez que puede el inverso del morfismo
    """
    for h in morphisms:
        yield h
        if h.inj:
            yield h.inverse()

def open_definable_lindenbaum(k, arity, subtype):
    """
    >>> from definability.examples import examples
    >>> from definability.definability import newconstellation2
    >>> k=newconstellation2.Model_Family({examples.retrombo, examples.rettestlinden2})
    >>> len(open_definable_lindenbaum(k,2,examples.tiporet))
    4
    """
    morphisms = include_inverses(chain(morphsgenerators.k_isos_no_auts(k, subtype),morphsgenerators.k_sub_isos(k, subtype)))
    return lindenbaum_algebra(k, arity, morphisms)

def open_positive_lindenbaum(k, arity, subtype):
    """
    >>> from definability.examples import examples
    >>> from definability.definability import newconstellation2
    >>> k=newconstellation2.Model_Family({examples.retrombo, examples.rettestlinden2})
    >>> len(open_positive_lindenbaum(k,2,examples.tiporet))
    2
    """
    morphisms = include_inverses(chain(morphsgenerators.k_isos_no_auts(k, subtype),morphsgenerators.k_sub_homs(k, subtype)))
    return lindenbaum_algebra(k, arity, morphisms)

def existential_lindenbaum(k, arity, subtype):
    """
    >>> from definability.examples import examples
    >>> from definability.definability import newconstellation2
    >>> k=newconstellation2.Model_Family({examples.retrombo, examples.rettestlinden2})
    >>> len(existential_lindenbaum(k,2,examples.tiporet))
    17
    """
    morphisms = include_inverses(chain(morphsgenerators.k_isos_no_auts(k, subtype),morphsgenerators.k_embs(k, subtype)))
    return lindenbaum_algebra(k, arity, morphisms)

def existential_positive_lindenbaum(k, arity, subtype):
    """
    >>> from definability.examples import examples
    >>> from definability.definability import newconstellation2
    >>> k=newconstellation2.Model_Family({examples.retrombo, examples.rettestlinden2})
    >>> len(existential_positive_lindenbaum(k,2,examples.tiporet))
    2
    """
    morphisms = include_inverses(chain(morphsgenerators.k_isos_no_auts(k, subtype),morphsgenerators.k_sub_homs(k, subtype)))
    return lindenbaum_algebra(k, arity, morphisms)

def definable_lindenbaum(k, arity, subtype):
    """
    >>> from definability.examples import examples
    >>> from definability.definability import newconstellation2
    >>> k=newconstellation2.Model_Family({examples.retrombo, examples.rettestlinden2})
    >>> len(definable_lindenbaum(k,2,examples.tiporet))
    27
    """
    morphisms = include_inverses(chain(morphsgenerators.k_isos_no_auts(k, subtype),morphsgenerators.k_isos(k, subtype)))
    return lindenbaum_algebra(k, arity, morphisms)

def lindenbaum_algebra(k, arity, morphisms):
    """
    Satura a k por un conjunto de flechas
    Devuelve los join irreducibles del algebra de lindenbaum
    de aridad dada para la familia K, con las flechas en morphisms.
    """
    # influye muchisimo el orden en que se recorre k!
    assert isinstance(k,Model_Family)

    morphisms = list(morphisms)
    result = []

    singletons =[]
    for m in k:
        for s in product(m.universe, repeat=arity):
            singletons.append((m, tuple(s)))

    while singletons:
        m,a = singletons.pop()
        new = closurem(a, m, k, morphisms)
        result.append(new)
        for ma in new:
            for t in new[ma]:
                if (ma,t) in singletons:
                    singletons.remove((ma,t))

    return result


def closurem(t, m, k, arrows):
    """
    Calcula la clausura de la tupla (o lista de tuplas) t para todo el grupo de flechas.
    TOMA t una tupla, m la estructura a la que pertenece t, k la familia de estructuras
    y arrows las flechas
    """
    result = {a: [] for a in k}
    result[m] = [t]

    checked = defaultdict(list)

    while sum(len(x) for x in result.values()) != sum(len(x) for x in checked.values()):

        for source in result.keys():
            for t in result[source]:
                if t not in checked[source]:
                    for i in (a for a in arrows if a.source.supermodel == source):

                        try:
                            it = i.vector_call(t)
                        except ValueError:
                            # no estaba en el dominio
                            continue
                        if it not in result[i.target.supermodel]:
                            result[i.target.supermodel].append(it)
                            result[i.target.supermodel].sort()
                    checked[source].append(t)
                    checked[source].sort()
    return result


class LindenbaumAlgebra(FO_Model):

    """
    Algebra de Lindenbaum
    """

    def __init__(self, atoms, name=""):
        self.fo_type = FO_Type({'^': 2, 'v': 2},{})
        self.atoms = atoms

        #self.operations = operations
        #self.relations = relations
        self.name = name
    
    @property
    def cardinality(self):
        return 2**len(self.atoms)
    
    @property
    def universe(self):
        atoms = list(self.atoms)
        for i in itertools.product([True,False],repeat=len(atoms)):
            yield list(itertools.compress(atoms,i))
    
    def __repr__(self):
        if self.name:
            return "LindenbaumAlgebra(name= %s)\n" % self.name
        else:
            result = "LindenbaumAlgebra(\n"
            result += indent("atoms= %s,\n" % repr(self.atoms))
            result += indent("cardinality= %s" % repr(self.cardinality))
            return result + ")"

    def homomorphisms_to(self, target, subtype, inj=None, surj=None, without=[]):
        """
        Genera todos los homomorfismos de este modelo a target, en el subtype.

        >>> from definability.examples.examples import *
        >>> len(retrombo.homomorphisms_to(retrombo,tiporet))
        16
        >>> len(retrombo.homomorphisms_to(rettestlinden,tiporet))
        49
        >>> len(rettestlinden.homomorphisms_to(retrombo,tiporet))
        36
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
        y el mismo universo
        """
        if set(self.universe) != set(other.universe):
            return False
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
            def leq(x,y):
                return self.operations["v"](x,y) == y
            self.relations["<="] = FO_Relation(leq, self.universe, arity=2)

    def draw_lattice(self):
        return latticedraw.LatDraw(self)

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
    def __mul__(self, other):
        """
        Calcula el producto entre modelos

        >>> from definability.examples.examples import *
        >>> retcadena2.fo_type = retrombo.fo_type
        >>> j=retcadena2*retrombo
        >>> r=retcadena2**3
        >>> bool(j.is_isomorphic(r,tiporet))
        True
        """
        return FO_Product([self, other])
    
    def __pow__(self, exponent):
        """
        Calcula la potencia de un modelo
        
        >>> from definability.examples.examples import *
        >>> r=retcadena2**2
        >>> bool(r.is_isomorphic(retrombo,tiporet))
        True
        >>> r=posetcadena2**2
        >>> bool(r.is_isomorphic(posetrombo,tipoposet))
        True
        """
        return FO_Product([self] * exponent)

    def continous(self):
        """
        Devuelve un modelo isomorfo pero de universo [0..n]
        """
        translation = list(self.universe)
        universe = list(range(len(translation)))

        operations = {}
        for op in self.operations:
            operations[op] = self.operations[op].rename(translation)
            
        relations = {}
        for rel in self.relations:
            relations[rel] = self.relations[rel].rename(translation)
        
        return (FO_Model(self.fo_type, universe, operations, relations), translation)

        


if __name__ == "__main__":
    import doctest
    doctest.testmod()
