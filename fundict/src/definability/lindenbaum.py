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

def ji_of_existencial_positive_definable_algebra(constellation, subtype, arity):
    """
    Devuelve los atomos del algebra de relaciones de cierta aridad con el subtipo,
    en la constelacion que DEBE TENER UN SOLO PLANETA
    """
    constellation.is_existential_positive_definable(subtype,subtype)
    
    mainsatellite, = constellation.main_satellites(subtype)
    singuletes = map(lambda x: tuple(x),list(product(mainsatellite.universe,repeat=arity)))
    
    result = []
    
    endos = constellation.arrows(mainsatellite,mainsatellite,morphtype=Homomorphism)
    
    for k in singuletes:
        result.append(closure(k,endos))
    
    return join_irreducibles(result)

def atoms_of_open_definable_algebra(constellation, subtype, arity):
    """
    Devuelve los atomos del algebra de relaciones de cierta aridad con el subtipo,
    en la constelacion que DEBE TENER UN SOLO PLANETA
    """
    constellation.is_open_definable(subtype,subtype)
    
    mainsatellite, = constellation.main_satellites(subtype)

    singuletes = map(lambda x: tuple(x),list(product(mainsatellite.universe,repeat=arity)))
    
    result = []
    
    isos = list(constellation.iter_arrows(subtype,morphtype=Isomorphism))
    
    while singuletes:
        k = singuletes[0]
        result.append(closure(k,isos))
        for t in result[-1]:
            singuletes.remove(t)
    
    return result

def ji_of_open_positive_definable_algebra(constellation, subtype, arity):
    """
    Devuelve los atomos del algebra de relaciones de cierta aridad con el subtipo,
    en la constelacion que DEBE TENER UN SOLO PLANETA
    """
    constellation.is_positive_open_definable(subtype,subtype)
    
    mainsatellite, = constellation.main_satellites(subtype)
    singuletes = map(lambda x: tuple(x),list(product(mainsatellite.universe,repeat=arity)))
    
    result = []
    
    homos = list(constellation.iter_arrows(subtype,morphtype=Homomorphism))
    
    for k in singuletes:
        result.append(closure(k,homos))
    
    return join_irreducibles(result)

def join_irreducibles(lst):
    """
    Dada una lista de listas, devuelve una lista dejando solo las que son join-irreducibles
    """
    result = []
    for s in lst:
        s = list(set(s))
        sf = [False] * len(s)
        if s and s not in result: # el vacio no va
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
                    try:
                        it = i.vector_call(t)
                    except ValueError:
                        # no estaba en el dominio
                        continue
                    if it not in result:
                        result.append(it)
                checked.append(t)
    return result

def older_existencial_positive_definable_algebra(constellation, subtype, arity):
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
            if s and s not in result: # el vacio no va
                result.append(s)

    return result

def old_ji_of_existencial_positive_definable_algebra(constellation, subtype, arity):
    """
    Devuelve todas las relaciones de una cierta aridad definibles por una formula existencial
    positiva en el tipo subtype en el unico planeta de constellation.
    usando el algoritmo que va filtrando las que no son ji.
    """
    at = atoms_of_existencial_definable_algebra(constellation, subtype, arity)
    constellation.is_existential_positive_definable(subtype,subtype)

    mainsatellite, = constellation.main_satellites(subtype)

    result = []
    
    #endos = filter(lambda x: not isinstance(x, Isomorphism), constellation.arrows(mainsatellite,mainsatellite,morphtype=Homomorphism))
    endos = constellation.arrows(mainsatellite,mainsatellite,morphtype=Homomorphism)
    jjj= 2**len(at)
    for cant,s in enumerate(powerset(at)):
        s = list(set(reduce(lambda x,y:x+y, s, [])))
        print "%s porciento (%s de %s)" % (float(cant)/jjj, cant, jjj)
        print s
        if is_closed(s, endos):
            s = list(set(s))
            sf = [False] * len(s)
            if s and s not in result: # el vacio no va
                for ji in result:
                    if set(ji).issubset(set(s)):
                        for i in range(len(s)):
                            if s[i] in ji:
                                sf[i] = True
                if not all(sf):                
                    result.append(s)
    return result

