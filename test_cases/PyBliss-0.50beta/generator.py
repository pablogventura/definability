import sys
sys.path.append('.')
sys.path.append('./lib/python')
import PyBliss



def traverse3(G, N):
    """
    Enumerate all graphs over N vertices up to isomorphism
    by using a form the 'weak canonical augmentation' method.
    """
    result = []
    if G.nof_vertices() == N:
        return [G]
    i = G.nof_vertices()
    vertices = G.get_vertices() + ["tmp"]
    children = set()
    for k in xrange(0, pow(2, i+1)):
        G.add_vertex('tmp')
        for j in xrange(0, i+1):
            if (k & 0x01) == 1:
                G.add_edge('tmp', vertices[j])
            k = k / 2
        child = G.relabel(G.canonical_labeling())
        G.del_vertex('tmp') # restore G
        if child in children:
            continue
        child2 = child.copy()
        child2.del_vertex(0)
        child2_canform = child2.relabel(child2.canonical_labeling())
        if child2_canform.get_isomorphism(G) != None:
            children.add(child)
    for child in children:
        result += traverse3(child, N)
    return result

N = 5
G = PyBliss.Graph()
h=traverse3(G, N)
#print h
print (len(h))
print (h[5])
print ("There are "+str(len(h))+" non-isomorphic graphs with "+str(N)+" vertices")

import sqlite3
conn = sqlite3.connect('graphs.db')

c = conn.cursor()
# Create table
c.execute('''CREATE TABLE tests
             (nnodes INT, nedges INT, ngensubisos INT, natomslindenbaum INT, time BIGINT, graph BLOB)''')

for g in h:
    #pgraph = cPickle.dumps(g, cPickle.HIGHEST_PROTOCOL)
    #curr.execute("insert into table (data) values (:data)", sqlite3.Binary(pdata))



    # Insert a row of data
    c.execute("INSERT INTO tests VALUES (?, ?, ?, ?, ?, ?)", (g.nof_vertices(),0,0,0,0,"hola"))

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()


