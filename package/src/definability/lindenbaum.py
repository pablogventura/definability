from itertools import product

from morphisms import Homomorphism, Isomorphism
from misc import powerset
from fofunctions import FO_Relation
from datetime import datetime

from collections import defaultdict

def saturation(k, arity, morphisms):
    assert len(k) == 1
    k = list(k)[0]
    morphisms = list(morphisms)
    singletons = list(map(tuple, list(product(k.universe, repeat=arity))))
    result = []

    while singletons:
        a = singletons.pop()
        result.append(closure(a, morphisms))
        for t in result[-1]:
            if t in singletons:
                singletons.remove(t)
    
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



if __name__ == "__main__":
    import examples
    import newconstellation2
    k={examples.retrombo}
    for r in saturation(k,2,newconstellation2.k_embs(k,examples.tiporet)):
        print(r)

    import doctest
    doctest.testmod()
