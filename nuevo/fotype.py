#!/usr/bin/env python
# -*- coding: utf8 -*-

class FO_Type(object):
    """
    Maneja tipos de primer orden:
    Teoricamente es una 4-upla (C,F,R,a)
    Toma dos diccionarios con nombres y aridades
    
    >>> t = FO_Type({"+":2},{"<":2})
    >>> t
    FO_Type({'+': 2},{'<': 2})
    """
    def __init__(self,operations,relations):
        self.operations = operations
        self.relations = relations
    def __repr__(self):
        return "FO_Type(%s,%s)"%(repr(self.operations),repr(self.relations))

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
