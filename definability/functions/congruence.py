#!/usr/bin/env python
# -*- coding: utf8 -*-

from ..first_order.fofunctions import FO_Relation
from ..misc.misc import indent
from ..interfaces.minion_limpio import MinionSolLimpio, ParallelMinionSolLimpio
from itertools import combinations, product, chain
from functools import lru_cache
from functools import reduce, total_ordering
from collections import defaultdict


class _CardinalBlock(object):
    def __init__(self, value):
        self.value = value


class Partition(object):
    def __init__(self, iter_of_iter=()):
        self.v = dict()
        self.from_table(iter_of_iter)
    
    def __call__(self, a, b):
        return self.root(a) == self.root(b)
    
    def from_table(self, l):
        for a, b in l:
            self.add_element(a)
            self.add_element(b)
            self.join_blocks(a, b)
    
    def table(self):
        result = set()
        for a in self.v:
            for b in self.v:
                if self(a, b):
                    result.add((a, b))
        return result
    
    def copy(self):
        result = Partition()
        result.v = self.v.copy()
        return result
    
    def from_blocks(self, ls):
        """
        Extiende la particion con una lista de listas
        :param list:
        :return:
        """
        for l in ls:
            for e in l:
                self.add_element(e)
                self.join_blocks(e, l[0])
    
    def add_element(self, e):
        if e not in self.v:
            self.v[e] = _CardinalBlock(-1)
    
    def root(self, e):
        """
        Representante de la clase de equivalencia de e
        """
        # TODO NO DEBERIA SER RECURSIVO
        # deberia avanzar recordando los que no tienen al root como padre y acomodar todo al final
        if self.is_root(e):
            return e
        else:
            self.v[e] = self.root(self.v[e])
            return self.v[e]
    
    def join_blocks(self, i, j):
        
        ri = self.root(i)
        rj = self.root(j)
        if ri != rj:
            si = self.v[ri].value
            sj = self.v[rj].value
            if si > sj:
                self.v[ri] = rj
                self.v[rj] = _CardinalBlock(si + sj)
            else:
                self.v[rj] = ri
                self.v[ri] = _CardinalBlock(si + sj)
    
    def to_list(self):
        result = defaultdict(list)
        for e in self.v:
            result[self.root(e)].append(e)
        return list(result.values())
    
    def __eq__(self, other):
        return self.table() == other.table()

    def __lt__(self, other):
        return self.table() < other.table()

    def __le__(self, other):
        return self == other or self < other
    
    def __ge__(self, other):
        return other <= self
    
    def __gt__(self, other):
        return other < self
    
    def __repr__(self):
        result = repr(self.to_list())[1:-1].replace("[", "|").replace("]", "|")
        return "[" + result + "]"
    
    def meet(self, other):
        """

        :type other: Partition
        """
        result = Partition()
        ht = dict()
        for e in self.v:
            r1 = self.root(e)
            r2 = other.root(e)
            if (r1, r2) in ht:
                r = ht[r1, r2]
                result.v[r] = _CardinalBlock(result.v[r].value + 1)
                result.v[e] = r
            else:
                ht[(r1, r2)] = e
                result.v[e] = _CardinalBlock(-1)
        return result
    
    def is_root(self, e):
        return isinstance(self.v[e], _CardinalBlock)
    
    def join(self, other):
        """
        The join(U, V)
            for each i which is not a root of U
                join-blocks(i, U[i], V)
        :type other: Partition
        """
        result = other.copy()
        for e in self.v:
            if not self.is_root(e):  # not a root
                result.join_blocks(e, self.root(e))
        return result
    
    def iter_tuples(self):
        for a in self.v:
            for b in self.v:
                if self(a, b):
                    yield (a, b)
    
    def block(self, e):
        result = set()
        r = self.root(e)
        for i in self.v:
            if self.root(i) == r:
                result.add(i)
        return frozenset(result)
    
    def iter_blocks(self):
        for e in self.v:
            if self.is_root(e):
                yield self.block(e)

    def roots(self):
        for e in self.v:
            if self.is_root(e):
                yield e
    
    def to_congruence(self, model):
        return Congruence(self.table(), model)
    
    def __hash__(self):
        return hash(frozenset(self.v.items()))


