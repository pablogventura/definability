#!/usr/bin/env python
# -*- coding: utf8 -*-
from examples.examples import *
from collections import defaultdict
from itertools import product, chain, combinations, permutations
from functions.morphisms import Isomorphism, Embedding, Homomorphism
from interfaces.minion import ParallelMorphMinionSol
from first_order.model import FO_Model
from definability.morphsgenerators import *
from definability.exceptions import Counterexample

class Model_Family(object):
    def __init__(self, k):
        self.__k = defaultdict(list)
        for model in k:
            self.add(model)
    
    def add(self, model):
        self.__k[len(model)].append(model)
    
    def remove(self, model):
        self.__k[len(model)].remove(model)
    
    def __iter__(self):
        for cardinality in sorted(self.__k.keys(), reverse=True):
            for model in self.__k[cardinality]:
                yield model
    
    def __contains__(self, model):
        return model in self.__k[len(model)]

    def __len__(self):
        return sum(len(i) for i in self.__k.values())
    
    def without_isos(self, subtype, supertype):
        return Model_Family_woiso(self.__k, subtype, supertype)

    def is_open_definable(self, subtype, supertype):
        """
        Devuelve una tupla diciendo si es definible y un contrajemplo
        para la definibilidad abierta de supertype, en k con el subtype

        >>> from examples.examples import *
        >>> k = Model_Family([retrombo])
        >>> k.is_open_definable(tiporet,tiporet+tipoposet)
        (True, None)
        >>> (b,i) = k.is_open_definable(tiporet,tiporet+tipotest)
        >>> b
        False
        >>> isinstance(i,Isomorphism)
        True
        """
        for subiso in k_sub_isos(self.without_isos(subtype, supertype), subtype):
            if not subiso.preserves_type(supertype):
                return (False, subiso)
        return (True, None)


    def is_open_positive_definable(self, subtype, supertype):
        """
        Devuelve una tupla diciendo si es definible y un contrajemplo
        para la definibilidad abierta positiva de supertype, en k con el subtype

        >>> from examples.examples import *
        >>> k = Model_Family([retrombo])
        >>> k.is_open_definable(tiporet,tiporet+tipodistinto)
        (True, None)
        >>> (b,h) = k.is_open_positive_definable(tiporet,tiporet+tipodistinto)
        >>> b
        False
        >>> isinstance(h,Homomorphism)
        True
        """
        for subhom in k_sub_homs(self.without_isos(subtype, supertype), subtype):
            if not subhom.preserves_type(supertype, check_inverse=subhom.is_embedding()):
                return (False, subhom)
        return (True, None)


    def is_existential_definable(self, subtype, supertype):
        """
        Devuelve una tupla diciendo si es definible y un contrajemplo
        para la definibilidad existencial de supertype, en k con el subtype

        >>> from examples.examples import *
        >>> k = Model_Family([retrombo])
        >>> k.is_existential_definable(tiporet,tiporetacotado)
        (True, None)
        >>> (b,e) = k.is_open_definable(tiporet,tiporetacotado)
        >>> b
        False
        >>> isinstance(e,Embedding)
        True
        """
        for emb in k_embs(self.without_isos(subtype, supertype), subtype):
            if not emb.preserves_type(supertype):
                return (False, emb)
        return (True, None)


    def is_existential_positive_definable(self, subtype, supertype):
        """
        Devuelve una tupla diciendo si es definible y un contrajemplo
        para la definibilidad existencial positiva de supertype, en k con el subtype

        >>> from examples.examples import *
        >>> k = Model_Family([retrombo])
        >>> k.is_existential_definable(tiporet,tiporetacotado)
        (True, None)
        >>> (b,h) = k.is_existential_positive_definable(tiporet,tiporetacotado) # parece que max, min no son def por extienciales positivas
        >>> b
        False
        >>> isinstance(h, Homomorphism)
        True
        """
        for hom in k_homs(self.without_isos(subtype, supertype), subtype):
            if not hom.preserves_type(supertype):
                return (False, hom)
        return (True, None)


    def is_definable(self, subtype, supertype):
        """
        Devuelve una tupla diciendo si es definible y un contrajemplo
        para la definibilidad de primer orden de supertype, en k con el subtype

        >>> from examples.examples import *
        >>> k = Model_Family([retrombo])
        >>> k.is_definable(tiporet,tiporetacotado)
        (True, None)
        >>> (b,a) = k.is_definable(tiporet,tiporet+tipotest2)
        >>> b
        False
        >>> isinstance(a,Isomorphism)
        True
        """

        for iso in k_isos(self.without_isos(subtype, supertype), subtype):
            if not iso.preserves_type(supertype):
                return (False, iso)
        return (True, None)

class Model_Family_woiso(Model_Family):

    def __init__(self, d, subtype, supertype):
        super(Model_Family_woiso, self).__init__([])
        self._Model_Family__k = d.copy()
        self.__preprocessing(subtype,supertype)
        
    def add(self, model):
        raise NotImplementedError
        
    def __preprocessing(self, subtype, supertype):
        """
        Preprocesamiento para eliminar isomorfismos en k
        
        >>> from examples.examples import *
        >>> rettest10.join_to_le()
        >>> rettest102.join_to_le()
        >>> k= Model_Family([rettest10, rettest102])
        >>> len(k)
        2
        >>> len(k.without_isos(tiporet, tiporet + tipoposet))
        1
        """
        for iso in k_isos_no_auts(self, subtype):
            if not iso.preserves_type(supertype):
                raise Counterexample(iso)
            else:
                self.remove(iso.target)

        


if __name__ == "__main__":
    import doctest
    doctest.testmod()
