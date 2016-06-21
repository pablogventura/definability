#!/usr/bin/env python
# -*- coding: utf8 -*-

import coverage
import glob
cv = coverage.Coverage(include=glob.glob("*.py")+glob.glob("first_order/*.py"))
cv.start()

import unittest
import doctest

import config
import examples
import files
import first_order.fofunctions
import first_order.fotheories
import first_order.fotheory
import first_order.fotype
import first_order.model
import functions
import mace4
import minion
import misc
import morphisms
import morphsgenerators
import newconstellation2
import lindenbaum

modules = [config,
           examples,
           files,
           first_order.fofunctions,
           first_order.fotheories,
           first_order.fotheory,
           first_order.fotype,
           first_order.model,
           functions,
           mace4,
           minion,
           misc,
           morphisms,
           morphsgenerators,
           newconstellation2,
           lindenbaum]

def load_tests(loader, tests, ignore):
    for module in modules:
        tests.addTests(doctest.DocTestSuite(module))
    return tests


if __name__ == '__main__':
    unittest.main(exit=False,failfast=True)
    print("=" * 80)
    print("Coverage:")
    cv.stop()
    cv.report(show_missing=True)
