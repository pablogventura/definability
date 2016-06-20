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

    >>> sum_mod3=Function({(0,0):0, (0,1):1, (0,2):2, (1,0):1, (1,1):2, (1,2):0, (2,0):2, (2,1):0, (2,2):1,})
    >>> sum_mod3mas3=Function({(0,0):3, (0,1):4, (0,2):5, (1,0):4, (1,1):5, (1,2):3, (2,0):5, (2,1):3, (2,2):4,})
    >>> sum_mod3.table()
    [[0, 0, 0], [0, 1, 1], [0, 2, 2], [1, 0, 1], [1, 1, 2], [1, 2, 0], [2, 0, 2], [2, 1, 0], [2, 2, 1]]
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
    [(0, 1), (1, 2), (0, 0), (2, 0), (1, 0), (2, 2), (0, 2), (2, 1), (1, 1)]

    >>> sum_mod3.arity()
    2

    >>> sum_mod3 == sum_mod3mas3
    False
    >>> sum_mod3.map_in_place(lambda x: x+3)
    >>> sum_mod3 == sum_mod3mas3
    True
    >>> sum_mod3(1,2)
    3

    >>> sum_mod3(2,2)
    4

    >>> sum_mod3.table()
    [[0, 0, 3], [0, 1, 4], [0, 2, 5], [1, 0, 4], [1, 1, 5], [1, 2, 3], [2, 0, 5], [2, 1, 3], [2, 2, 4]]
    """

    def __init__(self, d, arity=None):
        # assert issubclass(type(l),list)
        if isinstance(d, list):
            d = self.__list_to_dict(d)
        self.dict = d
        self.empty = False
        assert all(isinstance(t, tuple) for t in self.dict.keys())
        if not self.dict:
            self.empty = True
            self.arityval = arity
        else:
            self.arityval = len(self.dict.keys()[0])
        self.relation = False  # maneja si la funcion es booleana

    def copy(self):
        """
        Devuelve una copia de si mismo
        """
        result = copy.copy(self)
        result.dict = self.dict.copy()
        return result

    def domain(self):
        """
        Un generador del dominio
        """
        if self.relation:
            return product(self.d_universe, repeat=self.arity())
        else:
            return self.dict.iterkeys()

    def image(self):
        """
        Un generador de la imagen
        """
        return iter(set(self.dict.values()))

    def arity(self):
        """
        Devuelve la aridad de la funcion, revisando la 'primer' tupla del diccionario.
        """
        return self.arityval

    def map_in_place(self, f):
        """
        Funciona como un map, pero respeta la estructura de la matriz.
        """
        self.dict = self.dict.copy()
        for key in self.dict:
            self.dict[key] = f(self.dict[key])

    def restrict(self, subuniverse):
        """
        Restringe la funcion a un subconjunto.
        """

        result = self.copy()
        for t in self.dict:
            if any(e not in subuniverse for e in t):
                del result.dict[t]
        return result

    def vector_call(self, vector):
        return type(vector)(map(self, vector))

    def __call__(self, *args):
        if not len(args) == self.arity():
            raise ValueError(
                "Arity is %s, not %s. Do you need use vector_call?" % (self.arity(), len(args)))
        try:
            result = self.dict[args]
        except KeyError:
            if self.relation and all(x in self.d_universe for x in args):
                return False
            print self.relation
            raise ValueError("Value '%s' not in domain" % str(args) + repr(self))

        if self.relation:
            return bool(result)
        else:
            return result

    def __lasfen__(self):
        """
        Devuelve la cardinalidad del conjunto de partida.
        """
        return len(self.array)

    def __eq__(self, other):
        """
        Dos funciones son iguales si tienen el mismo dominio y el mismo comportamiento.
        """
        # basta con revisar el arreglo, ya que contiene el dominio y el
        # comportamiento
        return self.dict == other.dict

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        """
        Hash de las funciones para manejar funciones en conjuntos.
        No es muy rapida.
        """
        return hash(str(sorted(self.dict.iteritems())))

    def table(self):
        """
        Devuelve una lista de listas con la tabla que representa a la relacion/operacion
        """
        result = sorted(self.dict.iteritems())
        if self.relation:
            result = filter(lambda (k, v): v, result)
            result = map(lambda (k, v): list(k), result)
        else:
            result = map(lambda (k, v): list(k) + [v], result)
        return result

    def __list_to_dict(self, l):
        from itertools import product
        import numpy as np
        l = np.array(l, dtype=np.dtype(object))
        arity = l.ndim
        result = {}
        for t in product(range(len(l)), repeat=arity):
            if l.item(*t) is not None:
                result[t] = l.item(*t)
        return result

    def __repr__(self):
        if self.relation:
            result = "Relation(\n"
            table = map(lambda x: "%s," % x, self.table())
        else:
            if self.arity():
                result = "Function(\n"
                table = map(lambda x: "%s -> %s," %
                            (x[:-1], x[-1]), self.table())
            else:
                result = "Constant(\n"
                table = str(self.table()[0][0])
        table = indent("\n".join(table))

        return result + table + ")"

    def __iter__(self):
        """
        Vuelve a las funciones iterables a partir de su grafico
        o a las relaciones directamente desde su conjunto de tuplas.
        """
        return iter(self.table())


if __name__ == "__main__":
    import doctest
    doctest.testmod()
