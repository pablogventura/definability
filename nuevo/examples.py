#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
Modulo con ejemplos rapidos, para hacer pruebas
"""

from model import FO_Model
from fotype import FO_Type
from fofunctions import FO_Relation


tipoposet = FO_Type({},{"<=":2})

posetdiamante = FO_Model(tipoposet,5,{},{"<=":FO_Relation([[1,1,1,1,1],
                                                           [0,1,0,0,0],
                                                           [0,1,1,0,0],
                                                           [0,1,0,1,0],
                                                           [0,1,0,0,1]],
                                                           tipoposet,"<=")})

posetcadena2 = FO_Model(tipoposet, 2,{},{"<=":FO_Relation([[1, 0],
                                                           [1, 1]],tipoposet,"<=")})


if __name__ == "__main__":
    import doctest
    doctest.testmod()
