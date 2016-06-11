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
    >>> FO_Type({'+': 2},{'<': 2}) + FO_Type({'-': 2},{'<=': 2})
    FO_Type({'+': 2, '-': 2},{'<=': 2, '<': 2})
    >>> FO_Type({'+': 2, '-': 2},{'<=': 2, '<': 2}) - FO_Type({'-': 2},{'<=': 2})
    FO_Type({'+': 2},{'<': 2})
    """

    def __init__(self, operations, relations):
        self.operations = operations
        self.relations = relations

    def copy(self):
        return FO_Type(self.operations.copy(), self.relations.copy())

    def __repr__(self):
        return "FO_Type(%s,%s)" % (repr(self.operations), repr(self.relations))

    def __eq__(self, other):
        return self.operations == other.operations and self.relations == other.relations

    def __ne__(self, other):
        return not self.__eq__(other)

    def subtype(self, operations, relations):
        return FO_Type({op: self.operations[op] for op in operations}, {rel: self.relations[rel] for rel in relations})

    def is_subtype_of(self, supertype):
        result = all(op in supertype.operations and self.operations[
                     op] == supertype.operations[op] for op in self.operations)
        result = result and all(rel in supertype.relations and self.relations[
                                rel] == supertype.relations[rel] for rel in self.relations)
        return result

    def __sub__(self, other):
        """
        Resta de tipos, devuelve un nuevo tipo con las rel/op que pertenecen a self, pero no a other.
        """
        assert other.is_subtype_of(self), (self,other)
        result = self.copy()
        for op in other.operations:
            del result.operations[op]
        for rel in other.relations:
            del result.relations[rel]
        return result

    def __add__(self, other):
        """
        Suma de tipos, genera un tipo por union de los diccionarios.
        """
        result = self.copy()
        for rel in other.relations:
            assert rel not in result.relations, (rel, self, other)
            result.relations[rel] = other.relations[rel]
        for op in other.operations:
            assert op not in result.operations
            result.operations[op] = other.operations[op]
        return result
    def __hash__(self):
        return hash((tuple(self.operations.items()), tuple(self.relations.items())))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
