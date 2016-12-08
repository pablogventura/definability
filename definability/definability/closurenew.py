from unionfind import UnionFind

uf = UnionFind()
uf.insert_objects(product(m.universe, repeat=arity))

for each node u :
   for each node v connected to u :  
       if findset(u)!=findset(v) :
           union(u,v)  

**I assume you know about how findset and union works **  
for each node if (parent[node] == node)  
    connected_component += 1
