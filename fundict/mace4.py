import subprocess as sp
import threading
import re
import Queue
import config
from model import FO_Model  # para los contraejemplos
from fofunctions import FO_Operation, FO_Relation

def getops(li, st):
    # TODO , PARECIERA QUE DEBERIA SER UN METODO INTERNO DE LOS MODELOS QUE DEVUELVE MACE4
    """extract operations/relations from the Prover9 model, se usa en isofilter y prover9"""
    result = {}
    for op in li:
        if op[0] == st:
            result[op[1]] = op[3]
    for oprel in result:
        if st == "function":
            result[oprel] = FO_Operation(result[oprel])
        elif st == "relation":
            result[oprel] = FO_Relation(result[oprel])
        else:
            raise KeyError
    return result

class Mace4():

    def __init__(self, assume_list, goal_list, mace_seconds=30, domain_cardinality=None, one=False, noniso=True, options=[], fo_type=None):
        self.apps = []  # subprocesos
        self.ts = []  # hilos

        self.__aborting = False
        self.macerunning = True
        self.parsing = True
        self.assume_list = assume_list
        self.goal_list = goal_list
        self.options = options
        self.fo_type = fo_type
        self.models = []
        self.count = 0

        maceargs = []
        if domain_cardinality:
            st = str(domain_cardinality)
            maceargs = ["-n", st, "-N", st] + ([] if one else ["-m", "-1"]) + ["-S", "1"]  # set skolem_last
        mace4app = sp.Popen([config.ladr_path + "mace4", "-t", str(mace_seconds)] + maceargs, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        mace4app.stdin.write(self.generate_input())
        mace4app.stdin.close()  # TENGO QUE MANDAR EL EOF!
        self.apps.append(mace4app)

        if domain_cardinality is not None and not one and noniso:
            interp1app = sp.Popen([config.ladr_path + "interpformat", "standard"], stdin=mace4app.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
            isofilterapp = sp.Popen([config.ladr_path + 'isofilter',
                                     'check',
                                     "+ * v ^ ' - ~ \\ / -> B C D E F G H I J K P Q R S T U V W b c d e f g h i j k p q r s t 0 1 <= -<",
                                     'output',
                                     "+ * v ^ ' - ~ \\ / -> B C D E F G H I J K P Q R S T U V W b c d e f g h i j k p q r s t 0 1 <= -<"], stdin=interp1app.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
            interp2app = sp.Popen([config.ladr_path + "interpformat", "portable"], stdin=isofilterapp.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
            self.apps += [interp1app, isofilterapp, interp2app]
            self.__stdout = interp2app.stdout
        else:
            interpapp = sp.Popen([config.ladr_path + "interpformat", "portable"], stdin=mace4app.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
            self.apps.append(interpapp)
            self.__stdout = interpapp.stdout
        self.__stderr = mace4app.stderr

        tparseerr = threading.Thread(target=self.__parse_stderr, args=())
        tparseerr.start()
        self.ts.append(tparseerr)

        self.__qmodels = Queue.Queue()
        tparseout = threading.Thread(target=self.__parse_stdout, args=())
        tparseout.start()
        self.ts.append(tparseout)
        
    def generate_input(self):
        result = ""
        for st in self.options:
            result += st + ".\n"
        result += 'formulas(assumptions).\n'
        for st in self.assume_list:
            result += st + '.\n'
        result += 'end_of_list.\nformulas(goals).\n'
        for st in self.goal_list:
            result += st + '.\n'
        result += 'end_of_list.\n'
        return result
        
    def __parse_stdout(self):
        if not self.__aborting:
            self.__stdout.readline()  # quita el [ del principio
            buf = ""
            for line in iter(self.__stdout.readline, b''):
                buf += line
                if buf.count("[") == buf.count("]"):
                    # hay un modelo completo
                    buf = buf.replace("\n", "")  # quito saltos de linea
                    buf = buf.strip()  # quito espacios para poder sacar la coma
                    if buf[-1] == ",":
                        buf = buf[:-1]  # saco la coma!

                    m = eval(buf)

                    self.__qmodels.put(FO_Model(self.fo_type, range(m[0]), getops(m[2], 'function'), getops(m[2], 'relation')))
                    self.count += 1
                    buf = ""
            self.parsing = False  # hubo eof
            self.__qmodels.put(None)  # para marcar el final

    def __parse_stderr(self):
        if not self.__aborting:
            for line in iter(self.__stderr.readline, b''):
                if "exit" in line:
                    self.macerunning = False
                    self.exitcomment = re.search("\((.+)\)", line).group(1)

    def __iter__(self):
        if self.models:
            for m in self.models:
                yield m
        else:
            while self.parsing or not self.__qmodels.empty():
                m = self.__qmodels.get()
                if m is not None:
                    self.models.append(m)
                    yield m
                else:
                    break

    def __len__(self):
        if self.parsing:
            self.ts[1].join()  # este es el que parsea la stdout
        return self.count

    def abort(self):
        self.__aborting = True
        for app in self.apps:
            app.kill()
            app.wait()
            del app

    def __del__(self):
        self.abort()
