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

    checked_edges = [] # lados ya recorridos
    le=[] # lista de tuplas de <=
    equal = defaultdict(list) # lista de tuplas de = cocientado
    quo_nodes = list(nodes) # los nodos que van quedando al cocientar
    
    while nodes_to_check:
        path =  [nodes_to_check[0]] # es una pila LIFO (lleva el camino actual)
        
        while path:
            v = path[-1] # lo toma del final
            if v in nodes_to_check:
                nodes_to_check.remove(v)
            for w in father_first_sort(quo_nodes, path):
                if (v,w) not in checked_edges:
                    if func_le(v,w):
                        checked_edges.append((v,w)) # no quiero volver a pasar por aca
                        if (w,v) in le:
                            assert w == path[-2] # entonces ya habia pasado por w antes de llegar a v
                            le.remove((w,v))
                            equal[w].append(v)
                            quo_nodes.remove(v)
                        else:
                            path.append(w) # ahora el camino es mas largo
                            le.append((v,w))
                        break
            if v == path[-1]:
                del path[-1] # lo borra porque no agrego a nadie nuevo FINAL DEL CAMINO

    return le,equal

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
