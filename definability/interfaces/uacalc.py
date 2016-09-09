#!/usr/bin/env python
# -*- coding: utf8 -*-


from xml.etree import ElementTree
from xml.dom import minidom

from collections import defaultdict
from itertools import product
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem)
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
    
    
from xml.etree.ElementTree import Element, SubElement, Comment

"""
  <op>
    <opSymbol>
      <opName>meet</opName>
      <arity>2</arity>
    </opSymbol>
    <opTable>
      <intArray>
        <row r="[0]">0,0,0,0,0</row>
        <row r="[1]">0,1,0,0,1</row>
        <row r="[2]">0,0,2,0,2</row>
        <row r="[3]">0,0,0,3,3</row>
        <row r="[4]">0,1,2,3,4</row>
      </intArray>
    </opTable>
  </op>
"""

def modelUACALC(model,name):
    alg = Element('algebra')
    balg = SubElement(alg, 'basicAlgebra')
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

    return prettify(alg)
