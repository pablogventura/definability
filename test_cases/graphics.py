# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sqlite3
import matplotlib.pyplot as plt

def main():
    path = input("Path to db file[graphs.db]: ") or "graphs.db"
    conn = sqlite3.connect(path)

    c = conn.cursor()
    c.execute('SELECT * FROM arities WHERE graph_id = 10')
    arities = []
    times = []
    for d in c:
        arities.append(d[1])
        times.append(d[3])
    
    conn.close()
    plt.plot(arities, times, '-')
    plt.axis([0, max(arities)+1, 0, max(times)*1.1])
    plt.ylabel('Seconds')
    plt.xlabel('Arity')
    plt.show()

if __name__ == "__main__":
    main()
