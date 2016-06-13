#!/usr/bin/env python
# -*- coding: utf8 -*-
import networkx
from examples import *
from collections import defaultdict
from itertools import product, chain, combinations, permutations, ifilter
from morphisms import Isomorphism, Embedding, Homomorphism
from minion import ParallelMorphMinionSol
from model import FO_Model
from morphsgenerators import *

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
    for iso in k_isos_no_auts(k,subtype):
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
    for subiso in k_sub_isos(k, subtype):
        if not subiso.preserves_type(supertype):
            return (False, subiso)
    return (True,None)


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
    for subhom in k_sub_homs(k, subtype):
        if not subhom.preserves_type(supertype):
            return (False, subhom)
    return (True,None)

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
    for emb in k_embs(k, subtype):
        if not emb.preserves_type(supertype):
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
    for hom in k_homs(k, subtype):
        if not hom.preserves_type(supertype):
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
    for iso in k_isos(k, subtype):
        if not iso.preserves_type(supertype):
            return (False, iso)
    return (True,None)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
