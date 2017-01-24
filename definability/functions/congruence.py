#!/usr/bin/env python
# -*- coding: utf8 -*-

from ..first_order.fofunctions import FO_Relation


class Eq_Rel(FO_Relation):

    """
    Relacion binaria que cumple los axiomas de equivalencia

    >>> from definability.examples import examples
    >>> rel = Eq_Rel([(0, 0),(1, 1),(2, 2),(3, 3),(4, 4),(2, 3),(3, 2)], examples.retdiamante)
    >>> rel(2, 3)
    True
    >>> rel(4, 3)
    False
    >>> rel.table()
    [[0, 0], [1, 1], [2, 2], [2, 3], [3, 2], [3, 3], [4, 4]]
    """

    def __init__(self, d, model):
        assert d and isinstance(d, list) and isinstance(d[0], tuple)
        self.model = model
        self.d = d
        super(Eq_Rel, self).__init__(d, model.universe)
        assert self.symm() and self.refl() and self.trans()

    def refl(self):
        for x in self.model.universe:
            if not (x, x) in self.d:
                return False
        return True

    def symm(self):
        for r in self.d:
            if not (r[1], r[0]) in self.d:
                return False
        return True

    def trans(self):
        for r in self.d:
            for s in self.d:
                if r[1] == s[0]:
                    if not (r[0], s[1]) in self.d:
                        return False
        return True


class Congruence(Eq_Rel):

    """
    Congruencia

    >>> from definability import fotheories
    >>> rel = Congruence([(1, 1),(2, 2),(3, 3),(0, 0),(1, 3),(3, 1),(0, 2),(2, 0)], fotheories.Lat.find_models(4)[0])
    >>> rel(1, 3)
    True
    >>> rel(0, 3)
    False
    >>> rel.table()
    [[0, 0], [0, 2], [1, 1], [1, 3], [2, 0], [2, 2], [3, 1], [3, 3]]
    """

    def __init__(self, d, model):
        assert d and isinstance(d, list) and isinstance(d[0], tuple)
        assert model
        self.model = model
        self.d = d
        super(Congruence, self).__init__(d, model)
        assert self.preserva_operaciones()

    def relacionados(self, t, s):
        for i in range(len(t)):
            if not (t[i], s[i]) in self.d:
                return False
        return True

    def __preserva_operacion(self, op):
        if self.model.operations[op].arity() == 0:
            pass
        else:
            for t in self.model.operations[op].domain():
                for s in self.model.operations[op].domain():
                    if self.relacionados(t, s):
                        if not (self.model.operations[op](*t), self.model.operations[op](*s)) in self.d:
                            return False
        return True

    def preserva_operaciones(self):
        result = True
        for op in self.model.operations:
            result = result and self.__preserva_operacion(op)
        return result

    def __and__(self, other):
        assert self.model == other.model
        result = list(set(self.d) & set(other.d))
        return Congruence(result, self.model)

    def __or__(self, other):
        assert self.model == other.model
        result_ant = {}
        result = set(self.d) | set(other.d)
        while (result != result_ant):
            result_ant = result
            for x in self.model.universe:
                for y in self.model.universe:
                    if not (x, y) in result_ant:
                        for z in self.model.universe:
                            if (x, z) in result_ant and (z, y) in result_ant:
                                result = result | {(x, y), (y, x)}
        return Congruence(list(result), self.model)


if __name__ == "__main__":
    import doctest
    doctest.testmod()