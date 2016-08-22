#!/usr/bin/env python
# -*- coding: utf8 -*-

import logging
import time
from unittest import TestCase

from definability.first_order import fotheories
from definability.first_order import formulas
from definability.definability import lindenbaum
from definability.definability.newconstellation2 import Model_Family

import subprocess

logging.basicConfig(format='%(asctime)s %(message)s', filename='history.log', level=logging.INFO)
repo_version = subprocess.check_output(["git", "rev-parse", "HEAD"])

class TestOld(TestCase):

    def setUp(self):
        self.graphs = fotheories.Graph.find_models(4)

    def test_len(self):
        self.assertEqual(len(self.graphs), 89) # hay 89 grafos
    
    def test_oldnewalgoritms(self):
        onew = 0
        oold = 0
        for i,g in enumerate(self.graphs):
            tick = time.time()
            new = sorted(list(formulas.bolsas(g,2).values()))
            tock = time.time() - tick
            onew += tock
            tick = time.time()
            old = sorted([list(d.values())[0] for d in lindenbaum.open_definable_lindenbaum(Model_Family([g]),2,g.fo_type)])
            tock = time.time() - tick
            oold += tock
            self.assertEqual(new, old) # las algebras de lindenbaum son iguales
        logging.info('version=%s, new_order=%s, old_order=%s, relation=%s' % (repo_version, onew/len(self.graphs),oold/len(self.graphs),(onew/len(self.graphs))/(oold/len(self.graphs)))) 


