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
    FO_Type({'+': 2},{})
    >>> st.is_subtype_of(t)
    True
    """
    def __init__(self,operations,relations):
        self.operations = operations
        self.relations = relations

    def __repr__(self):
        return "FO_Type(%s,%s)"%(repr(self.operations),repr(self.relations))
    def __eq__(self,other):
        return self.operations == other.operations and self.relations == other.relations
    def subtype(self,operations,relations):
        return FO_Type({op:self.operations[op] for op in operations},{rel:self.relations[rel] for rel in relations})
    def is_subtype_of(self, supertype):
        result = all(op in supertype.operations and self.operations[op] == supertype.operations[op] for op in self.operations)
        result = result and all(rel in supertype.relations and self.relations[rel] == supertype.relations[rel] for rel in self.relations)
        return result


if __name__ == "__main__":
    import doctest
    doctest.testmod()
