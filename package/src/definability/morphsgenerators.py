#!/usr/bin/env python
# -*- coding: utf8 -*-
import networkx
from examples import *
from collections import defaultdict
from itertools import product, chain, combinations, permutations, ifilter
from morphisms import Isomorphism, Embedding, Homomorphism
from minion import ParallelMorphMinionSol
from model import FO_Model

def k_isos_no_auts(k,subtype):
    """
    Genera los isomorfismos entre estructuras distintas de k
    No incluye los automorfismos.
    """
    for (a,b) in combinations(k,2): # nunca con si mismo
        if {a,b} <= k: # si ya lo encontre isomorfo, no lo busco de nuevo
            iso = a.is_isomorphic(b,subtype)
            if iso:
                yield iso
                k.remove(b)

def k_sub_isos(k, subtype):
    """
    Genera los isomorfismos entre subestructuras de k
    """
    for iso in k_isos_no_auts(k,subtype):
        yield iso

    s=set()
    for a in sorted(k, key=len, reverse=True):
        for (i,b) in a.substructures(subtype): # hay que chequear que las devuelva de mayor a menor
            # i es una funcion de inclusion, no se si hace falta
            iso = check_isos(b,s,subtype)
            if iso:
                yield iso
                #TODO filtrar subestructuras de esta subestrucutra
            else:
                s.add(b)
                for aut in b.automorphisms(subtype):
                    yield aut

def check_isos(a,s,subtype):
    for b in ifilter(lambda x:len(a)==len(x),s):
        iso = a.is_isomorphic(b,subtype)
        if iso:
            return iso

def k_sub_homs(k, subtype):
    """
    Genera los homomorfismos entre subestructuras de k
    """
    for iso in k_isos_no_auts(k,subtype):
        yield iso
    s=set()
    for a in sorted(k, key=len, reverse=True):
        for (i,b) in a.substructures(subtype): # hay que chequear que las devuelva de mayor a menor
            # i es una funcion de inclusion, no se si hace falta
            for bihom in check_bihomos(b,s,subtype,supertype):
                yield bihom
                if bihom.is_embedding: # es un isomorfismo
                    pass
                    #TODO filtrar subestructuras de esta subestrucutra
                else:
                    s.add(b)
                    for aut in b.automorphisms(subtype):
                        yield aut
    for a,b in ifilter(lambda (a,b): len(a)>len(b), permutations(s,2)):
        # como len(a)>len(b) los homos sobre no son inyectivos
        for homo in a.homomorphisms_to(b, subtype, surj=True):
            yield homo

def check_bihomos(a,s,subtype):
    for b in ifilter(lambda x:len(a)==len(x),s):
        bihomos = a.homomorphisms_to(b,subtype,inj=True,surj=True)
        for h in bihomos:
            if h.is_embedding(): # ES EQUIVALENTE A QUE SEA EMBEDDING
                yield h # TODO lo retorna como ISOMORFISMO!!
                return
        # si no hubo isos empiezo a devolver los bihomos
        for h in bihomos:
            yield h
        if not bihomos: # no habia bihomos reviso en la otra direccion por cantor-bernstein
            assert len(bihomos) == 0 # por las dudas
            for h in b.homomorphisms_to(a,subtype,inj=True,surj=True):
                yield h


def k_embs(k, subtype):
    """
    Genera los embeddings entre estructuras de k
    """
    for iso in k_isos_no_auts(k,subtype):
        yield iso
    s=set()
    for a,b in product(k,repeat=2):
        for emb in a.embeddings_to(b,subtype):
            yield emb

def k_homs(k, subtype):
    """
    Genera los homomorfismos entre estructuras de k
    """
    for iso in k_isos_no_auts(k,subtype):
        yield iso
    s=set()
    for a,b in product(k,repeat=2):
        for hom in a.homomorphisms_to(b,subtype):
            yield hom

def k_isos(k, subtype):
    """
    Genera los isomorfismos entre estructuras de k
    Incluye los automorfismos.
    """
    for iso in k_isos_no_auts(k,subtype):
        yield iso
    s=set()
    for a in k:
        for aut in a.automorphisms(subtype):
            yield aut

if __name__ == "__main__":
    import doctest
    doctest.testmod()
