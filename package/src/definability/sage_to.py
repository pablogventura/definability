#!/usr/bin/env python
# -*- coding: utf8 -*-

import examples
import model
import fofunctions
from itertools import product


def sage_lattice_to_model(lat):
    """
    Convierte de un reticulado de sage a un modelo.
    """

    meet = [[[] for i in range(lat.cardinality())]
            for i in range(lat.cardinality())]
    join = [[[] for i in range(lat.cardinality())]
            for i in range(lat.cardinality())]

    for t in product(list(range(lat.cardinality())), repeat=2):
        meet[t[0]][t[1]] = lat.meet(*t)
        join[t[0]][t[1]] = lat.join(*t)

    meet = fofunctions.FO_Operation(meet)
    join = fofunctions.FO_Operation(join)

    return model.FO_Model(examples.tiporet, list(range(lat.cardinality())), {"v": join, "^": meet}, {})


def sage_poset_to_model(pos):
    """
    Convierte de un poset de sage a un modelo.
    """
    le = []
    for t in product(list(range(pos.cardinality())), repeat=2):
        if pos.le(*t):
            le.append(t)
    le = fofunctions.FO_Relation(le, list(range(pos.cardinality())))
    return model.FO_Model(examples.tipoposet, list(range(pos.cardinality())), {}, {"<=": le})
