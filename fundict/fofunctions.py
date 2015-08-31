#!/usr/bin/env python
# -*- coding: utf8 -*-

from functions import Function

class FO_OpRel(Function):
    """
    Clase general de las operaciones y relaciones de primer orden
    """
    def __init__(self, d):
        super(FO_OpRel, self).__init__(d)

class FO_Operation(FO_OpRel):
    r"""
    Operacion de primer orden
    """
    def __init__(self, d):
        super(FO_Operation, self).__init__(d)
        self.relation = False


class FO_Relation(FO_OpRel):
    r"""
    Relacion de primer orden
    
    >>> par = FO_Relation({(0,):1,(1,):0,(2,):1,(3,):0,(4,):1})
    >>> par(2)
    True
    >>> par(3)
    False
    >>> par.table()
    [[0], [2], [4]]
    """
    def __init__(self, d):
        super(FO_Relation, self).__init__(d)
        self.relation = True




if __name__ == "__main__":
    import doctest
    doctest.testmod()
