#!/usr/bin/env python
# -*- coding: utf8 -*-

from ..interfaces.mace4 import Mace4Sol


class FO_Theory():
    FO_Theories = []
    FirstOrderClasses = []

    def __init__(self, abbr, name, axioms, results=[], options=[], syntax='Prover9'):
        """
        Define a first-order class of models by a list of first-order axioms

        INPUT:
            abbr    -- a short string without spaces abbreviating the name
            name    -- a string giving the name of the class
            axioms  -- list of strings in the given syntax
            results -- list of strings in the given syntax
            options -- list of strings defining the syntax
            syntax  -- a string indicating which program can parse the 
                       axioms, results and options
        """
        self.abbr = abbr
        self.name = name
        self.syntax = syntax
        self.axioms = axioms
        self.results = results
        self.options = options
        FO_Theory.FO_Theories.append(abbr)
        FO_Theory.FO_Theories.sort(key=str.lower)
        FO_Theory.FirstOrderClasses.append(name + " (" + abbr + ")")
        FO_Theory.FirstOrderClasses.sort(key=str.lower)

    def __repr__(self):
        """
        Display a first-order class in a way that can be parsed by Python
        
        >>> from definability.first_order import fotheories
        >>> print(fotheories.DLat)
        FO_Theory("Distributive lattices", syntax="Prover9", axioms=[ 
        "(x v y) v z = x v (y v z)",
        "x v y = y v x",
        "(x^y)^z = x^(y^z)",
        "x^y = y^x",
        "(x v y)^x = x",
        "(x^y) v x = x",
        "x^(y v z) = (x^y) v (x^z)"],
        results=[ 
        "x v (y^z) = (x v y)^(x v z)",
        "((x v y)^(x v z))^(y v z) = ((x^y)v(x^z))v(y^z)"])
        """
        st = 'FO_Theory(\"' + self.name + '\", syntax=\"' + self.syntax +\
             '\"' + ', axioms=[ \n\"' + '\",\n\"'.join(self.axioms) + '\"]'
        if self.options != []:
            st += ',\noptions=[ \n\"' + '\",\n\"'.join(self.options) + '\"]'
        if self.results != []:
            st += ',\nresults=[ \n\"' + '\",\n\"'.join(self.results) + '\"]'
        return st + ')'

    def subclass(self, abbr, name, arg, results=[], options=[]):
        """
        Add a list of axioms or another FO class to the current one.

        INPUT:
            abbr -- a short name (string) for the new FO subclass
            name -- a string naming the new FO subclass
            arg -- a list of axioms or an existing FO_Theory using same syntax
        """
        if type(arg) != list:
            arg = arg.axioms  # assume its another FO_Theory
        newaxioms = self.axioms + [a for a in arg if a not in self.axioms]
        return FO_Theory(abbr, name, newaxioms, results, options)


    def find_models(self, cardinality, seconds=60):
        """
        Find models of given (finite) cardinality for the axioms 
        of the FO_Theory self.
        """
        return Mace4Sol(self.axioms, mace_seconds=seconds, domain_cardinality=cardinality, options=self.options)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
