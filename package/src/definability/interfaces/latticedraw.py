#!/usr/bin/env python
# -*- coding: utf8 -*-


import subprocess as sp
from select import poll, POLLIN

from ..functions.morphisms import Homomorphism, Embedding, Isomorphism
from ..interfaces import config
from ..interfaces import files
from itertools import product
from collections import defaultdict
from ..misc import misc


class LatDraw(object):
    count = 0

    def __init__(self, lattice):
        """
        Toma el input para minion, si espera todas las soluciones y una funcion para aplicar
        a las listas que van a ir siendo soluciones.
        """
        self.id = LatDraw.count
        self.lattice = lattice

        LatDraw.count += 1
        self.input_filename = config.lat_draw_path + "input_lat_draw%s" % self.id

        files.create_pipe(self.input_filename)
        "java -jar dist/lib/LatDraw.jar examples/prueba.lat"
        self.app = sp.Popen(["java","-jar",config.lat_draw_path + "LatDraw.jar", self.input_filename],
                                  stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        files.write(self.input_filename, self.generate_lat_file())
        self.EOF = False
        self.solutions = []

    def generate_lat_file(self):

        """
        (
          (0 (a b c))
          (a (1))
          (b (1))
          (c (1))
          (1 ())
        )"""
        l = self.lattice
        l.join_to_le()
        result = ""
        espacio = " "
        result+="\n"
        result+="(\n"
        for e in l.universe:
            result+="  (%s (%s))\n" % (e, espacio.join(str(r[1]) for r in l.relations["<="].table() if r[0]==e))
        result+=")\n"
        return result



if __name__ == "__main__":
    import doctest
    doctest.testmod()
