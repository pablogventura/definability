#!/usr/bin/env python
# -*- coding: utf8 -*-

import examples
import model
import fofunctions


def sage_lattice_to_model(lat):
    """
    Convierte de un reticulado de sage a un modelo.
    """
    meet = [list(r) for r in lat.meet_matrix().rows()]
    join = [list(r) for r in lat.join_matrix().rows()]

    meet = fofunctions.FO_Operation(meet)
    join = fofunctions.FO_Operation(join)

    return model.FO_Model(examples.tiporet, range(lat.cardinality()), {"v": join, "^": meet}, {})


def sage_poset_to_model(pos):
    """
    Convierte de un poset de sage a un modelo.
    """
    le = [list(r) for r in pos.lequal_matrix().rows()]
    le = fofunctions.FO_Relation(le, range(pos.cardinality()))
    return model.FO_Model(examples.tipoposet, range(pos.cardinality()), {}, {"<=":le})
