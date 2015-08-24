#!/usr/bin/env python
# -*- coding: utf8 -*-

def indent(text):
    r"""
    Indenta un parrafo
    >>> print indent("hola\nhola\nhola")
      hola
      hola
      hola
    <BLANKLINE>
      
    """
    text = "  " + text.strip("\n") 
    return text.replace('\n', '\n  ') + "\n"


if __name__ == "__main__":
    import doctest
    doctest.testmod()
