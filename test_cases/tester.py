# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sqlite3
import importlib.machinery
import time
import sys

definability = importlib.machinery.SourceFileLoader('definability','../definability/__init__.py').load_module()
from definability import FO_Relation
from definability import FO_Type
from definability import FO_Model
k_sub_isos = definability.lindenbaum.morphsgenerators.k_sub_isos
Model_Family = definability.definability.newconstellation2.Model_Family
open_definable_lindenbaum_special = definability.definability.lindenbaum.open_definable_lindenbaum_special


def main():
    print("tester.py totalparallelprocess thisprocessid")
    path = input("Path to db file[graphs.db]: ") or "graphs.db"
    conn = sqlite3.connect(path)
    graphsignature = FO_Type({},{"e":2})

    c = conn.cursor()
    w = conn.cursor()
    numberofinstances= sys.argv[1]
    instance=sys.argv[2]
    c.execute("SELECT * FROM graphs where (graphs.id % " + numberofinstances + ") = " + instance)
    try:
        for i,g in enumerate(c):
            graphid = g[1]
            print(g)
            universe,_,_,edges = eval(g[0])
            rel = FO_Relation(edges+[(y,x) for x,y in edges],range(universe),arity=2)
            model = FO_Model(graphsignature,range(universe),{},{"e":rel})
            family= Model_Family({model})
            subisos_time = time.perf_counter()
            subisos = list(k_sub_isos(family,model.fo_type))
            subisos_time = time.perf_counter() - subisos_time

            w.execute("UPDATE graphs SET ngensubisos = ? WHERE id = ?",(len(subisos),graphid))
            for arity in range(len(model)+1):
                algebra_time = time.perf_counter()
                algebra = open_definable_lindenbaum_special(model, arity, model.fo_type,morphs=subisos)
                algebra_time = time.perf_counter() - algebra_time
                print((subisos_time,algebra_time,len(model)+1,graphid,arity))
                print("%s of %s, %s percent..." % (graphid,433366/numberofinstances,graphid/(433366/numberofinstances)))
                
                w.execute("INSERT INTO arities VALUES (?, ?, ?, ?)", (graphid,arity,len(algebra),algebra_time))
        conn.commit()
        conn.close()
    except KeyboardInterrupt:
        conn.commit()
        conn.close()

if __name__ == "__main__":
    main()
