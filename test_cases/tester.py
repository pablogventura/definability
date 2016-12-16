# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sqlite3
import importlib.machinery

definability = importlib.machinery.SourceFileLoader('definability','../definability/__init__.py').load_module()
from definability.first_order.fofunctions import FO_Relation

def main():
    path = input("Path to db file[graphs.db]: ") or "graphs.db"
    conn = sqlite3.connect(path)

    c = conn.cursor()
    c.execute('SELECT * FROM graphs')
    for i,g in enumerate(c):
        universe,_,_,edges = eval(g[0])
        universe = range(universe)
        
        print((universe,edges))
        if i == 5:
            break

    conn.close()

if __name__ == "__main__":
    main()
