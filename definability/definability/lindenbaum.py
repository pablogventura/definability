from itertools import product, chain

from ..functions.morphisms import Homomorphism, Isomorphism
from ..definability.newconstellation2 import Model_Family
from ..misc.misc import powerset
from ..first_order.fofunctions import FO_Relation
from ..definability import morphsgenerators
from datetime import datetime

from collections import defaultdict

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

class Lindenbaum_Algebra(object):
    def __init__(self, model_family):
        self.d = defaultdict(defaultdict(list))
        self.equivalence = defaultdict(list)

    def add_relation(formula, relations):
        assert isinstance(dict,relations)
        self.d[formula].update(relations)
    
    def finish(self):
        for sf in l[0].subformulas:
            h = [f.subformulas for f in filter(lambda f,sf=sf: sf in f.subformulas, l)]
            result[sf] = set()
            for formulas in h:
                result[sf]=result[sf].intersection(set(formulas))
        
    def __repr__(self):
        pass
        


if __name__ == "__main__":
    import doctest
    doctest.testmod()
