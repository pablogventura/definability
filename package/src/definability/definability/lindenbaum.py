from itertools import product, chain

from ..functions.morphisms import Homomorphism, Isomorphism
from ..definability.newconstellation2 import Model_Family
from ..misc.misc import powerset
from ..first_order.fofunctions import FO_Relation
from ..definability import morphsgenerators
from datetime import datetime

from collections import defaultdict

def open_definable_lindenbaum(k, arity, subtype):
    morphisms = chain(morphsgenerators.k_isos_no_auts(k, subtype),morphsgenerators.k_sub_isos(k, subtype))
    return lindenbaum_algebra(k, arity, morphisms)

def open_positive_lindenbaum(k, arity, subtype):
    morphisms = chain(morphsgenerators.k_isos_no_auts(k, subtype),morphsgenerators.k_sub_homs(k, subtype))
    return lindenbaum_algebra(k, arity, morphisms)

def existential_lindenbaum(k, arity, subtype):
    morphisms = chain(morphsgenerators.k_isos_no_auts(k, subtype),morphsgenerators.k_embs(k, subtype))
    return lindenbaum_algebra(k, arity, morphisms)

def existential_positive_lindenbaum(k, arity, subtype):
    morphisms = chain(morphsgenerators.k_isos_no_auts(k, subtype),morphsgenerators.k_sub_homs(k, subtype))
    return lindenbaum_algebra(k, arity, morphisms)

def definable_lindenbaum(k, arity, subtype):
    morphisms = chain(morphsgenerators.k_isos_no_auts(k, subtype),morphsgenerators.k_isos(k, subtype))
    return lindenbaum_algebra(k, arity, morphisms)

def lindenbaum_algebra(k, arity, morphisms):
    """
    Satura a k por un conjunto de flechas
    Devuelve los join irreducibles del algebra de lindenbaum
    de aridad dada para la familia K, con las flechas en morphisms.
    >>> from definability.examples import examples
    >>> from definability.definability import newconstellation2
    >>> k=newconstellation2.Model_Family({examples.retrombo, examples.rettestlinden2})
    >>> len(lindenbaum_algebra(k,2,morphsgenerators.k_embs(k,examples.tiporet)))
    17
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


def closure(t, arrows):
    """
    Calcula la clausura de la tupla (o lista de tuplas) t para todo el grupo de flechas.
    """
    result = [t]

    checked = []

    while len(result) != len(checked):
        for t in result:
            if t not in checked:
                for i in arrows:
                    try:
                        it = i.vector_call(t)
                    except ValueError:
                        # no estaba en el dominio
                        continue
                    if it not in result:
                        result.append(it)
                checked.append(t)
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

if __name__ == "__main__":
    import doctest
    doctest.testmod()
