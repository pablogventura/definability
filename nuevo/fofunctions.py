#!/usr/bin/env python
# -*- coding: utf8 -*-
from functions import Function

class FO_OpRel(Function):
    """
    Clase general de las operaciones y relaciones de primer orden
    """
    def __init__(self, l, fo_type, symbol):
        super(FO_OpRel, self).__init__(l)
        self.fo_type = fo_type
        self.symbol = symbol

class FO_Operation(FO_OpRel):
    r"""
    Operacion de primer orden
    
    >>> from fotype import FO_Type
    >>> sum = FO_Operation([[0,1,2],[1,2,0],[2,0,1]],FO_Type({"+":2},{"<":2}),"+")
    >>> sum(2,2)
    1
    >>> sum.table()
    [[0, 0, 0], [0, 1, 1], [0, 2, 2], [1, 0, 1], [1, 1, 2], [1, 2, 0], [2, 0, 2], [2, 1, 0], [2, 2, 1]]
    >>> sum.minion_table()
    '+ 9 3\n0 0 0\n0 1 1\n0 2 2\n1 0 1\n1 1 2\n1 2 0\n2 0 2\n2 1 0\n2 2 1\n'
    """
    def __init__(self, l, fo_type, symbol):
        super(FO_Operation, self).__init__(l, fo_type, symbol)
        assert self.fo_type.operations[symbol] == self.arity()
        self.relation = False
    def minion_table(self):
        return super(FO_Operation, self).minion_table(self.symbol)

class FO_Relation(FO_OpRel):
    r"""
    Relacion de primer orden
    
    >>> from fotype import FO_Type
    >>> par = FO_Relation([1,0,1,0,1],FO_Type({"+":2},{"p":1}),"p")
    >>> par(2)
    1
    >>> par(3)
    0
    >>> par.table()
    [[0], [2], [4]]
    >>> par.minion_table()
    'p 3 1\n0\n2\n4\n'
    """
    def __init__(self, l, fo_type, symbol):
        super(FO_Relation, self).__init__(l, fo_type, symbol)
        assert self.fo_type.relations[symbol] == self.arity()
        self.relation = True
    def __call__(self, *args):
        return bool(super(FO_Relation, self).__call__(*args))
    def minion_table(self):
        return super(FO_Relation, self).minion_table(self.symbol)










if __name__ == "__main__":
    import doctest
    doctest.testmod()
