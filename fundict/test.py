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
from examples import *
from morphisms import *


def load_tests(loader, tests, ignore):
    modules = [config,examples,files,fofunctions,fotype,functions,minion,misc,model,morphisms]
    for module in modules:
        tests.addTests(doctest.DocTestSuite(module))
    return tests

class Test(unittest.TestCase):

    def test_split(self):
        r13= list(retrombo.substructures(tiporet))[3]
        r12= list(retrombo.substructures(tiporet))[2]
        self.assertEqual(r13.cardinality,1)
        self.assertEqual(r12.cardinality,1)
        self.assertEqual(len(r13.embeddings_to(retrombo,tiporet)),4)
        self.assertEqual(len(r13.isomorphisms_to(retrombo,tiporet)),0)
        self.assertEqual(len(r13.homomorphisms_to(retrombo,tiporet)),4)
        self.assertIsInstance(r13.is_isomorphic(r12,tiporet), Isomorphism)
        r21= list(retrombo.substructures(tiporet))[4]
        r22= list(retrombo.substructures(tiporet))[5]
        self.assertEqual(r21.cardinality,2)
        self.assertEqual(r22.cardinality,2)
        self.assertIsInstance(r21.is_isomorphic(r22,tiporet),Isomorphism)
        self.assertEqual(len(r21.isomorphisms_to(r22,tiporet)),1)
        self.assertEqual(len(r21.homomorphisms_to(r22,tiporet)),3)

if __name__ == '__main__':
    unittest.main()
