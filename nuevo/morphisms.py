#!/usr/bin/env python
# -*- coding: utf8 -*-

from functions import Function

class Morphism(Function):
    """
    Clase general de los morfismos
    """
    def __init__(self, l, source, target):
        super(Morphism, self).__init__(l)
        self.source = source
        self.target = target
        if self.is_auto():
            self.stype = "Automorphism"
        else:
            self.stype = "Morphism"

    def is_auto(self):
        """
        Es un 'auto-morfismo'?
        """
        return self.source == self.target
    def __repr__(self):
        
        result = super(Morphism, self).__repr__()
        result = result[len("Function("):-1]
        result += ",\n"
        result += repr(self.source) + ",\n"
        result += repr(self.target) + ")"
        return self.stype + "(\n" + result

class Homomorphism(Morphism):
    """
    Homomorfismos
    
    >>> import examples
    >>> h = Homomorphism([[1,1],[1,1]],examples.posetcadena2,examples.posetcadena2)
    >>> print h
    Homeomorphism(
    [
    [1 1],
    [1 1],
    ],
    FO_Model(
    FO_Type({},{'<=': 2}),
    2,
    {},
    {'<=': Function([
    [1 0],
    [1 1],
    ])}),
    FO_Model(
    FO_Type({},{'<=': 2}),
    2,
    {},
    {'<=': Function([
    [1 0],
    [1 1],
    ])}))
    """
    def __init__(self,l,source,target):
        super(Homomorphism, self).__init__(l,source,target)
        if self.is_auto():
            self.stype = "Homeomorphism"
        else:
            self.stype = "Homomorphism"

class Embedding(Homomorphism):
    """
    Embeddings

    >>> import examples
    >>> h = Embedding([[1,1],[1,1]],examples.posetcadena2,examples.posetcadena2)
    >>> print h
    Autoembedding(
    [
    [1 1],
    [1 1],
    ],
    FO_Model(
    FO_Type({},{'<=': 2}),
    2,
    {},
    {'<=': Function([
    [1 0],
    [1 1],
    ])}),
    FO_Model(
    FO_Type({},{'<=': 2}),
    2,
    {},
    {'<=': Function([
    [1 0],
    [1 1],
    ])}))
    """
    def __init__(self,l,source,target):
        super(Embedding, self).__init__(l,source,target)
        if self.is_auto():
            self.stype = "Autoembedding"
        else:
            self.stype = "Embedding"

class Isomorphism(Embedding):
    """
    Isomorfismos
    
    >>> import examples
    >>> h = Isomorphism([[1,1],[1,1]],examples.posetcadena2,examples.posetcadena2)
    >>> print h
    Automorphism(
    [
    [1 1],
    [1 1],
    ],
    FO_Model(
    FO_Type({},{'<=': 2}),
    2,
    {},
    {'<=': Function([
    [1 0],
    [1 1],
    ])}),
    FO_Model(
    FO_Type({},{'<=': 2}),
    2,
    {},
    {'<=': Function([
    [1 0],
    [1 1],
    ])}))
    """
    def __init__(self,l,source,target):
        super(Isomorphism, self).__init__(l,source,target)
        if self.is_auto():
            self.stype = "Automorphism"
        else:
            self.stype = "Isomorphism"



if __name__ == "__main__":
    import doctest
    doctest.testmod()
