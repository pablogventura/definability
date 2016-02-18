import config
import examples
import files
import fofunctions
import fotheories
import fotype
import functions
import minion
import misc
import model
import morphisms
import constellation
import lindenbaum
import preorder
from examples import *
from morphisms import *

grafos = fotheories.DiGraph.find_models(5)
for g in grafos:
    c=constellation.Constellation(g)
    atomos = lindenbaum.ji_of_existencial_definable_algebra(c, g.fo_type, 3)
    jis = lindenbaum.ji_of_existencial_positive_definable_algebra(c, g.fo_type, 3)
    jjis = lindenbaum.new_ji_of_existencial_positive_definable_algebra(atomos,c, g.fo_type)
    assert len(jis) == len(jjis[0])
    print "*" * 80
    print g
    print "*" * 80
