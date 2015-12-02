#!/usr/bin/env python
# -*- coding: utf8 -*-

from collections import defaultdict

def preorder_to_poset(nodes, func_le, source=None):
    """
    Recorre con DFS el preorden y siempre trata de encontrar una ida y venida
    con el siguiente vertice del camino, para poder ir cocientando y disminuir
    el tamaño del grafo formado por el preorden.
    Empieza desde source, si no llega a recorrer todo, sigue por un vertice sin explorar.
    Devuelve la lista de tuplas en <= en el poset y un diccionario con las equivalencias.
    
    >>> import itertools, random
    >>> le = lambda x,y: y % x == 0
    >>> nodos = range(-3,0) + range(1,4) + [6,-6]
    >>> filter(lambda n: map(len,preorder_to_poset(n, le)) != [5,4],itertools.permutations(nodos))
    []
    """
    nodes_to_check = list(nodes) # vertices ya recorridos
    if source:
        nodes_to_check.remove(source)
        nodes_to_check.insert(0,source)

    checked_edges = defaultdict(set) # lados ya recorridos
    inaccesibles = defaultdict(set)
    quo_nodes = list(nodes) # los nodos que van quedando al cocientar
    
    le=[] # lista de tuplas de <=
    equal = defaultdict(list) # lista de tuplas de = cocientado
    
    while nodes_to_check:
        path = [nodes_to_check[0]] # es una pila LIFO (lleva el camino actual)
        
        while path:
            v = path[-1] # lo toma del final
            if v in nodes_to_check:
                nodes_to_check.remove(v)
            for w in father_first_sort(quo_nodes, path):
                if w not in checked_edges[v]:
                    checked_edges[v].add(w) # no quiero volver a pasar por aca
                    if func_le(v,w):
                        if len(path) >= 2 and path[-2] == w: # puedo volver!
                            le.remove((w,v))
                            equal[w].append(v)
                            inaccesibles[w] = inaccesibles[w].union(inaccesibles[v])
                            checked_edges[w] = checked_edges[w].union(inaccesibles[w])
                            quo_nodes.remove(v)
                            del path[-1]
                        else:
                            path.append(w) # ahora el camino es mas largo
                            le.append((v,w))
                            inaccesibles[w] = inaccesibles[w].union(inaccesibles[v])
                            checked_edges[w] = checked_edges[w].union(inaccesibles[w])
                        break
                    else:
                        inaccesibles[v].add(w)
            if v == path[-1]:
                for vv in path[:-1]:
                    if (vv,v) not in le:
                        le.append((vv,v))
                        checked_edges[vv].add(v)
                del path[-1] # lo borra porque no agrego a nadie nuevo FINAL DEL CAMINO

    return le,equal



def pre_to_poset(nodes, fun_le, origen):
    """
    Version mas lenta, pero mas conceptual
    """
    nodes = list(nodes)
    c = [origen]
    cs = []
    inal = defaultdict(set)
    eq = defaultdict(set)

    while c:

        v = c[-1]

        orden = [x for x in nodes if x not in inal[v] and x != v]
        if len(c) >= 2 and c[-2] in orden:
            orden.remove(c[-2])
            orden = [c[-2]] + orden
        for w in orden:

            if w not in inal[v] and ((len(c) >= 2 and w == c[-2]) or not any(v in p and w in p for p in [c]+cs)):
                if fun_le(v,w):
                    if len(c) >= 2 and c[-2] == w:
                        del c[-1]
                        nodes.remove(v)
                        eq[w].add(v)
                    else:
                        c.append(w)
                        inal[w] = inal[w].union(inal[v])
                    break
                else:
                    inal[v].add(w)
        if v == c[-1]:
            if (not cs) or (cs and c != cs[-1][:len(c)]):
                cs.append(list(c))
            del c[-1]
    return cs, eq
    

def transitive_closure(relation, universe):
    """
    Clausura transitiva con el algoritmo de Warshall (modificado!)
    http://people.cs.pitt.edu/~adamlee/courses/cs0441/lectures/lecture27-closures.pdf
    """
    relation = set(relation)   
    for k in universe:
        for i in universe:
            for j in universe:
                if (i,k) in relation and (k,j) in relation:
                    relation.add((i,j))
    return relation


def father_first_sort(nodes, path):
    """
    Iterador que devuelve primero el padre del ultimo elemento del camino
    y luego va devolviendo aquellos nodos que no estan en el camino en cualquier orden.
    """
    if len(path) >= 2 and path[-2] in nodes:
        yield path[-2]
    for node in nodes:
        if node not in path:
            yield node


if __name__ == "__main__":
    import doctest
    doctest.testmod()
