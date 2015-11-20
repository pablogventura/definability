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

def arbolDFS(grafo,origen):
    """
    Devuelve el arbol DFS de un grafo desde un origen dado.
    """
    path = [] # es una pila LIFO (lleva el camino actual)
    visitado = [] # lados ya recorridos
    path.append(origen)
    le=[] # lista de tuplas de <=
    equal = [] # lista de tuplas de = cocientado
    nodes = random.sample(grafo.nodes(),len(grafo.nodes())) # para probar con muchos ordenes
    
    while path:
        v = path[-1] # lo toma del final
        father_first_sort(nodes, path)
        for w in nodes:
            if v!=w and (v,w) not in visitado:
                if (v,w) in grafo.edges():
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
    if len(path) >= 2 and path[-2] in nodes:
        nodes.remove(path[-2])
        nodes.insert(0,path[-2])
