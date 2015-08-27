#!/usr/bin/env python
# -*- coding: utf8 -*-

from functions import Function

class FO_OpRel(Function):
    """
    Clase general de las operaciones y relaciones de primer orden
    """
    def __init__(self, l):
        super(FO_OpRel, self).__init__(l)

class FO_Operation(FO_OpRel):
    r"""
    Operacion de primer orden
    
    >>> from fotype import FO_Type
    >>> sum = FO_Operation([[0,1,2],[1,2,0],[2,0,1]])
    >>> sum(2,2)
    1
    >>> sum.table()
    [[0, 0, 0], [0, 1, 1], [0, 2, 2], [1, 0, 1], [1, 1, 2], [1, 2, 0], [2, 0, 2], [2, 1, 0], [2, 2, 1]]
    """
    def __init__(self, l):
        super(FO_Operation, self).__init__(l)
        self.relation = False


class FO_Relation(FO_OpRel):
    r"""
    Relacion de primer orden
    
    >>> from fotype import FO_Type
    >>> par = FO_Relation([1,0,1,0,1])
    >>> par(2)
    1
    >>> par(3)
    0
    >>> par.table()
    [[0], [2], [4]]
    """
    def __init__(self, l):
        super(FO_Relation, self).__init__(l)
        self.relation = True








if __name__ == "__main__":
    import doctest
    doctest.testmod()
