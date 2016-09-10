# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""An example of how to embed an IPython shell into a running program.

Please see the documentation in the IPython.Shell module for more details.

The accompanying file embed_class_short.py has quick code fragments for
embedding which you can cut and paste in your code once you understand how
things work.

The code in this file is deliberately extra-verbose, meant for learning."""
from __future__ import print_function

# The basics to get you going:

# IPython injects get_ipython into builtins, so you can know if you have nested
# copies running.

# Try running this code both at the command line and from inside IPython (with
# %run example-embed.py)
from traitlets.config import Config
from definability import *
import random



def generador(n, e1,e2,a,b,c):
    tipo = FO_Type({'0': 0,'1': 0,'t': 0,'b': 0, "u":3, "u1":1, "u2":1, "u3":1},{})
    universo = range(n) 
    ops = {}
    ops["0"] = FO_Constant(0)
    ops["1"] = FO_Constant(1) 
    ops["b"] = FO_Constant(2)
    ops["t"] = FO_Constant(3)
    
    def u(z,x,y):
        if z == 0:
            return x
        elif z == 1:
            return y
        else:
            return z
    
    ops["u"] = FO_Operation(u,d_universe=universo)
    
    u1=[random.randrange(n) for i in range(n)]
    u1[2]=0
    u1[3]=e1
    
    u2=[random.randrange(n) for i in range(n)]
    u2[2]=e2
    u2[3]=e1
    
    u3=[random.randrange(n) for i in range(n)]
    u3[3]=1
    u3[2]=e2
    

    ops["u1"]=FO_Operation(u1,d_universe=universo)
    ops["u2"]=FO_Operation(u2,d_universe=universo)
    ops["u3"]=FO_Operation(u3,d_universe=universo)
    
    return FO_Model(tipo, universo, ops, {}, name='')

random.seed(0)

algebra = generador(10,4,5,6,7,8)

h = algebra **2

# s ya no es un producto sino una subestructura
s = h.substructure(h.subuniverse([(2,3),(3,2),(6,7),(6,8)],h.fo_type)[0],h.fo_type)[1]

from definability.interfaces import uacalc

print ("\n\n" + uacalc.congruencesUACALC(examples.retrombo**2))