class Congruence(Partition):
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
    
    def __init__(self, table, model, check_operations=False):
        self.model = model
        super(Congruence, self).__init__(table)
        self_relation = []
        for i in model.universe:
            self_relation.append((i,i))
        self.from_table(self_relation)
        if check_operations:
            assert self.are_operations_preserved()
    
    def __is_operation_preserved(self, op):
        if self.model.operations[op].arity() == 0:
            pass
        else:
            for t in self.model.operations[op].domain():
                for s in self.model.operations[op].domain():
                    if self.are_tuples_related(t, s):
                        if not self(self.model.operations[op](*t), self.model.operations[op](*s)):
                            return False
        return True
    
    def are_operations_preserved(self):
        result = True
        for op in self.model.operations:
            result = result and self.__is_operation_preserved(op)
        return result
    
    def are_tuples_related(self, t, s):
        for i in range(len(t)):
            if not self(t[i], s[i]):
                return False
        return True

    def classes(self):
        return self.iter_blocks()

    def equiv_class(self, x):
        return self.block(x)

    def copy(self):
        return Congruence(self.table(), self.model)
    
    def __and__(self, other):
        """
        Genera la congruencia a partir de la intersección de 2 congruencias
        """
        assert self.model == other.model
        return self.meet(other).to_congruence(self.model)
    
    def __or__(self, other):
        """
        Genera la congruencia a partir de la unión de 2 congruencias
        """
        assert self.model == other.model
        return self.join(other).to_congruence(self.model)
    
    def __eq__(self, other):
        if self.model != other.model:
            return False
        return super(Congruence, self).__eq__(other)

    def __lt__(self, other):
        if self.model != other.model:
            return False
        return super(Congruence, self).__lt__(other)

    def __le__(self, other):
        if self.model != other.model:
            return False
        return super(Congruence, self).__le__(other)
    
    def __ge__(self, other):
        if self.model != other.model:
            return False
        return super(Congruence, self).__ge__(other)
    
    def __gt__(self, other):
        if self.model != other.model:
            return False
        return super(Congruence, self).__gt__(other)
    
    def __repr__(self):
        return "Congruence(" + super(Congruence, self).__repr__() + ")"
    
    def __hash__(self):
        return hash(frozenset(self.v.items()))


class CongruenceSystem(object):
    """
    Sistema de Congruecias
    Dado una lista de congruencias, una lista de elementos y un sigma generador
    del proyecto, genera el Sistema de Congruencias para ese proyectivo

    >>> from definability import fotheories
    >>> C1 = Congruence([(1, 1),(2, 2),(3, 3),(0, 0),(1, 3),(3, 1),(0, 2),(2, 0)], fotheories.Lat.find_models(4)[0])
    >>> C2 = Congruence([(1, 1),(2, 2),(3, 3),(0, 0),(0, 3),(3, 0),(1, 2),(2, 1)], fotheories.Lat.find_models(4)[0])
    >>> CS = CongruenceSystem([C1, C2], [2, 3])
    >>> CS.solutions()
    {0}
    """
    
    def __init__(self, congruences, elements, sigma=None, check_system=False):
        assert congruences and isinstance(congruences, list)
        assert elements and isinstance(elements, list)
        assert len(elements) == len(elements)
        n = len(elements)
        model = congruences[0].model
        for tita in congruences:
            assert isinstance(tita, Congruence)
            assert tita.model == model
        for x in elements:
            assert x in model.universe
        self.model = model
        self.n = n
        self.congruences = congruences
        self.elements = elements
        if check_system:
            if sigma:
                assert self.is_system(lambda x, y: sup_proj(sigma, x, y))
            else:
                assert self.is_system()
        self.sigma = sigma
    
    def solutions(self):
        sol = self.congruences[0].equiv_class(self.elements[0])
        for i in list(range(self.n)):
            if i != 0:
                sol = sol & self.congruences[i].equiv_class(self.elements[i])
        return sol
    
    def has_solution(self):
        if len(self.solutions()) == 0:
            return False
        else:
            return True
    
    def is_system(self, sup=lambda x, y: x | y):
        for i in list(range(self.n)):
            for j in list(range(self.n)):
                if i != j:
                    if [self.elements[i], self.elements[j]] not in sup(self.congruences[i], self.congruences[j]):
                        return False
        return True


def maxcon(model):
    univ = [(x, y) for x in model.universe for y in model.universe]
    return Congruence(univ, model)


def mincon(model):
    univ = [(x, x) for x in model.universe]
    return Congruence(univ, model)


def sup_proj(sigma, x, y):
    """
    Devuelve el supremo entre x e y dentro del reticulado de congruencias
    generado por el conjunto sigma
    """
    assert x.model == y.model
    xy_up = [c for c in sigma if (x <= c and y <= c)]
    e = maxcon(x.model)
    for r in xy_up:
        e = e & r
    return e


def empty_intersections(con_list):
    l = []
    for c in con_list:
        l.append(sorted(c.classes(), key=len))
    for t in product(*l):
        r = frozenset.intersection(*t)
        if not r:
            yield t


