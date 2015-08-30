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

    >>> sum_mod3=Function    ([[0,1,2],[1,2,0],[2,0,1]])
    >>> sum_mod3mas3=Function([[3,4,5],[4,5,3],[5,3,4]])
    >>> sum_mod3
    Function(
      [0, 0] -> 0,
      [0, 1] -> 1,
      [0, 2] -> 2,
      [1, 0] -> 1,
      [1, 1] -> 2,
      [1, 2] -> 0,
      [2, 0] -> 2,
      [2, 1] -> 0,
      [2, 2] -> 1,
    )
    
    >>> list(sum_mod3.domain())
    [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    
    >>> sum_mod3.arity()
    2
    
    >>> emb = [2,1]
    >>> g=sum_mod3.restrict(emb)
    >>> emb[g(emb.index(2),emb.index(2))] == sum_mod3(2,2)
    True
    >>> emb[g(emb.index(1),emb.index(1))] == sum_mod3(1,1)
    True
    >>> sum_mod3 == sum_mod3mas3
    False
    >>> sum_mod3.map_in_place(lambda x: x+3)
    >>> sum_mod3 == sum_mod3mas3
    True
    >>> sum_mod3(1,2)
    3
    
    >>> sum_mod3(2,2)
    4
    
    >>> len(sum_mod3) # debe dar 3 porque los argumentos estan en range(0,3)
    3
    
    >>> sum_mod3.table()
    [[0, 0, 3], [0, 1, 4], [0, 2, 5], [1, 0, 4], [1, 1, 5], [1, 2, 3], [2, 0, 5], [2, 1, 3], [2, 2, 4]]
    """
    def __init__(self, l):
        # assert issubclass(type(l),list)
        self.array = np.array(l, dtype=np.dtype(object))
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
        
        result = np.full(self.array.shape, None,dtype=np.dtype(object))
        i=0
        for k in elements:
            if result.ndim == 0:
                if self.array == k:
                    result.itemset(i)
            else:
                result[self.array==k] = i
            i+=1
        
        # tengo que borrar filas y columnas
        
        args = [elements for i in range(self.arity())]
        if result.ndim == 0:    
            return type(self)(result.item())
        else:
            return type(self)(result[np.ix_(*args)].tolist())
        
        
    def map_in_place(self, f):
        """
        Funciona como un map, pero respeta la estructura de la matriz.
        """
        a = self.array.reshape(-1)
        for i, v in enumerate(a):
            if a[i] is not None:
                a[i] = f(v)
    
    def vector_call(self, vector):
        return map(self,vector)

    def __call__(self, *args):
        if not len(args) == self.arity():
            raise ValueError("Arity is %s, not %s. Do you need use vector_call?" % (self.arity(),len(args)))
        result = self.array.tolist()
        for i in args:
            result = result[i]
        if result is None:
            raise ValueError("Value '%s' not in domain" % str(args))
        if self.relation:
            return bool(result)
        else:
            return result
    
    def __len__(self):
        """
        Devuelve la cardinalidad del conjunto de partida.
        """
        return len(self.array)
    
    def __eq__(self,other):
        """
        Dos funciones son iguales si tienen el mismo dominio y el mismo comportamiento.
        """
        # basta con revisar el arreglo, ya que contiene el dominio y el comportamiento
        return (self.array == other.array).all()
    
    def __hash__(self):
        """
        Hash de las funciones para manejar funciones en conjuntos.
        No es muy rapida.
        """
        return hash(self.array.tostring())
        
    def __repr__(self):
        if self.relation:
            result = "Relation(\n"
            table = map(lambda x:"%s," % x,self.table())
        else:
            if self.arity():
                result = "Function(\n"
                table = map(lambda x: "%s -> %s," % (x[:-1],x[-1]) ,self.table())
            else:
                result = "Constant(\n"
                table = str(self.table()[0][0])
        table = indent("\n".join(table))

        return result + table + ")"

    def table(self):
        """
        Devuelve una lista de listas con la tabla que representa a la relacion/operacion
        """
        if self.arity():
            cardinality = len(self)
            result = []
            for t in self.domain():
                try:
                    if self.relation:
                        if self(*t):
                            result.append(list(t))
                    else:
                        result.append(list(t)+[self(*t)])
                except ValueError:
                    # no estaba en el dominio, no se agrega a la tabla
                    pass
            if len(result)==0:
                result.append([])
            return result
        else:
            return [[self.array.item()]]


if __name__ == "__main__":
    import doctest
    doctest.testmod()
