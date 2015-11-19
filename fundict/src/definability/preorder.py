import networkx, itertools, random

le=lambda x,y:y%x==0
nodos = range(-3,0) + range(1,4) + [6,-6]
lados = []
for a,b in itertools.product(nodos,repeat=2):
    if le(a,b):
        lados.append((a,b))

g=networkx.MultiDiGraph(lados)

def arbolDFS(grafo,origen):
    """
    Devuelve el arbol DFS de un grafo desde un origen dado.
    """
    s = [] # es una pila LIFO
    visitado = []
    s.append(origen)
    le=[]
    equal = []
    nodes = random.sample(grafo.nodes(),len(grafo.nodes())) # para probar con muchos ordenes
    
    while s:
        v = s[-1] # lo toma del final
        if len(s) >= 2:
            pv = s[-2]
        else:
            pv = None
        agrego = False
        if pv in nodes:
            nodes.remove(pv)
            nodes = [pv] + nodes
        for w in nodes:
            if v!=w and (v,w) in grafo.edges():
                if (v,w) not in visitado:
                    agrego = True 
                    visitado.append((v,w))
                    s.append(w) # lo inserta al final
                    if (w,v) in le:
                        assert w in s[:-1]
                        le.remove((w,v))
                        equal.append((w,v))
                        nodes.remove(v)
                        s = s[:-1] # borra el ultimo
                        agrego = False
                    else:
                        le.append((v,w))
                    break
        if not agrego:
            #result[v].sort() # ya esta listo, lo ordeno
            del s[-1] # lo borra porque todos sus vecinos fueron visitados
    
    return le,equal
