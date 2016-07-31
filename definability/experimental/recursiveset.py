import inspect
from itertools import count, cycle

class RecursiveSet(object):
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
    def wrap(f):
        return RecursiveSet(f,superset)
    return wrap

def enumerateSets(*args):
    sets = [iter(s) for s in args]
    for s in cycle(sets):
        yield s.__next__()


@chiSet(count(0))
def omega(n):
    return isinstance(n,int) and n>=0



@chiSet(enumerateSets(count(0),count(-1,-1)))
def zeta(n):
    return isinstance(n,int)
