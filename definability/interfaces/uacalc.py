#!/usr/bin/env python
# -*- coding: utf8 -*-


from xml.etree import ElementTree
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
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

def operationUACALC(sym,op):
    op = Element('op')
    opSymbol = SubElement(op, 'opSymbol')
    opName = SubElement(opSymbol, 'opName')
    opName.text = str(sym)
    arity = SubElement(opSymbol, 'arity')
    arity.text = op.arity()

    opTable = SubElement(op, 'opTable')
    intArray = SubElement(opTable, 'intArray')
    table = op.table()
    row = SubElement(intArray, 'intArray',{'r':"[0]"})
    row.text = "0,0,0,0,0"

    return prettify(op)
