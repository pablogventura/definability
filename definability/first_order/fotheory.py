#!/usr/bin/env python
# -*- coding: utf8 -*-

from ..interfaces.mace4 import Mace4Sol


class FO_Theory():

    def __init__(self, name, axioms, results=[], options=[]):
        """
        Define a first-order class of models by a list of first-order axioms

        INPUT:
            name    -- a string giving the name of the class
            axioms  -- list of strings in the given syntax
            results -- list of strings in the given syntax
            options -- list of strings defining the syntax
        """
        self.name = name
        self.axioms = axioms
        self.results = results
        self.options = options

    def __repr__(self):
        """
        Display a first-order class in a way that can be parsed by Python

        >>> from definability.first_order import fotheories
        >>> print(fotheories.DLat)
        FO_Theory("Distributive lattices", axioms=[
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
        st = 'FO_Theory(\"' + self.name + '\"' + ', axioms=[\n\"' + '\",\n\"'.join(self.axioms) + '\"]'
        if self.options != []:
            st += ',\noptions=[\n\"' + '\",\n\"'.join(self.options) + '\"]'
        if self.results != []:
            st += ',\nresults=[\n\"' + '\",\n\"'.join(self.results) + '\"]'
        return st + ')'

    def subclass(self, name, arg, results=[], options=[]):
        """
        Add a list of axioms or another FO class to the current one.

        INPUT:
            name -- a string naming the new FO subclass
            arg -- a list of axioms or an existing FO_Theory
        """
        if type(arg) != list:
            arg = arg.axioms  # assume its another FO_Theory
        newaxioms = self.axioms + [a for a in arg if a not in self.axioms]
        return FO_Theory(name, newaxioms, results, self.options + options)

    def find_models(self, cardinality):
        """
        Find models of given (finite) cardinality for the axioms
        of the FO_Theory self.
        """
        return Mace4Sol(self.axioms, domain_cardinality=cardinality, options=self.options)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
