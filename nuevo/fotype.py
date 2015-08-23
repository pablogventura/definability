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
    >>> st = t.subtype(["+"],[])
    >>> st
    FO_Type({'+': 2},{},supertype=FO_Type({'+': 2},{'<': 2}))
    >>> st.is_subtype_of(t)
    True
    """
    def __init__(self,operations,relations,supertype=None):
        self.operations = operations
        self.relations = relations
        self.supertype = supertype
    def __repr__(self):
        if self.supertype:
            return "FO_Type(%s,%s,supertype=%s)"%(repr(self.operations),repr(self.relations),repr(self.supertype))
        else:
            return "FO_Type(%s,%s)"%(repr(self.operations),repr(self.relations))
    def __eq__(self,other):
        return self.operations == other.operations and self.relations == other.relations
    def subtype(self,operations,relations):
        return FO_Type({op:self.operations[op] for op in operations},{rel:self.relations[rel] for rel in relations},supertype=self)
    def is_subtype_of(self, supertype):
        return self.supertype == supertype

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
