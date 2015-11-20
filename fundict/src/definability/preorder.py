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
    s = [] # es una pila LIFO (lleva el camino actual)
    visitado = [] # lados ya recorridos
    s.append(origen)
    le=[] # lista de tuplas de <=
    equal = [] # lista de tuplas de = cocientado
    nodes = random.sample(grafo.nodes(),len(grafo.nodes())) # para probar con muchos ordenes
    
    while s:
        v = s[-1] # lo toma del final
        if len(s) >= 2:
            pv = s[-2] # el padre para preguntar si puedo volver
        else:
            pv = None
        agrego = False
        if pv in nodes:
            nodes.remove(pv)
            nodes = [pv] + nodes
        for w in nodes:
            if v!=w and (v,w) not in visitado:
                if (v,w) in grafo.edges():
                    visitado.append((v,w)) # no quiero volver a pasar por aca
                    if (w,v) in le:
                        assert w == s[-2] # entonces ya habia pasado por w antes de llegar a v
                        le.remove((w,v))
                        equal.append((w,v))
                        nodes.remove(v)
                    else:
                        agrego = True 
                        s.append(w) # ahora el camino es mas largo
                        le.append((v,w))
                    break
        if not agrego:
            del s[-1] # lo borra porque todos sus vecinos fueron visitados
    return le,equal
