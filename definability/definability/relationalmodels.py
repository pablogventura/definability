from itertools import combinations
from ..first_order.fotype import FO_Type
from ..definability.exceptions import Counterexample

def check_isos(a, s, subtype):
    for b in filter(lambda x: len(a) == len(x), s):
        iso = a.is_isomorphic(b, subtype)
        if iso:
            return iso

def calc_spectre(relation):
    result = set(len(set(t)) for t in relation)
    result = list(result)
    result.sort(reverse=True)
    return result


def is_open_def_rel(model, relation):
    model.relations["R"] = relation
    subtype = model.fo_type
    model.fo_type = model.fo_type + FO_Type({},{"R":relation.arity()})
    return is_open_def_rel_rec(model, calc_spectre(relation), subtype, model.fo_type, set())


def is_open_def_rel_rec(model, spectre, subtype, supertype, S):
    if not spectre:
        return True
    size = spectre[0]
    spectre = spectre[1:]
    
    for subu in combinations(model.universe,size):
        emb,subm = model.substructure(subu, model.fo_type)
        iso = check_isos(subm, S, subtype)
        if iso:
            if not iso.preserves_type(supertype):
                raise Counterexample(iso)
        else:
            S.add(subm)
            for aut in subm.automorphisms(subtype):
                if not aut.preserves_type(supertype):
                    raise Counterexample(aut)
            is_open_def_rel_rec(subm, spectre, subtype, supertype, S)
    return True

def dfs(model, relation):
    model.relations["R"] = relation
    subtype = model.fo_type
    model.fo_type = model.fo_type + FO_Type({},{"R":relation.arity()})
    supertype = model.fo_type
    
    
    spectre = calc_spectre(relation)
    size = spectre[0]

    subuniverses = list(combinations(model.universe,size))
    
    S = set()
    while subuniverses:
        subuniverse = subuniverses.pop()
        emb,subm = model.substructure(subuniverse, model.fo_type)
        iso = check_isos(subm, S, subtype)
        if iso:
            if not iso.preserves_type(supertype):
                raise Counterexample(iso)
        else:
            S.add(subm)
            for aut in subm.automorphisms(subtype):
                if not aut.preserves_type(supertype):
                    raise Counterexample(aut)
            try:
                size = next(x for x in spectre if x < len(subuniverse)) # EL SIGUIENTE EN EL ESPECTRO QUE SEA MAS CHICO QUE LEN DE SUBUNIVERSE
                subuniverses.extend(list(combinations(subuniverse,size)))
            except StopIteration:
                # no tiene mas hijos
                pass
    return True

