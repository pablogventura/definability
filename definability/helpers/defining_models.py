#!/usr/bin/env python
# -*- coding: utf8 -*-

from ..first_order.fofunctions import FO_Relation_decorator
from functools import lru_cache

def leq_from_uc(uc,universe=[]):
    """
    A partir de una lista de covers y un universo
    devuelve la FO_Relation para <=
    """
    if not isinstance(uc, dict):
        uc = {i:v for i,v in enumerate(uc)}
    if not universe:
        universe = set.union(*([set(l) for l in uc.values()]+[uc.keys()]))

    @FO_Relation_decorator(universe,arity=2)
    @lru_cache(maxsize=len(universe)**2, typed=False)
    def leq(x,y):
        l = list(uc[x])
        while l:
            if x==y or y in l:
                return True
            else:
                for z in uc[x]:
                    l+=uc[z]
                x = l.pop()
        return False
            
    return leq
