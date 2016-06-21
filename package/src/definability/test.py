#!/usr/bin/env python
# -*- coding: utf8 -*-

import coverage
import glob
cv = coverage.Coverage(include=glob.glob("*.py"))
cv.start()

import unittest
import doctest

import config
import examples
import files
import fofunctions
import fotheories
import fotheory
import fotype
import functions
import mace4
import minion
import misc
import model
import morphisms
import morphsgenerators
import newconstellation2
import lindenbaum


def load_tests(loader, tests, ignore):
    modules = [config, examples, files, fofunctions, fotheories, fotheory, fotype, functions, mace4, minion, misc, model, morphisms,
               morphsgenerators, newconstellation2, lindenbaum]
    for module in modules:
        tests.addTests(doctest.DocTestSuite(module))
    return tests


if __name__ == '__main__':
    unittest.main(exit=False,failfast=True)
    print("=" * 80)
    print("Coverage:")
    cv.stop()
    cv.report(show_missing=True)
