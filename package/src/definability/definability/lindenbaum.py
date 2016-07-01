from itertools import product

from ..functions.morphisms import Homomorphism, Isomorphism
from ..misc.misc import powerset
from ..first_order.fofunctions import FO_Relation
from datetime import datetime

from collections import defaultdict


def saturation(k, arity, morphisms):
    # TODO FALTA CORREGIR MUCHO, no pasa los tests, a veces se cuelga
    """
    Satura a k por un conjunto de flechas
    >>> from definability.examples import examples
    >>> from definability.definability import newconstellation2
    >>> k={examples.retrombo, examples.rettestlinden2}
    >>> len(saturation(k,2,newconstellation2.k_embs(k,examples.tiporet)))
    27
    """
    #s = max(k,key=len)
    morphisms = list(morphisms)
    result = []
    for s in k:
        singletons = list(map(tuple, list(product(s.universe, repeat=arity))))

        while singletons:
            a = singletons.pop()
            result.append(closurem(a, s, k, morphisms))
            for t in result[-1][s]:
                if t in singletons:
                    singletons.remove(t)

        #for l in result:
            #result[l]=list(set(result[l]))
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
    # TODO ANDA MEDIO MAL
    # TOMA t una tupla, m la estructura a la que pertenece t, k la familia de
    # estrucutras y arrows las flechas
    """
    Calcula la clausura de la tupla (o lista de tuplas) t para todo el grupo de flechas.
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
