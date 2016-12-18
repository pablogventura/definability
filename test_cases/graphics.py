# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sqlite3
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np

def main():
    path = "graphs.db"
    conn = sqlite3.connect(path)

    c = conn.cursor()
    c.execute("""SELECT * FROM graphs INNER JOIN arities ON graphs.id=arities.graph_id
                 WHERE graphs.nnodes=3""")
    ('(1, 0, [0], [])', 0, 1, 0, 0, 1, None, 0, 0, 1, 0.0007132369973987807)
    
    data=defaultdict(list)

    for d in c:
        graph,graphid,nnodes,nedges,ncolors,ngensubisos,timegensubisos,_,arity,natomslindenbaum,timealgebra = d
        data[arity].append(timealgebra)

    arities=list(data.keys())
    times=[]
    for arity in arities:
        times.append(sum(data[arity])/len(data[arity]))
    arities = np.array(arities)
    times = np.array(times)
    conn.close()
    print (arities,times)
    plt.plot(arities, times, '-')
    plt.axis([0, max(arities)+1, 0, max(times)*1.1])
    plt.ylabel('Seconds')
    plt.xlabel('Arity')
    plt.show()

if __name__ == "__main__":
    main()
