#!/usr/bin/env python
# -*- coding: utf8 -*-

import unittest
import doctest
import config
import examples
import files
import fofunctions
import fotype
import functions
import minion
import misc
import model
import morphisms
import constellation
from examples import *
from morphisms import *
from datetime import datetime


def load_tests(loader, tests, ignore):
    modules = [config,examples,files,fofunctions,fotype,functions,minion,misc,model,morphisms,constellation]
    for module in modules:
        tests.addTests(doctest.DocTestSuite(module))
    return tests

class Test(unittest.TestCase):

    def test_split(self):
        
        r13= list(retrombo.substructures(tiporet))[3][1]
        r12= list(retrombo.substructures(tiporet))[2][1]
        self.assertEqual(r13.cardinality,1)
        self.assertEqual(r12.cardinality,1)
        self.assertEqual(len(r13.embeddings_to(retrombo,tiporet)),4)
        self.assertEqual(len(r13.isomorphisms_to(retrombo,tiporet)),0)
        self.assertEqual(len(r13.homomorphisms_to(retrombo,tiporet)),4)
        self.assertIsInstance(r13.is_isomorphic(r12,tiporet), Isomorphism)
        r21= list(retrombo.substructures(tiporet))[4][1]
        r22= list(retrombo.substructures(tiporet))[5][1]
        self.assertEqual(r21.cardinality,2)
        self.assertEqual(r22.cardinality,2)
        self.assertIsInstance(r21.is_isomorphic(r22,tiporet),Isomorphism)
        self.assertEqual(len(r21.isomorphisms_to(r22,tiporet)),1)
        self.assertEqual(len(r21.homomorphisms_to(r22,tiporet)),3)
        
    def test_open_definable_one_planet(self):
        from constellation import Constellation
        habia = minion.MinionSol.count
        
        rettest10.join_to_le()
        c = Constellation()
        c.add_planet(rettest10)
        tick = datetime.now()
        self.assertEqual(c.is_open_definable(tiporet,tiporet+tipoposet),(True,None))
        tock = datetime.now()   
        diff = tock - tick    # the result is a datetime.timedelta object
        self.assertEqual((len(c.graph.edges()),len(c.graph.nodes())),(2364,26))
        print "is_open_definable tomo %s segundos" % diff.total_seconds()
        print "Genero %s flechas entre %s nodos" % (len(c.graph.edges()),len(c.graph.nodes()))
        print "Hubo %s llamadas a minion" % (minion.MinionSol.count-habia)

    def test_open_definable_multi_planet(self):
        from constellation import Constellation
        habia = minion.MinionSol.count
        
        rettest10.join_to_le()
        rettest102.join_to_le()
        c = Constellation()
        c.add_planet(rettest10)
        c.add_planet(rettest102)
        tick = datetime.now()
        self.assertEqual(c.is_open_definable(tiporet,tiporet+tipoposet),(True,None))
        tock = datetime.now()   
        diff = tock - tick    # the result is a datetime.timedelta object
        planets = reduce(lambda x,y:x+y,c.planets.values())
        satellites = reduce(lambda x,y:x+y,c.satellites.values())
        todos = planets + satellites
        for x in todos:
            for y in todos:
                if x != y:
                    for flecha in c.arrows(x,y):
                        self.assertIsInstance(flecha, morphisms.Embedding)
        
        self.assertEqual((len(c.graph.edges()),len(c.graph.nodes())),(2364,26))
        print "is_open_definable con 2 planets tomo %s segundos" % diff.total_seconds()
        print "Genero %s flechas entre %s nodos" % (len(c.graph.edges()),len(c.graph.nodes()))
        print "Hubo %s llamadas a minion" % (minion.MinionSol.count-habia)
        
if __name__ == '__main__':
    unittest.main()
