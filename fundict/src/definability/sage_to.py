#!/usr/bin/env python
# -*- coding: utf8 -*-

import examples
import model

def sage_lattice_to_model(lat):
    """
    Convierte de un reticulado de sage a un modelo.
    """
    meet = [list(r) for r in lat.meet_matrix().rows()]
    join = [list(r) for r in lat.join_matrix().rows()]
    
    meet = model.FO_Operation(meet)
    join = model.FO_Operation(join)
    
    return model.FO_Model(examples.tiporet, range(lat.cardinality()),{"v":join,"^":meet},{})
    
