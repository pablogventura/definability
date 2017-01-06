# -*- coding: utf-8 -*-
#!/usr/bin/env python

# ./geng 1 -q |./vcolg -e0:1 -T -q
import subprocess as sp
import os
import sqlite3
import sys

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
    if cardinality <= 8:
        geng = sp.Popen([nauty_path + "geng"] + [str(cardinality), "-q"], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        vcolg = sp.Popen([nauty_path + "vcolg"] + ["-e0:%s" % colors, "-T", "-q"], stdin=geng.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
        result=[]
        line=vcolg.stdout.readline().strip()
        while line:
            result.append(parse(line))
            line=vcolg.stdout.readline().strip()
        return result
    else:
         #./genrang 2 10 | ./shortg
        result=[]
        genrang = sp.Popen([nauty_path + "genrang"] + [str(cardinality),"1000", "-q", "-S0"], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        shortg = sp.Popen([nauty_path + "shortg"] + ["-q"], stdin=genrang.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
        vcolg = sp.Popen([nauty_path + "vcolg"] + ["-e0:%s" % colors, "-T", "-q"], stdin=shortg.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
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
        c.execute("""CREATE TABLE graphs
                    (
                       graph BLOB,
                       id int NOT NULL,
                       nnodes int NOT NULL,
                       nedges int NOT NULL,
                       ncolors int NOT NULL,
                       ngensubisos INT,
                       timegensubisos REAL,
                       PRIMARY KEY (id)
                    )""")
        c.execute("""CREATE TABLE arities
                    (
                       graph_id int NOT NULL,
                       arity int NOT NULL,
                       natomslindenbaum int,
                       time REAL,
                       PRIMARY KEY (graph_id, arity),
                       FOREIGN KEY (graph_id) REFERENCES graphs(id)
                    )""")
    except sqlite3.OperationalError:
        print("Error: The file already exists")
        sys.exit(1)
    
    try:
        for cardinality in range(mincardinality,maxcardinality+1):
            print "Generating cardinality %s..." % cardinality
            for g in generate_color_graphs(cardinality):
                c.execute("INSERT INTO graphs VALUES (?, ?, ?, ?, ?, ?, ?)", (str(g),count,g[0],g[1],0,None,None))
                count += 1
            conn.commit()
            print "Generated %s graphs" % count
        conn.close()
    except KeyboardInterrupt:
        conn.close()


def main():
    print("""Graph Format: (#nodes, #edges, colors, edges)""")
    path = raw_input("Path to db file[graphs.db]: ") or "graphs.db"
    maxcardinality = raw_input("Max cardinality[50]: ") or 50
    maxcardinality=int(maxcardinality)
    generate_database(path,maxcardinality)

if __name__ == "__main__":
    main()