def find_system(sigma, con_list, tuple_of_sets):
    model = list(sigma)[0].model
    joins = dict()
    for i, j in combinations(range(len(con_list)), r=2):
        joins[(i, j)] = sup_proj(sigma, con_list[i], con_list[j])
    
    to_minion = "MINION 3\n\n"
    to_minion += "**VARIABLES**\n"
    to_minion += "DISCRETE x[%s]{0..%s}\n\n" % (len(con_list), len(model) - 1)
    to_minion += "**TUPLELIST**\n"
    for i, s in enumerate(tuple_of_sets):
        to_minion += "D%s %s 1\n" % (i, len(s))
        for a in s:
            to_minion += "%s\n" % a
        to_minion += "\n"
    for (i, j) in joins:
        to_minion += "J%sJ%s %s 2\n" % (i, j, len(joins[(i, j)].d))
        for a, b in joins[(i, j)].d:
            to_minion += "%s %s\n" % (a, b)
        to_minion += "\n"
    to_minion += "**CONSTRAINTS**\n"
    for i in range(len(tuple_of_sets)):
        to_minion += "table([x[%s]],D%s)\n" % (i, i)
    for (i, j) in joins:
        to_minion += "table([x[%s],x[%s]],J%sJ%s)\n" % (i, j, i, j)
    to_minion += "\n\n"
    to_minion += "**EOF**"
    return MinionSolLimpio(to_minion, allsols=False)


def find_system_output(sigma, con_list, e_i):
    model = list(sigma)[0].model
    joins = dict()
    for i, j in combinations(range(len(con_list)), r=2):
        joins[(i, j)] = con_list[i] | con_list[j]
    
    to_minion = "MINION 3\n\n"
    to_minion += "**VARIABLES**\n"
    to_minion += "DISCRETE x[%s]{0..%s}\n\n" % (len(con_list), len(model) - 1)
    to_minion += "**TUPLELIST**\n"
    
    to_minion2 = ""
    for (i, j) in joins:
        to_minion2 += "J%sJ%s %s 2\n" % (i, j, len(joins[(i, j)].d))
        for a, b in joins[(i, j)].d:
            to_minion2 += "%s %s\n" % (a, b)
        to_minion2 += "\n"
    to_minion2 += "**CONSTRAINTS**\n"
    
    to_minion4 = ""
    for (i, j) in joins:
        to_minion4 += "table([x[%s],x[%s]],J%sJ%s)\n" % (i, j, i, j)
    to_minion4 += "\n\n"
    to_minion4 += "**EOF**"
    
    for tuple_of_sets in e_i:
        to_minion1 = ""
        to_minion3 = ""
        for i, s in enumerate(tuple_of_sets):
            to_minion1 += "D%s 1 1\n" % i
            to_minion1 += "%s\n" % next(iter(s))
            to_minion1 += "\n"
            to_minion3 += "table([x[%s]],D%s)\n" % (i, i)
        
        yield MinionSolLimpio(to_minion + to_minion1 + to_minion2 + to_minion3 + to_minion4, allsols=False)


def not_all_min_systems_solvable(sigma):
    sigma_m = minorice(sigma)
    e_i = empty_intersections(sigma_m)
    for i, solution in enumerate(find_system_output(sigma, sigma_m, e_i)):
        if i % 100 == 0:
            print("\t%s" % i)
        if solution:
            print("\t%s" % i)
            return solution
    return False


def minimal_systems(sigma):
    model = list(sigma)[0].model
    sigma_m = minorice(sigma)
    joins = dict()
    for i, j in combinations(range(len(sigma_m)), r=2):
        joins[(i, j)] = sup_proj(sigma, sigma_m[i], sigma_m[j])
    
    to_minion = "MINION 3\n\n"
    to_minion += "**VARIABLES**\n"
    to_minion += "DISCRETE x[%s]{0..%s}\n\n" % (len(sigma_m), len(model) - 1)
    to_minion += "**TUPLELIST**\n"
    for (i, j) in joins:
        to_minion += "J%sJ%s %s 2\n" % (i, j, len(joins[(i, j)].d))
        for a, b in joins[(i, j)].d:
            to_minion += "%s %s\n" % (a, b)
        to_minion += "\n"
    to_minion += "**CONSTRAINTS**\n"
    for (i, j) in joins:
        to_minion += "table([x[%s],x[%s]],J%sJ%s)\n" % (i, j, i, j)
    to_minion += "\n\n"
    to_minion += "**EOF**"
    return MinionSolLimpio(to_minion)


