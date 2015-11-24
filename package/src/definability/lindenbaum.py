from itertools import product, imap

from morphisms import Homomorphism, Isomorphism
from misc import powerset
from fofunctions import FO_Relation
from preorder import preorder_to_poset
from datetime import datetime


def atoms_of_existencial_definable_algebra(constellation, subtype, arity):
    """
    Devuelve los atomos del algebra de relaciones de cierta aridad con el subtipo,
    en la constelacion que DEBE TENER UN SOLO PLANETA
    >>> import constellation, examples
    >>> c = constellation.Constellation(examples.retrombo)
    >>> atoms_of_existencial_definable_algebra(c,examples.tiporet,2)
    [Relation(
      [0, 0],
    ), Relation(
      [0, 1],
    ), Relation(
      [0, 2],
      [0, 3],
    ), Relation(
      [1, 0],
    ), Relation(
      [1, 1],
    ), Relation(
      [1, 2],
      [1, 3],
    ), Relation(
      [2, 0],
      [3, 0],
    ), Relation(
      [2, 1],
      [3, 1],
    ), Relation(
      [2, 2],
      [3, 3],
    ), Relation(
      [2, 3],
      [3, 2],
    )]
    """
    constellation.is_existential_definable(subtype, subtype)

    mainsatellite, = constellation.main_satellites(subtype)

    singletons = map(
        tuple, list(product(mainsatellite.universe, repeat=arity)))

    result = []

    autos = constellation.arrows(
        mainsatellite, mainsatellite, morphtype=Isomorphism)

    while singletons:
        k = singletons[0]
        result.append(closure(k, autos))
        for t in result[-1]:
            singletons.remove(t)

    return lists_to_fo_relations(result, mainsatellite.universe)


def ji_of_existencial_positive_definable_algebra(constellation, subtype, arity):
    """
    Devuelve los atomos del algebra de relaciones de cierta aridad con el subtipo,
    en la constelacion que DEBE TENER UN SOLO PLANETA
    >>> import constellation, examples
    >>> c = constellation.Constellation(examples.retrombo)
    >>> ji_of_existencial_positive_definable_algebra(c,examples.tiporet,2)
    [Relation(
      [0, 0],
      [1, 1],
      [2, 2],
      [3, 3],
    ), Relation(
      [0, 0],
      [0, 1],
      [0, 2],
      [0, 3],
      [1, 1],
      [2, 1],
      [2, 2],
      [3, 1],
      [3, 3],
    ), Relation(
      [0, 0],
      [1, 0],
      [1, 1],
      [1, 2],
      [1, 3],
      [2, 0],
      [2, 2],
      [3, 0],
      [3, 3],
    ), Relation(
      [0, 0],
      [0, 1],
      [0, 2],
      [0, 3],
      [1, 0],
      [1, 1],
      [1, 2],
      [1, 3],
      [2, 0],
      [2, 1],
      [2, 2],
      [2, 3],
      [3, 0],
      [3, 1],
      [3, 2],
      [3, 3],
    )]
    """
    constellation.is_existential_positive_definable(subtype, subtype)

    mainsatellite, = constellation.main_satellites(subtype)
    singletons = imap(
        tuple, product(mainsatellite.universe, repeat=arity))

    endos = constellation.arrows(
        mainsatellite, mainsatellite, morphtype=Homomorphism)

    result = []
        
    for k in singletons:
        c = set(closure(k,endos)) # para poder comparar
        if c not in result:
            result.append(c)
    return lists_to_fo_relations(result, mainsatellite.universe)


def new_ji_of_existencial_positive_definable_algebra(atomos, constellation, subtype):
    # TODO emprolijar muchisimo!
    tack = datetime.now()
    atomos = map(lambda x: map(tuple, x), atomos)

    constellation.is_existential_positive_definable(subtype, subtype)

    result = []
    mainsatellite, = constellation.main_satellites(subtype)
    endos = constellation.arrows(
        mainsatellite, mainsatellite, morphtype=Homomorphism)

    drep = {a[0]:i for i,a in enumerate(atomos)}
    le = lambda x,y: any(h.vector_call(y)==x for h in endos)
    teck = datetime.now()
    print "tomo %s segundos" % (teck-tack).total_seconds()
    rel,equi = preorder_to_poset(drep.keys(),le,atomos[0][0])
    tick = datetime.now()
    print "tomo %s segundos" % (tick-teck).total_seconds()
    ji=list(atomos)
    for k in equi.keys():
        for v in equi[k]:
            ji[drep[k]] += atomos[drep[v]]
            ji[drep[v]] = None
    new_rel = []
    for (a,b) in rel:
        new_rel.append((ji[drep[a]],ji[drep[b]]))
    ji = filter(lambda x: x is not None, ji)
    ji = map(tuple,ji)
    new_rel=map(lambda x:tuple(map(tuple,x)),new_rel)
    tock = datetime.now()
    print "tomo %s segundos" % (tock-tick).total_seconds()
    return ji,new_rel    
        
        


