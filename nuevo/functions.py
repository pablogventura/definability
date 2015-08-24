#!/usr/bin/env python
# -*- coding: utf8 -*-

import numpy as np
from itertools import product
from misc import indent
import copy

class Function(object):

    r"""
    Define el arreglo n dimensional que se usan para tener operaciones y relaciones n-arias.
    Necesariamente toma numeros desde 0

    >>> sum_mod3=Function([[0,1,2],[1,2,0],[2,0,1]])
    >>> sum_mod3
    Function([
    [0 1 2],
    [1 2 0],
    [2 0 1],
    ])
    
    >>> list(sum_mod3.domain())
    [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    
    >>> sum_mod3.arity()
    2
    
    >>> emb = [2,1]
    >>> g=sum_mod3.restrict(emb)
    >>> g(emb.index(1),emb.index(2)) == sum_mod3(1,2)
    True
    
    >>> suma1 = Function([1,2,0])
    >>> suma1asum_mod3 = suma1.composition(sum_mod3)
    >>> suma1asum_mod3(1,2)
    1
    
    >>> suma1asum_mod3.map_in_place(lambda x: x+3)
    >>> suma1asum_mod3(1,2)
    4
    
    >>> sum_mod3(2,2)
    1
    
    >>> len(sum_mod3) # debe dar 3 porque los argumentos estan en range(0,3)
    3
    
    >>> sum_mod3.minion_table("a") # minion toma estas tablas
    'a 9 3\n0 0 0\n0 1 1\n0 2 2\n1 0 1\n1 1 2\n1 2 0\n2 0 2\n2 1 0\n2 2 1\n'
    
    >>> sum_mod3.table()
    [[0, 0, 0], [0, 1, 1], [0, 2, 2], [1, 0, 1], [1, 1, 2], [1, 2, 0], [2, 0, 2], [2, 1, 0], [2, 2, 1]]
    """
    def __init__(self, l):
        self.array = np.array(l)
        self.relation = False # maneja si la funcion es booleana
        
    def copy(self):
        """
        Devuelve una copia de si mismo
        """
        result = copy.copy(self)
        result.array = np.copy(result.array)
        return result
    
    def domain(self):
        """
        Un generador del dominio
        """
        return product(range(len(self)), repeat=self.arity())

    def arity(self):
        return self.array.ndim

    def restrict(self,elements):
        """
        Restringe el dominio a elements, en ese orden.
        Necesita certeza de que elements es cerrado bajo esta funcion!
        """

        # tengo que hacer reemplazos de nombre
        result = np.copy(self.array)
        i=0
        for k in elements:
            result[self.array==k] = i
            i+=1
        
        # tengo que borrar filas y columnas
        args = [elements for i in range(self.arity())]
        return Function(result[np.ix_(*args)].tolist())

            
    def composition(self,g):
        """
        Compone con otra list with arity, F.compone(G) = F o G
        y devuelve una nueva list with arity
        """
        assert self.arity() == 1
        result = g.copy()
        result.map_in_place(self)
        return result
        
        
    def map_in_place(self, f):
        """
        Funciona como un map, pero respeta la estructura de la matriz.
        """
        a = self.array.reshape(-1)
        for i, v in enumerate(a):
            a[i] = f(v)

    def __call__(self, *args):
        assert len(args) == self.arity()
        if len(args)==0:
            args = [0]
        result = self.array
        for i in args:
            result = result[i]
        if self.relation:
            return bool(result)
        else:
            return result
    
    def __len__(self):
        """
        Devuelve la cardinalidad del conjunto de partida.
        """
        return len(self.array)
        
    def __repr__(self):
        if self.relation:
            result = "Relation(\n"
            table = map(lambda x:"%s," % x,self.table())
        else:
            result = "Function(\n"
            table = map(lambda x: "%s -> %s," % (x[:-1],x[-1]) ,self.table())
        table = indent("\n".join(table))

        return result + table + ")"

    def table(self):
        """
        Devuelve una lista de listas con la tabla que representa a la relacion/operacion
        """
            
        cardinality = len(self)
        result = []
        for t in self.domain():
            if not self.relation or self(*t):
                result.append(list(t))
                if not self.relation:
                    result[-1].append(self(*t))
        if len(result)==0:
            result.append([])
        return result


if __name__ == "__main__":
    import doctest
    doctest.testmod()
