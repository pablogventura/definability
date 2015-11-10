#!/usr/bin/env python
# -*- coding: utf8 -*-

from itertools import imap, chain, combinations


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


def powerset(iterable):
    """
    Devuelve un generador que itera sobre partes del iterable,
    va de menor a mayor.

    >>> list(powerset([1,2,3]))
    [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]
    """
    s = list(iterable)
    return imap(list, chain.from_iterable(combinations(s, r) for r in range(len(s) + 1)))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