def atoms_of_open_definable_algebra(constellation, subtype, arity):
    """
    Devuelve los atomos del algebra de relaciones de cierta aridad con el subtipo,
    en la constelacion que DEBE TENER UN SOLO PLANETA
    >>> import constellation, examples
    >>> c = constellation.Constellation(examples.retrombo)
    >>> atoms_of_open_definable_algebra(c,examples.tiporet,2)
    [Relation(
      [0, 0],
    ), Relation(
      [0, 1],
    ), Relation(
      [0, 2],
      [0, 3],
    ), Relation(
      [1, 0],
    ), Relation(
      [1, 1],
    ), Relation(
      [1, 2],
      [1, 3],
    ), Relation(
      [2, 0],
      [3, 0],
    ), Relation(
      [2, 1],
      [3, 1],
    ), Relation(
      [2, 2],
      [3, 3],
    ), Relation(
      [2, 3],
      [3, 2],
    )]
    """
    constellation.is_open_definable(subtype, subtype)

    mainsatellite, = constellation.main_satellites(subtype)

    singletons = map(
        tuple, list(product(mainsatellite.universe, repeat=arity)))

    result = []

    isos = list(constellation.iter_arrows(subtype, morphtype=Isomorphism))

    while singletons:
        k = singletons[0]
        result.append(closure(k, isos))
        for t in result[-1]:
            singletons.remove(t)

    return lists_to_fo_relations(result, mainsatellite.universe)


def ji_of_open_positive_definable_algebra(constellation, subtype, arity):
    """
    Devuelve los atomos del algebra de relaciones de cierta aridad con el subtipo,
    en la constelacion que DEBE TENER UN SOLO PLANETA
    >>> import constellation, examples
    >>> c = constellation.Constellation(examples.retrombo)
    >>> ji_of_open_positive_definable_algebra(c,examples.tiporet,2)
    [Relation(
      [0, 0],
      [1, 1],
      [2, 2],
      [3, 3],
    ), Relation(
      [0, 0],
      [0, 1],
      [0, 2],
      [0, 3],
      [1, 1],
      [2, 1],
      [2, 2],
      [3, 1],
      [3, 3],
    ), Relation(
      [0, 0],
      [1, 0],
      [1, 1],
      [1, 2],
      [1, 3],
      [2, 0],
      [2, 2],
      [3, 0],
      [3, 3],
    ), Relation(
      [0, 0],
      [0, 1],
      [0, 2],
      [0, 3],
      [1, 0],
      [1, 1],
      [1, 2],
      [1, 3],
      [2, 0],
      [2, 1],
      [2, 2],
      [2, 3],
      [3, 0],
      [3, 1],
      [3, 2],
      [3, 3],
    )]
    """
    constellation.is_positive_open_definable(subtype, subtype)

    mainsatellite, = constellation.main_satellites(subtype)
    singletons = map(
        tuple, list(product(mainsatellite.universe, repeat=arity)))

    result = []

    homos = list(constellation.iter_arrows(subtype, morphtype=Homomorphism))

    for k in singletons:
        result.append(closure(k, homos))

    return lists_to_fo_relations(join_irreducibles(result), mainsatellite.universe)


def join_irreducibles(lst):
    """
    Dada una lista de listas, devuelve una lista dejando solo las que son join-irreducibles
    >>> join_irreducibles([[1,2],[2,3],[1,2,3],[1,2,3,4]])
    [[1, 2], [2, 3], [1, 2, 3, 4]]
    """
    result = []
    for s in lst:
        s = list(set(s))
        sf = [False] * len(s)
        if s and s not in result:  # el vacio no va
            for ji in result:
                if set(ji).issubset(set(s)):
                    for i in range(len(s)):
                        if s[i] in ji:
                            sf[i] = True
            if not all(sf):
                result.append(s)
    return result


def is_closed(l, arrows):
    """
    Devuelve si la lista de tuplas es cerrada bajo las flechas
    """
    result = l
    checked = []

    while len(result) != len(checked):
        for t in result:
            if t not in checked:
                for i in arrows:
                    it = i.vector_call(t)
                    if it not in result:
                        return False
                checked.append(t)
    return True


def closure(t, arrows):
    """
    Calcula la clausura de la tupla (o lista de tuplas) t para todo el grupo de flechas.
    """
    if isinstance(t, list):
        result = t
    else:
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


def lists_to_fo_relations(lst, d_universe):
    result = []
    for l in lst:
        result.append(FO_Relation({tuple(k): True for k in l}, d_universe))
    return result


def sets_to_poset(lst):
    """
    Convierte una lista de conjuntos en un poset por la inclusion.
    """
    from sage.combinat.posets.posets import Poset
    # lista de tuplas de tuplas.
    sets = map(lambda l: tuple(map(tuple, l)), lst)
    return Poset((sets, lambda x, y: set(x) <= set(y)))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
