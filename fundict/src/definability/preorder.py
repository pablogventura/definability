import itertools, random
from collections import defaultdict

def le(x,y):
    if x % 7 == 0:
        x = x / 7
    return y % x == 0

nodos = range(-3,0) + range(1,4) + [6,-6]
nodos = nodos + map(lambda x:x*7, nodos)
lados = []
for a,b in itertools.product(nodos,repeat=2):
    if le(a,b):
        lados.append((a,b))


def preorder_to_poset(nodes, func_le, source=None):
    """
    Devuelve el arbol DFS de un grafo desde un origen dado.
    """
    nodes_to_check = random.sample(nodes,len(nodes)) # vertices ya recorridos
    if source:
        nodes_to_check.remove(source)
        nodes_to_check.insert(0,source)

    checked_edges = [] # lados ya recorridos
    le=[] # lista de tuplas de <=
    equal = defaultdict(list) # lista de tuplas de = cocientado
    quo_nodes = random.sample(nodes,len(nodes)) # los nodos que van quedando al cocientar
    
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
    
