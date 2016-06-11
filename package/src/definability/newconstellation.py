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
    >>> (b,i) = is_open_definable(k,tiporet,tiporet+tipotest)
    >>> b
    False
    >>> isinstance(i,Isomorphism)
    True
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
    >>> is_open_definable(k,tiporet,tiporet+tipodistinto)
    (True, None)
    >>> (b,h) = is_open_positive_definable(k,tiporet,tiporet+tipodistinto)
    >>> b
    False
    >>> isinstance(h,Homomorphism)
    True
    """
    k,ce=preprocessing(k,subtype,supertype) # hago el preprosesamiento
    if ce:
        #encontre un contraejemplo durante el preprosesamiento
        return (False,ce)
    s=set()
    for a in sorted(k, key=len, reverse=True):
        for (i,b) in a.substructures(subtype): # hay que chequear que las devuelva de mayor a menor
            # i es una funcion de inclusion, no se si hace falta
            iso, ce = check_bihomos(b,s,subtype,supertype)
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

def check_bihomos(a,s,subtype,supertype):
    for b in ifilter(lambda x:len(a)==len(x),s):
        bihomos = a.homomorphisms_to(b,subtype,inj=True,surj=True)
        for h in bihomos:
            if h.is_embedding(): # ES EQUIVALENTE A QUE SEA EMBEDDING
                if h.preserves_type(supertype): # preserva como ISOMORFISMO
                    return (True,None)
                else:
                    #h es isomorfismo contraejemplo
                    return (True,h)
            elif not h.preserves_type(supertype): # no preserva como HOMOMORFISMO
                # h es homomorfismo contraejemplo
                return (False, h)
        if not bihomos: # no habia bihomos reviso en la otra direccion por cantor-bernstein
            assert len(bihomos) == 0 # por las dudas
            for h in b.homomorphisms_to(a,subtype,inj=True,surj=True):
                if not h.preserves_type(supertype):
                    # h es un homomorfismo contraejemplo
                    return (False,h)
    return (False,None)


def is_existential_definable(k, subtype, supertype):
    """
    Devuelve una tupla diciendo si es definible y un contrajemplo
    para la definibilidad existencial de supertype, en k con el subtype

    >>> from examples import *
    >>> k = {retrombo}
    >>> is_existential_definable(k,tiporet,tiporetacotado)
    (True, None)
    >>> (b,e) = is_open_definable(k,tiporet,tiporetacotado)
    >>> b
    False
    >>> isinstance(e,Embedding)
    True
    """
    k,ce=preprocessing(k,subtype,supertype) # hago el preprosesamiento
    if ce:
        #encontre un contraejemplo durante el preprosesamiento
        return (False,ce)
    s=set()
    for a,b in product(k,repeat=2):
        for emb in a.embeddings_to(b,subtype):
            if not emb.preserves_type(supertype):
                # emb es un embedding contrajemplo
                return (False, emb)
    return (True,None)

def is_existential_positive_definable(k, subtype, supertype):
    """
    Devuelve una tupla diciendo si es definible y un contrajemplo
    para la definibilidad existencial positiva de supertype, en k con el subtype

    >>> from examples import *
    >>> k = {retrombo}
    >>> is_existential_definable(k,tiporet,tiporetacotado)
    (True, None)
    >>> (b,h) = is_existential_positive_definable(k,tiporet,tiporetacotado) # parece que max, min no son def por extienciales positivas
    >>> b
    False
    >>> isinstance(h, Homomorphism)
    True
    """
    k,ce=preprocessing(k,subtype,supertype) # hago el preprosesamiento
    if ce:
        #encontre un contraejemplo durante el preprosesamiento
        return (False,ce)
    s=set()
    for a,b in product(k,repeat=2):
        for hom in a.homomorphisms_to(b,subtype):
            if not hom.preserves_type(supertype):
                # hom es un homomorfismo contrajemplo
                return (False, hom)
    return (True,None)

def is_definable(k, subtype, supertype):
    """
    Devuelve una tupla diciendo si es definible y un contrajemplo
    para la definibilidad de primer orden de supertype, en k con el subtype

    >>> from examples import *
    >>> k = {retrombo}
    >>> is_definable(k,tiporet,tiporetacotado)
    (True, None)
    >>> (b,a) = is_definable(k,tiporet,tiporet+tipotest2)
    >>> b
    False
    >>> isinstance(a,Isomorphism)
    True
    """
    k,ce=preprocessing(k,subtype,supertype) # hago el preprosesamiento
    if ce:
        #encontre un contraejemplo durante el preprosesamiento
        return (False,ce)
    s=set()
    for a in k:
        for aut in a.automorphisms(subtype):
            if not aut.preserves_type(supertype):
                # aut es un automorfismo contrajemplo
                return (False, aut)
    return (True,None)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
