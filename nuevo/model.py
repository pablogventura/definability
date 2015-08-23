#!/usr/bin/env python
# -*- coding: utf8 -*-

class FO_Model(object):
    """
    Modelos de algun tipo de primer orden.
    """
    def __init__(self,fo_type, cardinality, operations, relations, universe=None):
        self.fo_type = fo_type
        self.cardinality = cardinality
        self.universe = universe # TODO en el futuro universe podria manejar renombres, para que los elementos puedan ser cualquier cosa
        assert sorted(operations.keys()) == sorted(fo_type.operations.keys()), "Estan mal definidas las funciones"
        assert sorted(relations.keys()) == sorted(fo_type.relations.keys()), "Estan mal definidas las relaciones"

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
