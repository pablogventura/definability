#!/usr/bin/env python
# -*- coding: utf8 -*-
from ..examples import *
from itertools import product, combinations, permutations


def k_isos_no_auts(k, subtype):
    """
    Genera los isomorfismos entre estructuras distintas de k
    No incluye los automorfismos.
    """
    for (a, b) in combinations(k, 2):  # nunca con si mismo
        if a in k and b in k:  # si ya lo encontre isomorfo, no lo busco de nuevo
            iso = a.is_isomorphic(b, subtype)
            if iso:
                yield iso


def k_sub_isos(k, subtype):
    """
    Genera los isomorfismos entre subestructuras de k
    Necesita que k sea modulo isos del supertype
    """
    s = set()
    for a in sorted(k, key=len, reverse=True):
        # hay que chequear que las devuelva de mayor a menor
        for (i, b) in a.substructures(subtype):
            # i es una funcion de inclusion, no se si hace falta
            iso = check_isos(b, s, subtype)
            if iso:
                yield iso
                # TODO filtrar subestructuras de esta subestrucutra
            else:
                s.add(b)
                for aut in b.automorphisms(subtype):
                    yield aut


def check_isos(a, s, subtype):
    for b in filter(lambda x: len(a) == len(x), s):
        iso = a.is_isomorphic(b, subtype)
        if iso:
            return iso


def k_sub_homs(k, subtype):
    """
    Genera los homomorfismos entre subestructuras de k
    Necesita que k sea modulo isos del supertype
    """
    s = set()
    for a in sorted(k, key=len, reverse=True):
        # hay que chequear que las devuelva de mayor a menor
        for (i, b) in a.substructures(subtype):
            # i es una funcion de inclusion, no se si hace falta
            bihoms = False  # TODO LA LOGICA DE ESTO PODRIA MEJORARSE
            for bihom in check_bihomos(b, s, subtype):
                bihoms = True
                if bihom.is_embedding():  # es un isomorfismo
                    yield bihom
                    # TODO filtrar subestructuras de esta subestrucutra
                else:
                    yield bihom
                    s.add(b)
                    for aut in b.automorphisms(subtype):
                        yield aut
            if not bihoms:
                s.add(b)
                for aut in b.automorphisms(subtype):
                    yield aut

    for a, b in filter(lambda a_b: len(a_b[0]) > len(a_b[1]), permutations(s, 2)):
        # como len(a)>len(b) los homos sobre no son inyectivos
        for homo in a.homomorphisms_to(b, subtype, surj=True):
            yield homo


def check_bihomos(a, s, subtype):
    for b in filter(lambda x: len(a) == len(x), s):
        bihomos = a.homomorphisms_to(
            b, subtype, inj=True, surj=True)  # TODO HOMOS TO ANY
        for h in bihomos:
            if h.is_embedding():  # ES EQUIVALENTE A QUE SEA EMBEDDING
                yield h  # TODO lo retorna como ISOMORFISMO!!
                return
        # si no hubo isos empiezo a devolver los bihomos
        for h in bihomos:
            yield h
        # no habia bihomos reviso en la otra direccion por cantor-bernstein
        if not bihomos:
            assert len(bihomos) == 0  # por las dudas
            for h in b.homomorphisms_to(a, subtype, inj=True, surj=True):
                yield h


def k_embs(k, subtype):
    """
    Genera los embeddings entre estructuras de k
    Necesita que k sea modulo isos del supertype
    """
    for a, b in product(k, repeat=2):
        for emb in a.embeddings_to(b, subtype):
            yield emb


def k_homs(k, subtype):
    """
    Genera los homomorfismos entre estructuras de k
    Necesita que k sea modulo isos del supertype
    """
    for a, b in product(k, repeat=2):
        for hom in a.homomorphisms_to(b, subtype):
            yield hom


def k_isos(k, subtype):
    """
    Genera los isomorfismos entre estructuras de k
    Necesita que k sea modulo isos del supertype
    Incluye los automorfismos.
    """
    for a in k:
        for aut in a.automorphisms(subtype):
            yield aut

if __name__ == "__main__":
    import doctest
    doctest.testmod()
