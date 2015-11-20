import networkx, itertools, random

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

g=networkx.MultiDiGraph(lados)

def arbolDFS(nodes, func_le, origen):
    """
    Devuelve el arbol DFS de un grafo desde un origen dado.
    """
    path = [origen] # es una pila LIFO (lleva el camino actual)
    visitado = [] # lados ya recorridos
    le=[] # lista de tuplas de <=
    equal = [] # lista de tuplas de = cocientado
    nodes = random.sample(nodes,len(nodes)) # para probar con muchos ordenes
    
    while path:
        v = path[-1] # lo toma del final
        for w in father_first_sort(nodes, path):
            if (v,w) not in visitado:
                if func_le(v,w):
                    visitado.append((v,w)) # no quiero volver a pasar por aca
                    if (w,v) in le:
                        assert w == path[-2] # entonces ya habia pasado por w antes de llegar a v
                        le.remove((w,v))
                        equal.append((w,v))
                        nodes.remove(v)
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
    
