#!/usr/bin/env python
# -*- coding: utf8 -*-
import networkx
from examples import *
from collections import defaultdict
from itertools import product, chain, combinations
from morphisms import Isomorphism, Embedding, Homomorphism
from minion import ParallelMorphMinionSol
from model import FO_Model

def preprocessing(k,subtype,supertype):
    """
    >>> from examples import *
    >>> rettest10.join_to_le()
    >>> rettest102.join_to_le()
    >>> k= {rettest10, rettest102}
    >>> len(k)
    2
    >>> len(preprocessing(k,tiporet, tiporet + tipoposet))
    1
    """
    for (a,b) in combinations(k,2): # nunca con si mismo
        if {a,b} <= k: # si ya lo encontre iso no lo busco de nuevo
            iso = a.is_isomorphic(b,subtype)
            if iso and iso.preserves_type(supertype):
                k.remove(b)
            else:
                return iso
    return k



if __name__ == "__main__":
    import doctest
    doctest.testmod()
