#!/usr/bin/env python
# -*- coding: utf8 -*-

import coverage
import glob
cv = coverage.Coverage(include=glob.glob("*.py")+
                       glob.glob("first_order/*.py")+
                       glob.glob("definability/*.py")+
                       glob.glob("misc/*.py")+
                       glob.glob("examples/*.py")+
                       glob.glob("functions/*.py")+
                       glob.glob("interfaces/*.py"))
cv.start()

import unittest
import doctest

import interfaces.config
import interfaces.minion
import interfaces.mace4
import interfaces.files
import first_order.fofunctions
import first_order.fotheories
import first_order.fotheory
import first_order.fotype
import first_order.model
import examples.examples
import misc.misc
import functions.functions
import functions.morphisms
import definability.morphsgenerators
import definability.newconstellation2
import definability.lindenbaum

modules = [interfaces.config,
           interfaces.files,
           interfaces.mace4,
           interfaces.minion,
           first_order.fofunctions,
           first_order.fotheories,
           first_order.fotheory,
           first_order.fotype,
           first_order.model,
           examples.examples,
           misc.misc,
           functions.functions,
           functions.morphisms,
           definability.morphsgenerators,
           definability.newconstellation2,
           definability.lindenbaum]

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