def is_system(cong, elem, sup=lambda x, y: x | y):
    for i in list(range(len(cong))):
        for j in list(range(len(cong))):
            if i != j:
                if [elem[i], elem[j]] not in sup(cong[i], cong[j]):
                    return False
    return True


def minorice(sigma):
    """
    Dado un conjunto de congruecias devuelve el conjunto minimo
    {tita: tita in sigma tal que no existe delta in sigma con delta contenido en sigma}
    """
    rem = []
    sigma = list(set(sigma))
    for i in list(range(len(sigma))):
        if i not in rem:
            for j in range(i + 1, len(sigma)):
                if sigma[i] & sigma[j] == sigma[j]:
                    rem.append(i)
                    break
                elif sigma[i] & sigma[j] == sigma[i]:
                    rem.append(j)
    return [x for x in sigma if sigma.index(x) not in rem]


def subspectra(congruences):
    model = list(congruences)[0].model
    A_old = [[i] for i in range(len(congruences))]
    Adelta_old = []
    while A_old or Adelta_old:
        A = []
        Adelta = []
        for cs in A_old:
            for other in range(cs[-1] + 1, len(congruences)):
                if all(not congruences[other] < congruences[c] and not congruences[c] < congruences[other] for c in cs):
                    new = cs + [other]
                    
                    if reduce(lambda x, y: x & y, [congruences[i] for i in new], ) == mincon(model):
                        
                        Adelta.append(new)
                        yield [congruences[i] for i in new]
                    else:
                        A.append(new)
        for cs in Adelta_old:
            for other in range(cs[-1] + 1, len(congruences)):
                if all(not congruences[other] < congruences[c] and not congruences[c] < congruences[other] for c in cs):
                    new = cs + [other]
                    Adelta.append(new)
                    yield [congruences[i] for i in new]
        A_old = A
        Adelta_old = Adelta


def antichain(sigma, i, deltas):
    for j in deltas:
        if sigma[i] <= sigma[j] or sigma[j] <= sigma[i]:
            return False
    return True

def does_extend(sigma, deltas, x_tuple, i, z):
    assert len(deltas) == len(x_tuple)
    n = len(deltas)
    for j in range(n):
        join = sigma[deltas[j]] | sigma[i]
        if x_tuple[j] not in join.block(z):
            return False
    return True

def has_solution(sigma, deltas, x_tuple, i, z):
    n = len(deltas)
    inters_class = sigma[i].block(z)
    for j in range(n):
        inters_class = inters_class & sigma[deltas[j]].block(x_tuple[j])
    return inters_class != frozenset({})

def extend_const_sys(sigma, intersection, deltas, i):
    output = []
    n = len(deltas)
    for a in intersection.roots():
        clase_inter = intersection.block(a)
        for z in sigma[i].roots():
            clase_i = sigma[i].block(z)
            if clase_inter & clase_i == frozenset({}):
                a_tuple = n * [a]
                if does_extend(sigma, deltas, a_tuple, i, z):
                    output.append(a_tuple + [z])
    return output
 
def extend_non_sol_sys(sigma, deltas, i, vector):
    output = []
    for z in sigma[i].roots():
        if does_extend(sigma, deltas, vector, i, z):
            if not has_solution(sigma, deltas, vector, i, z):
                output.append(vector + [z])
    return output
 
def all_subspectra(A, sigma, all_solutions=True):
    n = len(sigma)
    print(n)
    H_old = [([] ,maxcon(A), [])]
    H_new = H_old.copy()
    solutions = []
    for i in range(n):
        for (deltas, intersection, vectors) in H_old:
            if antichain(sigma, i, deltas):
                intersection_new = intersection & sigma[i]
                deltas_new = deltas.copy()
                deltas_new.append(i)
                vectors_new = extend_const_sys(sigma, intersection, deltas, i)
                for vector in vectors:
                    vectors_new = vectors_new + extend_non_sol_sys(sigma, deltas, i, vector)
                new_tuple = (deltas_new, intersection_new, vectors_new)
                if intersection_new == mincon(A) and vectors_new == []:
                    if all_solutions == False:
                        return new_tuple
                    solutions.append(new_tuple)
                H_new.append(new_tuple)
        H_old = H_new
        print(i, len(H_old))
    return solutions
 
def all_global_desc(A, F, all_solutions=True):
    sigma = A.congruences_in(F)
    return all_subspectra(A, list(sigma), all_solutions)


if __name__ == "__main__":
    import doctest
    
    doctest.testmod()
"""
d = examples.cadena2sl
t = examples.cadena3sl
carpa = examples.carpasl
c = examples.cascosl
sigma = c.congruences_in([d,t,carpa])
functions.congruence.all_min_systems_solvable(sigma)
"""
