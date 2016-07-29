#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
Genera un modelo de primer orden a partir de un string
"""

from ..first_order.model import FO_Model
from ..first_order.fotype import FO_Type
from ..first_order.fofunctions import FO_Relation, FO_Operation, FO_Constant
import string

tipostring = FO_Type({}, {l:1 for l in string.ascii_uppercase})

def string_model(value):
    """
    Genera un modelo de primer orden de una string
    
    >>> m = string_model("TEST")
    >>> len(m)
    4
    >>> m.relations["T"]
    Relation(
      [0],
      [3],
    )
    >>> m.relations["E"]
    Relation(
      [1],
    )
    >>> m.relations["S"]
    Relation(
      [2],
    )
    """
    if  not(value.isalpha() and value.isupper()):
        raise ValueError("String must be only A..Z")
        
    rel={}
    rel = {l:FO_Relation(lambda i,l=l: value[i]==l, list(range(len(value))),arity=1) for l in string.ascii_uppercase}
        

    return FO_Model(tipostring, list(range(len(value))), {}, rel, name=value)

