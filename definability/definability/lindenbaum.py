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

def open_definable_lindenbaum_special(k, arity, subtype,morphs=None):
    """
    >>> from definability.examples import examples
    >>> from definability.definability import newconstellation2
    >>> k=newconstellation2.Model_Family({examples.retrombo, examples.rettestlinden2})
    >>> len(open_definable_lindenbaum(k,2,examples.tiporet))
    4
    """
    return lindenbaum_algebra_special(k, arity, include_inverses(morphs))

def lindenbaum_algebra_special(k, arity, morphisms):
    """
    Satura a k por un conjunto de flechas
    Devuelve los join irreducibles del algebra de lindenbaum
    de aridad dada para la familia K, con las flechas en morphisms.
    """
    from .unionfind import UnionFind
    assert isinstance(k,FO_Model)

    morphisms = list(morphisms)
    assert all(isinstance(i,Isomorphism) for i in morphisms)
    
    result = []
    nodes = list(product(k.universe, repeat=arity))
    uf = UnionFind()
    uf.insert_objects(nodes)

    for u in nodes:
        for m in morphisms:
            try:
                v = m.vector_call(u)
            except ValueError:
                # no estaba en el dominio
                continue
            if uf.find(u)!=uf.find(v):
                uf.union(u,v)  

    return uf.to_list()

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



        


if __name__ == "__main__":
    import doctest
    doctest.testmod()
