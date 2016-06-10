#!/usr/bin/env python
# -*- coding: utf8 -*-
import networkx
from examples import *
from collections import defaultdict
from itertools import product, chain, combinations, ifilter
from morphisms import Isomorphism, Embedding, Homomorphism
from minion import ParallelMorphMinionSol
from model import FO_Model

def preprocessing(k,subtype,supertype):
    """
    >>> from examples import *
    >>> rettest10.join_to_le()
    >>> rettest102.join_to_le()
    >>> k= {rettest10, rettest102}
    >>> len(k)
    2
    >>> k,ce = preprocessing(k,tiporet, tiporet + tipoposet)
    >>> (len(k),ce)
    (1, None)
    """
    for (a,b) in combinations(k,2): # nunca con si mismo
        if {a,b} <= k: # si ya lo encontre isomorfo, no lo busco de nuevo
            iso = a.is_isomorphic(b,subtype)
            if iso:
                if iso.preserves_type(supertype):
                    k.remove(b)
                else:
                    return (k,iso)
    return (k,None)

def is_open_definable(k, subtype, supertype):
    """
    Devuelve una tupla diciendo si es definible y un contrajemplo
    para la definibilidad abierta de supertype, en k con el subtype

    >>> from examples import *
    >>> k = {retrombo}
    >>> is_open_definable(k,tiporet,tiporet+tipoposet)
    (True, None)
    >>> is_open_definable(k,tiporet,tiporet+tipotest)
    (False, Isomorphism(
      [2] -> 0,
    ,
      FO_Type({'v': 2, '^': 2},{})
    ,
      antitype= ['P']
    ,
      Injective,
      Surjective,
    ))
    """
    k,ce=preprocessing(k,subtype,supertype) # hago el preprosesamiento
    if ce:
        #encontre un contraejemplo durante el preprosesamiento
        return (False,ce)
    s=set()
    for a in sorted(k, key=len, reverse=True):
        for (i,b) in a.substructures(subtype): # hay que chequear que las devuelva de mayor a menor
            # i es una funcion de inclusion, no se si hace falta
            iso, ce = check_isos(b,s,subtype,supertype)
            if ce:
                # ce es un isomorfismo contraejemplo
                return (False, ce)
            elif iso:
                pass
                #TODO filtrar subestructuras de esta subestrucutra
            else:
                s.add(b)
                for aut in b.automorphisms(subtype):
                    if not aut.preserves_type(supertype):
                        # aut es un automorfismo contrajemplo
                        return (False, aut)
    return (True,None)

def check_isos(a,s,subtype,supertype):
    for b in ifilter(lambda x:len(a)==len(x),s):
        iso = a.is_isomorphic(b,subtype)
        if iso:
            if iso.preserves_type(supertype):
                return (True,None)
            else:
                #iso es un contraejemplo
                return (True,iso)
    return (False,None)

def is_open_positive_definable(k, subtype, supertype):
    """
    Devuelve una tupla diciendo si es definible y un contrajemplo
    para la definibilidad abierta positiva de supertype, en k con el subtype

    >>> from examples import *
    >>> k = {retrombo}
    >>> is_open_positive_definable(k,tiporet,tiporet+tipoposet)
    (True, None)
    >>> is_open_positive_definable(k,tiporet,tiporet+tipotest)
    (False, Isomorphism(
      [2] -> 0,
    ,
      FO_Type({'v': 2, '^': 2},{})
    ,
      antitype= ['P']
    ,
      Injective,
      Surjective,
    ))
    """
    k,ce=preprocessing(k,subtype,supertype) # hago el preprosesamiento
    if ce:
        #encontre un contraejemplo durante el preprosesamiento
        return (False,ce)
    s=set()
    for a in sorted(k, key=len, reverse=True):
        for (i,b) in a.substructures(subtype): # hay que chequear que las devuelva de mayor a menor
            # i es una funcion de inclusion, no se si hace falta
            iso, ce = check_isos(b,s,subtype,supertype) # TODO BIHOMOS
            if ce:
                # ce es un homomorfismo biyectivo o isomorfismo contraejemplo
                return (False, ce)
            elif iso:
                pass
                #TODO filtrar subestructuras de esta subestrucutra
            else:
                s.add(b)
                for aut in b.automorphisms(subtype):
                    if not aut.preserves_type(supertype):
                        # aut es un automorfismo contrajemplo
                        return (False, aut)
    for a,b in ifilter(lambda (a,b): len(a)>len(b), combinations(s,2)):
        # como len(a)>len(b) los homos sobre no son inyectivos
        for homo in a.homomorphisms_to(b, subtype, surj=True):
            if not homo.preserves_type(supertype):
                # homo es un homomorfismo sobreyectivo no inyectivo contraejemplo
                return (False,homo)
    return (True,None)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
