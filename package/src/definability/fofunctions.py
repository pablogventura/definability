#!/usr/bin/env python
# -*- coding: utf8 -*-

from functions import Function
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
        if d and isinstance(d,list) and isinstance(d[0],tuple):
            d = {k:True for k in d}
        assert d_universe
        super(FO_Relation, self).__init__(d)
        self.d_universe = d_universe
        self.relation = True

    def is_a_function_graph(self, universe):
        """
        Revisa si la relacion es el grafico de una funcion para un universo dado.
        Si lo es, devuelve la funcion, y sino devuelve False.
        
        >>> rel = FO_Relation({(0,0,1):1,(0,0,2):1,(1,1,2):1},range(4))
        >>> rel.is_a_function_graph(range(4))
        False
        """
        table = self.table()
        # filtra los que estan en el universo
        function = filter(lambda t: all(v in universe for v in t), table)
        function = {tuple(t[:(self.arity() - 1)]): t[-1]
                    for t in function}  # le quita el ultimo a cada tupla
        sdomain = set(map(tuple, function.keys()))
        # habia tuplas repetidas, no respeta la condicion de funcion
        if len(function) != len(sdomain):
            return False
        # no tiene dominio suficiente
        elif len(sdomain) != len(universe)**(self.arity() - 1):
            return False
        else:
            return FO_Operation(function)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
