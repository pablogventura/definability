#!/usr/bin/env python
# -*- coding: utf8 -*-

import time
from unittest import TestCase

from definability.first_order import fotheories
from definability.first_order import formulas
from definability.definability import lindenbaum
from definability.definability.newconstellation2 import Model_Family

class TestOld(TestCase):

    def setUp(self):
        self.graphs = fotheories.Graph.find_models(4)
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("%s: %.3f" % (self.id(), t))

    def test_len(self):
        self.assertEqual(len(self.graphs), 89) # hay 89 grafos
    
    def test_oldnewalgoritms(self):
        for g in self.graphs:
            new = sorted(list(formulas.bolsas(g,2).values()))
            old = sorted([list(d.values())[0] for d in lindenbaum.open_definable_lindenbaum(Model_Family([g]),2,g.fo_type)])
            self.assertEqual(new, old) # hay 89 grafos

