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

    def is_a_function_graph(self, universe):
        """
        Revisa si la relacion es el grafico de una funcion para un universo dado.
        Si lo es, devuelve la funcion, y sino devuelve False.
        """
        table = self.table()
        function = filter(lambda t: all(v in universe for v in t), table) # filtra los que estan en el universo
        function = {tuple(t[:(self.arity()-1)]):t[-1] for t in function} # le quita el ultimo a cada tupla
        sdomain = set(map(tuple,function.keys()))
        if len(function) != len(sdomain): # habia tuplas repetidas, no respeta la condicion de funcion
            return False
        elif len(sdomain) != len(universe)**(self.arity()-1): # no tiene dominio suficiente
            return False
        else:
            return FO_Operation(function)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
