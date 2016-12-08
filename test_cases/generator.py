# -*- coding: utf-8 -*-
#!/usr/bin/env python

# ./geng 1 -q |./vcolg -e0:1 -T -q
import subprocess as sp
import os
import sqlite3

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

def generate_color_graphs(cardinality,colors=0):
    geng = sp.Popen([nauty_path + "geng"] + [str(cardinality), "-q"], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    vcolg = sp.Popen([nauty_path + "vcolg"] + ["-e0:%s" % colors, "-T", "-q"], stdin=geng.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
    result=[]
    line=vcolg.stdout.readline().strip()
    while line:
        result.append(parse(line))
        line=vcolg.stdout.readline().strip()
    return result

def generate_database(path,maxcardinality,mincardinality=0):
    count = 0
    conn = sqlite3.connect(path)

    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE tests
                     (nnodes INT, nedges INT, ngensubisos INT, natomslindenbaum INT, time BIGINT, graph BLOB)''')
        c.execute('''CREATE TABLE register
                     (nnodes INT)''')
    except sqlite3.OperationalError:
        mincardinality = c.execute('SELECT * FROM register').fetchone()[0] + 1
        print "Already generated up to cardinality %s" % (mincardinality-1)
    
    try:
        for cardinality in range(mincardinality,maxcardinality+1):
            print "Generating cardinality %s..." % cardinality
            for g in generate_color_graphs(cardinality):
                c.execute("INSERT INTO tests VALUES (?, ?, ?, ?, ?, ?)", (g[0],g[1],None,None,None,str(g)))
                count += 1
            c.execute("delete from register")
            c.execute("INSERT INTO register VALUES (?)", (cardinality,))
            conn.commit()
            print "Generated %s graphs" % count
        conn.close()
    except KeyboardInterrupt:
        conn.close()


def main():
    path = raw_input("Path to db file[graphs.db]: ") or "graphs.db"
    maxcardinality = raw_input("Max cardinality[10]: ") or 10
    maxcardinality=int(maxcardinality)
    generate_database(path,maxcardinality)

if __name__ == "__main__":
    main()
