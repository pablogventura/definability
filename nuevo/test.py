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


def load_tests(loader, tests, ignore):
    modules = [config,examples,files,fofunctions,fotype,functions,minion,misc,model,morphisms]
    for module in modules:
        tests.addTests(doctest.DocTestSuite(module))
    return tests
    
if __name__ == '__main__':
    unittest.main()
