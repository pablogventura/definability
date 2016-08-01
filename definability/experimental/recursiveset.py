#!/usr/bin/env python
# -*- coding: utf8 -*-

import inspect
from itertools import count, cycle

class RecursiveSet(object):
    """
    Clase para crear conjuntos recursivos con una funcion chi
    """
    def __init__(self,f,superset):
        self.f = f
        self.superset= superset
        
    def __contains__(self, item):
        if item not in self.superset:
            return False
        return self.f(item)
    
    def __iter__(self):
        for i in self.superset:
            if self.f(i):
                yield i
                
    def __repr__(self):
        return "{item in %s: %s}" % (self.superset, ("".join(inspect.getsourcelines(self.f)[0])))
    
    def __bool__(self):
        return True
        
def chiSet(superset):
    """
    Decorador para convertir facilmente una funcion
    en un conjunto, usandola como chi
    Necesita un generador del superset, para poder
    iterar sobre el.
    """
    def wrap(f):
        return RecursiveSet(f,superset)
    return wrap

def enumerateSets(*args):
    """
    Dados generadores infinitos, genera la union
    """
    sets = [iter(s) for s in args]
    for s in cycle(sets):
        yield s.__next__()


@chiSet(count(0))
def omega(n):
    """
    Ejemplo del conjunto omega
    """
    return isinstance(n,int) and n>=0



@chiSet(enumerateSets(count(0),count(-1,-1)))
def zeta(n):
    """
    Ejemplo del conjunto zeta
    """
    return isinstance(n,int)
