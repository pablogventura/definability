from itertools import product
from morphisms import Isomorphism

def existencial_definable_algebra(constellation, subtype, arity):
    """
    Devuelve los atomos del algebra de relaciones de cierta aridad con el subtipo,
    en la constelacion que DEBE TENER UN SOLO PLANETA
    """
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
    


def closure(t,arrows):
    """
    Calcula la clausura de la tupla t para todo el grupo de flechas.
    """
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


    
    
