from itertools import product

from morphisms import Homomorphism, Isomorphism
from misc import powerset

def atoms_of_existencial_definable_algebra(constellation, subtype, arity):
    """
    Devuelve los atomos del algebra de relaciones de cierta aridad con el subtipo,
    en la constelacion que DEBE TENER UN SOLO PLANETA
    """
    constellation.is_existential_definable(subtype,subtype)
    
    mainsatellite, = constellation.main_satellites(subtype)

    singuletes = map(lambda x: tuple(x),list(product(mainsatellite.universe,repeat=arity)))
    
    result = []
    
    autos = constellation.arrows(mainsatellite,mainsatellite,morphtype=Isomorphism)
    
    while singuletes:
        k = singuletes[0]
        result.append(closure(k,autos))
        for t in result[-1]:
            singuletes.remove(t)
    
    return result
    
def existencial_positive_definable_algebra(constellation, subtype, arity):
    """
    Devuelve todas las relaciones de una cierta aridad definibles por una formula existencial
    positiva en el tipo subtype en el unico planeta de constellation.
    """
    at = atoms_of_existencial_definable_algebra(constellation, subtype, arity)
    constellation.is_existential_positive_definable(subtype,subtype)

    mainsatellite, = constellation.main_satellites(subtype)

    result = []
    
    #endos = filter(lambda x: not isinstance(x, Isomorphism), constellation.arrows(mainsatellite,mainsatellite,morphtype=Homomorphism))
    endos = constellation.arrows(mainsatellite,mainsatellite,morphtype=Homomorphism)

    for s in powerset(at):
        s = list(set(reduce(lambda x,y:x+y, s, [])))
        if is_closed(s, endos):
            s = set(s)
            if s not in result:
                result.append(s)

    return result

def ji_of_existencial_positive_definable_algebra(constellation, subtype, arity):
    """
    Devuelve las relaciones join-irreducibles del casireticulado de relaciones
    existencial-positivo definibles.
    """
    # lplus lleva las relaciones definibles por existenciales positivas
    lplus = map(set,sorted(existencial_positive_definable_algebra(constellation, subtype, arity),key=len)[1:])
    join_irreducibles = filter(lambda e: len(e) == len(lplus[0]), lplus) # el conjunto de los minimales es j-irre
    
    for rel in lplus:
        for ji in join_irreducibles:
            if rel not in join_irreducibles:
                if not rel.issuperset(ji) or (rel-ji) not in lplus:
                    join_irreducibles.append(rel)
                    print join_irreducibles[-1]
        print rel
    return join_irreducibles
    
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

def closure(t,arrows):
    """
    Calcula la clausura de la tupla (o lista de tuplas) t para todo el grupo de flechas.
    """
    if isinstance(t,list):
        result = t
    else:
        result = [t]
    checked = []

    while len(result) != len(checked):
        for t in result:
            if t not in checked:
                for i in arrows:
                    it = i.vector_call(t)
                    if it not in result:
                        result.append(it)
                checked.append(t)
    return result


    
    
