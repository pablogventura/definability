# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sqlite3
import importlib.machinery
import time

definability = importlib.machinery.SourceFileLoader('definability','../definability/__init__.py').load_module()
from definability import FO_Relation
from definability import FO_Type
from definability import FO_Model
k_sub_isos = definability.lindenbaum.morphsgenerators.k_sub_isos
Model_Family = definability.definability.newconstellation2.Model_Family
open_definable_lindenbaum_special = definability.definability.lindenbaum.open_definable_lindenbaum_special



def main():
    path = input("Path to db file[graphs.db]: ") or "graphs.db"
    conn = sqlite3.connect(path)
    graphsignature = FO_Type({},{"e":2})

    c = conn.cursor()
    c.execute('SELECT * FROM graphs')
    for i,g in enumerate(c):
        universe,_,_,edges = eval(g[0])
        rel = FO_Relation(edges+[(y,x) for x,y in edges],range(universe),arity=2)
        model = FO_Model(graphsignature,range(universe),{},{"e":rel})
        family= Model_Family({model})
        subisos_time = time.perf_counter()
        subisos = k_sub_isos(family,model.fo_type)
        subisos_time = time.perf_counter() - subisos_time
        
        for arity in range(len(model)):
            algebra_time = time.perf_counter()
            algebra = open_definable_lindenbaum_special(model, arity, model.fo_type,morphs=subisos)
            algebra_time = time.perf_counter() - algebra_time
            print((subisos_time,algebra_time))
        if i == 5:
            break
    conn.close()

if __name__ == "__main__":
    main()
