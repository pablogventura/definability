#!/usr/bin/env python
# -*- coding: utf8 -*-

import coverage
import glob
cv = coverage.Coverage(include=glob.glob("*.py"))
cv.start()

import unittest
import doctest

import config, examples, files, fofunctions, fotheories, fotheory, fotype, functions, mace4, minion, misc, model, morphisms, morphsgenerators, newconstellation2



def load_tests(loader, tests, ignore):
    modules = [config, examples, files, fofunctions, fotheories, fotheory, fotype, functions, mace4, minion, misc, model, morphisms,
               morphsgenerators, newconstellation2]
    for module in modules:
        tests.addTests(doctest.DocTestSuite(module))
    return tests


if __name__ == '__main__':
    unittest.main(exit=False)
    print "=" * 80
    print "Coverage:"
    cv.stop()
    cv.report()
