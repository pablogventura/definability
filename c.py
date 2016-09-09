import sys
from os.path import expanduser
home = expanduser("~")
jars = home+"/UACalc/UACalc_CLI/Jars"
sys.path.append(jars+"/uacalc.jar")
sys.path.append(jars+"/LatDraw.jar")
sys.path.append(home+"/UACalc/Examples")

from OperationFactory import Operation
from org.uacalc.alg import BasicAlgebra
from org.uacalc.io import AlgebraIO
from org.uacalc.alg import Malcev
from org.uacalc.alg.conlat import BasicPartition

f3 = AlgebraIO.readAlgebraFile("test.ua")
conlat = f3.con().getUniverseList()
print(conlat)

