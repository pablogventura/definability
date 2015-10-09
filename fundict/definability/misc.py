#!/usr/bin/env python
# -*- coding: utf8 -*-

def indent(text):
    r"""
    Indenta un parrafo
    >>> print indent("hola\n  hola\nhola")
      hola
        hola
      hola
    <BLANKLINE>
    >>> print indent(indent("hola\n  hola\nhola"))
        hola
          hola
        hola
    <BLANKLINE>
    """
    text = "  " + text.strip("\n") 
    return text.replace('\n', '\n  ') + "\n"

def powerset(lst):
    """
    From http://rosettacode.org/wiki/Power_set#Python
    """
    # TODO generar desde el chico al grande, para no tener que ordenar al final
    result = [[]]
    for x in lst:
        # for every additional element in our set
        # the power set consists of the subsets that don't
        # contain this element (just take the previous power set)
        # plus the subsets that do contain the element (use list
        # comprehension to add [x] onto everything in the
        # previous power set)
        result.extend(sorted([subset + [x] for subset in result]))
    return sorted(result,key=len)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
