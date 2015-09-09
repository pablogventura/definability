#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
Modulo con ejemplos rapidos, para hacer pruebas
"""

from model import FO_Model
from fotype import FO_Type
from fofunctions import FO_Relation, FO_Operation


tipoposet = FO_Type({},{"<=":2})
tiporet = FO_Type({"^":2,"v":2},{})
tiporetacotado = FO_Type({"^":2,"v":2, "Max":1,"Min":1},{})
tipotest = FO_Type({},{"P":1,"<=":2})

posetdiamante = FO_Model(tipoposet,range(5),{},{"<=":FO_Relation({(0, 0): 1,
                                                                  (0, 1): 1,
                                                                  (0, 2): 1,
                                                                  (0, 3): 1,
                                                                  (0, 4): 1,
                                                                  (1, 0): 0,
                                                                  (1, 1): 1,
                                                                  (1, 2): 0,
                                                                  (1, 3): 0,
                                                                  (1, 4): 0,
                                                                  (2, 0): 0,
                                                                  (2, 1): 1,
                                                                  (2, 2): 1,
                                                                  (2, 3): 0,
                                                                  (2, 4): 0,
                                                                  (3, 0): 0,
                                                                  (3, 1): 1,
                                                                  (3, 2): 0,
                                                                  (3, 3): 1,
                                                                  (3, 4): 0,
                                                                  (4, 0): 0,
                                                                  (4, 1): 1,
                                                                  (4, 2): 0,
                                                                  (4, 3): 0,
                                                                  (4, 4): 1}
                                                                 )})

posetcadena2 = FO_Model(tipoposet, range(2),{},{"<=":FO_Relation({(0, 0): 1, (0, 1): 0, (1, 0): 1, (1, 1): 1})})


retrombo = FO_Model(tiporetacotado,range(4), {'^': FO_Operation({(0, 0): 0,
                                                                 (0, 1): 0,
                                                                 (0, 2): 0,
                                                                 (0, 3): 0,
                                                                 (1, 0): 0,
                                                                 (1, 1): 1,
                                                                 (1, 2): 2,
                                                                 (1, 3): 3,
                                                                 (2, 0): 0,
                                                                 (2, 1): 2,
                                                                 (2, 2): 2,
                                                                 (2, 3): 0,
                                                                 (3, 0): 0,
                                                                 (3, 1): 3,
                                                                 (3, 2): 0,
                                                                 (3, 3): 3}),
                                              'v': FO_Operation({(0, 0): 0,
                                                                 (0, 1): 1,
                                                                 (0, 2): 2,
                                                                 (0, 3): 3,
                                                                 (1, 0): 1,
                                                                 (1, 1): 1,
                                                                 (1, 2): 1,
                                                                 (1, 3): 1,
                                                                 (2, 0): 2,
                                                                 (2, 1): 1,
                                                                 (2, 2): 2,
                                                                 (2, 3): 1,
                                                                 (3, 0): 3,
                                                                 (3, 1): 1,
                                                                 (3, 2): 1,
                                                                 (3, 3): 3}
                                                                ),
                                              "Max":FO_Operation({():1}),
                                              "Min":FO_Operation({():0}),
                                             },
                                             {'<=': FO_Relation({(0, 0): 1,
                                                                 (0, 1): 1,
                                                                 (0, 2): 1,
                                                                 (0, 3): 1,
                                                                 (1, 0): 0,
                                                                 (1, 1): 1,
                                                                 (1, 2): 0,
                                                                 (1, 3): 0,
                                                                 (2, 0): 0,
                                                                 (2, 1): 1,
                                                                 (2, 2): 1,
                                                                 (2, 3): 0,
                                                                 (3, 0): 0,
                                                                 (3, 1): 1,
                                                                 (3, 2): 0,
                                                                 (3, 3): 1}
                                                                ),
                                              "P":FO_Relation({(0,):0,(1,):0,(2,):1,(3,):1}) # Relacion de prueba
                                             })


if __name__ == "__main__":
    import doctest
    doctest.testmod()
