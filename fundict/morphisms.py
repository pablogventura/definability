#!/usr/bin/env python
# -*- coding: utf8 -*-

from functions import Function
from misc import indent

class Homomorphism(Function):
    """
    Homomorfismos
    
    >>> import examples
    >>> h = Homomorphism({(0,):1,(1,):1},examples.posetcadena2,examples.posetcadena2,examples.posetcadena2.fo_type)
    >>> print h
    Homeomorphism(
      [0] -> 1,
      [1] -> 1,
    ,
      FO_Type({},{'<=': 2})
    ,
    )
    """
    def __init__(self, d, source, target, subtype, inj=None, surj=None):
        super(Homomorphism, self).__init__(d)
        self.source = source
        self.target = target
        self.subtype = subtype
        self.inj = inj
        self.surj = surj
        assert self.arity() == 1
        assert self.subtype.is_subtype_of(source.fo_type) and self.subtype.is_subtype_of(target.fo_type)
        
        if self.is_auto():
            self.stype = "Homeomorphism"
        else:
            self.stype = "Homomorphism"

        
    def inverse(self):
        assert self.inj

        d = {}
        for k in self.dict:
            d[self.dict[k]]=k
        return type(self)(d,self.target,self.source,self.subtype,self.inj,self.surj)
        
    def composition(self,g):
        """
        Compone con otro morfismo, F.compone(G) = F o G
        y devuelve un nuevo morfismo
        El tipo del morfismo esta dado por el de menor 'grado' entre los dos
        """
        if issubclass(type(self),type(g)):
            morph_type = type(g)
        else:
            morph_type = type(self)
        
        result = morph_type.copy(g)
        result.map_in_place(self)
        return result
        
    def is_auto(self):
        """
        Es un 'auto-morfismo'?
        """
        return self.source == self.target
    def __repr__(self):
        result =  "%s(\n" % self.stype
        result += indent("\n".join(map(lambda x: "%s -> %s," % (x[:-1],x[-1]) ,self.table()))) + ",\n"
        #result += indent(repr(self.source) + ",")
        #result += indent(repr(self.target) + ",")
        result += indent(repr(self.subtype)) + ",\n"
        if self.inj:
            result += indent("Injective,")
        if self.surj:
            result += indent("Surjective,")
        result += ")"
        return result

class Embedding(Homomorphism):
    """
    Embeddings

    >>> import examples
    >>> h = Embedding({(0,):1,(1,):1},examples.posetcadena2,examples.posetcadena2,examples.posetcadena2.fo_type)
    >>> print h
    Autoembedding(
      [0] -> 1,
      [1] -> 1,
    ,
      FO_Type({},{'<=': 2})
    ,
      Injective,
    )
    """
    def __init__(self, d, source, target, subtype, inj=True, surj=None):
        assert inj
        super(Embedding, self).__init__(d,source,target,subtype,inj,surj)
        if self.is_auto():
            self.stype = "Autoembedding"
        else:
            self.stype = "Embedding"

class Isomorphism(Embedding):
    """
    Isomorfismos
    
    >>> import examples
    >>> h = Isomorphism({(0,):1,(1,):1},examples.posetcadena2,examples.posetcadena2,examples.posetcadena2.fo_type)
    >>> print h
    Automorphism(
      [0] -> 1,
      [1] -> 1,
    ,
      FO_Type({},{'<=': 2})
    ,
      Injective,
      Surjective,
    )

    """
    def __init__(self, d, source, target, subtype, inj=True, surj=True):
        assert inj and surj
        super(Isomorphism, self).__init__(d,source,target,subtype,inj,surj)
        if self.is_auto():
            self.stype = "Automorphism"
        else:
            self.stype = "Isomorphism"



if __name__ == "__main__":
    import doctest
    doctest.testmod()
