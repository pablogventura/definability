#!/usr/bin/env python
# -*- coding: utf8 -*-

from ..functions.functions import Function
from itertools import product


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

    def graph_fo_relation(self, universe):
        """
        Genera la relacion dada por el grafico de la funcion en el universo
        """
        return FO_Relation([tuple(row) for row in self.table()], universe)


class FO_Relation(FO_OpRel):

    r"""
    Relacion de primer orden

    >>> par = FO_Relation({(0,):1,(1,):0,(2,):1,(3,):0,(4,):1},range(4))
    >>> par(2)
    True
    >>> par(3)
    False
    >>> par.table()
    [[0], [2], [4]]
    """

    def __init__(self, d, d_universe):
        if d and isinstance(d, list) and isinstance(d[0], tuple):
            d = {k: True for k in d}
        assert d_universe
        super(FO_Relation, self).__init__(d)
        self.d_universe = d_universe
        self.relation = True

def FO_Constant(value):
    return FO_Operation({(): value})

if __name__ == "__main__":
    import doctest
    doctest.testmod()
