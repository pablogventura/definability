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
    def __init__(self, d, source, target, subtype, antitype=[], inj=None, surj=None):
        super(Homomorphism, self).__init__(d)
        self.source = source
        self.target = target
        self.subtype = subtype
        self.antitype = antitype # lleva una lista de relaciones/operaciones que rompen el morfismo
        assert isinstance(antitype,list), type(antitype)
        self.inj = inj
        self.surj = surj
        assert self.arity() == 1
        #assert self.subtype.is_subtype_of(source.fo_type) and self.subtype.is_subtype_of(target.fo_type)
        
        if self.is_auto():
            self.stype = "Homeomorphism"
        else:
            self.stype = "Homomorphism"

        
    def inverse(self):
        """
        Devuelve la inversa del morfismo
        Para que sea funcion la inversa tiene que ser injectivo.
        """
        assert self.inj

        d = {}
        for k in self.dict:
            if len(k) > 1:
                d[(self.dict[k],)]=k
            else:
                d[(self.dict[k],)]=k[0]
        return type(self)(d,self.target,self.source,self.subtype, self.antitype,self.inj,self.surj)
        
    def composition(self,g):
        """
        Compone con otro morfismo, F.compone(G) = F o G
        y devuelve un nuevo morfismo
        El tipo del morfismo esta dado por el de menor 'grado' entre los dos
        El tipo de primer orden es el mas chico entre los dos.
        """
        assert set(g.target.universe).issubset(set(self.source.universe))
        if issubclass(type(g),type(self)): # el padre es el tipo menos restrictivo
            morph_type = type(self)
        else:
            morph_type = type(g)
        if self.subtype.is_subtype_of(g.subtype):
            subtype = self.subtype
        else:
            subtype = g.subtype     
        antitype = self.antitype + g.antitype
        
        result = morph_type(g.dict, g.source, self.target, subtype, antitype)
        result.map_in_place(self)
        
        result.inj = None
        result.surj = None
        if self.inj and g.inj:
            result.inj = True
        if self.surj and g.surj:
            result.surj = True
        
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
        if self.antitype:
            result += indent("antitype= " + repr(self.antitype)) + ",\n"
        if self.inj:
            result += indent("Injective,")
        if self.surj:
            result += indent("Surjective,")
        result += ")"
        return result
        
    def preserves_relation(self, rel):
        """
        Revisa si el homomorfismo preserva la relacion.
        
        Sean A un conjunto, R ⊆ Aⁿ y 𝛾:D ⊆ A → A una función.
        Diremos que 𝛾  preserva a R si para todo (a₁,...,aₙ) ∈ R∩Dⁿ
        se tiene que (𝛾(a₁),...,𝛾(aₙ)) ∈ R.
        
        >>> from examples import *
        >>> retrombo.is_homomorphic_image(retrombo, tiporet)
        Homeomorphism(
          [0] -> 0,
          [1] -> 0,
          [2] -> 0,
          [3] -> 0,
        ,
          FO_Type({'v': 2, '^': 2},{})
        ,
        )

        >>> h=retrombo.is_homomorphic_image(retrombo, tiporet)

        >>> h.preserves_relation("<=")
        True

        >>> h.preserves_relation("P")
        False
        """

        if rel in self.subtype.relations:
            return True
        elif rel in self.antitype:
            return False
        else:
            result = True
            for t in self.source.relations[rel].domain():
                if self.source.relations[rel](*t):
                    result = result and self.target.relations[rel](*self.vector_call(t))
            return result

    def inverse_preserves_rel(self, rel):
        """
        Prueba que ("<=_b" interseccion Im(f)^aridad(<=_b)) este contenido en f("<=_a")
        Funcion de Camper
        """
        if rel in self.subtype.relations:
            return True
        elif rel in self.antitype:
            return False
        else:
            frelSource = [map(lambda x: self(x), row) for row in self.source.relations[rel].table()]
            for row in self.target.relations[rel].table():
                if all(x in self.image() for x in row):
                    if not row in frelSource:
                        return False
            return True

    def preserves_type(self, supertype, check_inverse=False):
        """
        Revisa que el homomorfismo tambien sea un homomorfismo para el supertipo.
        
        Revisa preservacion de las relaciones que tiene supertype, que no tiene el morfismo en su tipo.
        Si preserva el tipo, se cambia de tipo a ese.

        >>> from examples import *
        >>> retrombo.is_homomorphic_image(retrombo, tiporet)
        Homeomorphism(
          [0] -> 0,
          [1] -> 0,
          [2] -> 0,
          [3] -> 0,
        ,
          FO_Type({'v': 2, '^': 2},{})
        ,
        )

        >>> h=retrombo.is_homomorphic_image(retrombo, tiporet)

        >>> h.preserves_type(tiporet+tipoposet)
        True

        >>> h.preserves_type(tiporet+tipotest)
        False
        """

        checktype = supertype - self.subtype
        assert not checktype.operations # no tiene que haber diferencia en las operaciones con el supertipo
        
        for rel in checktype.relations:
            if not self.preserves_relation(rel) or (check_inverse and not self.inverse_preserves_rel(rel)):
                self.antitype.append(rel)
                return False
        
        self.subtype = supertype # se auto promueve a un homo del supertipo
        return True  
            
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
    def __init__(self, d, source, target, subtype, antitype=[], inj=True, surj=None):
        assert inj
        super(Embedding, self).__init__(d,source,target,subtype, antitype, inj,surj)
        if self.is_auto():
            self.stype = "Autoembedding"
        else:
            self.stype = "Embedding"
    
    def isomorphism_to_image(self):
        """
        Devuelve un isomorfismo a la imagen del embedding.
        """
        return Isomorphism(self.dict,self.source,self.target.restrict(list(self.image()),self.subtype),self.subtype, self.antitype)

    def preserves_type(self, supertype, check_inverse=True):
        return super(Embedding, self).preserves_type(supertype,check_inverse)
       
        

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
    def __init__(self, d, source, target, subtype, antitype=[], inj=True, surj=True):
        assert inj and surj
        super(Isomorphism, self).__init__(d,source,target,subtype,antitype,inj,surj)
        if self.is_auto():
            self.stype = "Automorphism"
        else:
            self.stype = "Isomorphism"




if __name__ == "__main__":
    import doctest
    doctest.testmod()
