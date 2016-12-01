# ./geng 1 -q |./vcolg -e0:1 -T -q
import subprocess as sp

import os

home = os.getenv('HOME')

# siempre tienen que terminar en barra
nauty_path = os.path.join(home, "nauty26r7/")

def parse(line):
    if not line:
        return
    else:
        line = line.split(" ")
        nnodes = int(line.pop(0))
        nedges = int(line.pop(0))
        
        color = []
        for i in range(nnodes):
            color.append(int(line.pop(0)))
        
        edges = []
        if nedges:    
            assert line.pop(0) == ''
            for i in range(nedges):
                a = int(line.pop(0))
                b = int(line.pop(0))
                edges.append((a,b))
        return (nnodes,nedges,color,edges)

def generate_color_graphs(cardinality):
    geng = sp.Popen([nauty_path + "geng"] + [str(cardinality), "-q"], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    vcolg = sp.Popen([nauty_path + "vcolg"] + ["-e0:%s" % cardinality, "-T", "-q"], stdin=geng.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
    result=[]
    line=vcolg.stdout.readline().strip()
    while line:
        result.append(parse(line))
        line=vcolg.stdout.readline().strip()
    return result

import sqlite3
conn = sqlite3.connect('graphs.db')

c = conn.cursor()
c.execute('''CREATE TABLE tests
             (nnodes INT, nedges INT, ngensubisos INT, natomslindenbaum INT, time BIGINT, graph BLOB)''')

for g in []:
    # Insert a row of data
    c.execute("INSERT INTO tests VALUES (?, ?, ?, ?, ?, ?)", (g.nof_vertices(),0,0,0,0,"hola"))

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()


print generate_color_graphs(2)
