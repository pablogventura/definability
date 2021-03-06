#!/usr/bin/env python
# -*- coding: utf8 -*-


from xml.etree import ElementTree
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment

from collections import defaultdict
from itertools import product

from ..first_order.model import FO_Product

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem)
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")    

"""
<algebra>
  <productAlgebra>
    <algName>Prod of r^3</algName>
    <cardinality>64</cardinality>
    <factors>
      <factor>
"""


def model_to_UACALC_file(model,name,path):
    f=open(path,"w")
    f.write(modelUACALC(model,name))
    f.close()
    

def modelUACALC(model,name):
    alg = Element('algebra')
    if isinstance(model,FO_Product):
        factors = model.factors
        palg = SubElement(alg, 'productAlgebra')
        nalg = SubElement(palg, "algName")
        nalg.text = str(name)
        calg = SubElement(palg, "cardinality")
        calg.text = str(len(model))
        for f in factors:
            fact = SubElement(palg, "factor")
            basicAlgebraUACALC(f,"h",fact)
    else:
        basicAlgebraUACALC(model,name,alg)
    return prettify(alg)

def basicAlgebraUACALC(model,name,xmlfather):

    balg = SubElement(xmlfather, 'basicAlgebra')
    algname = SubElement(balg, 'algName')
    algname.text = str(name)
    algcard = SubElement(balg, 'cardinality')
    algcard.text = str(len(model))
    operations = SubElement(balg, 'operations')
    for sym in model.operations:

        op = SubElement(operations,'op')
        opSymbol = SubElement(op, 'opSymbol')
        opName = SubElement(opSymbol, 'opName')
        opName.text = str(sym)
        arity = SubElement(opSymbol, 'arity')
        arity.text = str(model.operations[sym].arity())

        opTable = SubElement(op, 'opTable')
        intArray = SubElement(opTable, 'intArray')
        ntable = defaultdict(list)


        for r in product(range(len(model)), repeat=model.operations[sym].arity()):
            ntable[r[:-1]].append(model.operations[sym](*r))
            
        for r in sorted(ntable.keys()):
            if len(r) > 0:
                row = SubElement(intArray, 'row',{'r':str(list(r))})
            else:
                row = SubElement(intArray, 'row')
            row.text = str(ntable[r])[1:-1].replace(" ","")

    return balg


import execnet
from os.path import expanduser
from ..interfaces import config
def congruencesUACALC(model):
    model_to_UACALC_file(model,"test","test.ua")
    gw = execnet.makegateway("popen//python=%sjython"%config.jython_path)
    channel = gw.remote_exec("""
        import sys

        sys.path.append("%suacalc.jar")
        sys.path.append("%sLatDraw.jar")

        from org.uacalc.alg import BasicAlgebra
        from org.uacalc.io import AlgebraIO
        from org.uacalc.alg import Malcev
        from org.uacalc.alg.conlat import BasicPartition
        
        f3 = AlgebraIO.readAlgebraFile("test.ua")
        conlat = f3.con()
        congruencia = conlat.Cg(0,2) # la congruencia mas chica que tiene al (0,2)
        
        channel.send(congruencia.toString())
    """ % (config.uacalccli_path,config.uacalccli_path))
    return list(channel)[0]
