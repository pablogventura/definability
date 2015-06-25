import os
import subprocess as sp
import Queue
import threading
import re

import config
from model import Model # para los contraejemplos

from misc import writefile,readfile

def getops(li, st):
    # TODO , PARECIERA QUE DEBERIA SER UN METODO INTERNO DE LOS MODELOS QUE DEVUELVE MACE4
    """extract operations/relations from the Prover9 model, se usa en isofilter y prover9"""
    result = {}
    for op in li:
        if op[0] == st:
            result[op[1]] = op[3]
    return result

class Proof():

    def __init__(self, formula_list, syntax='Prover9'):
        """
        Stores a proof as a list of formulas.

        INPUT:
            syntax -- a string that indicates what syntax is used for the
                formulas that prepresent the proof, e.g. "Prover9".
            formula_list -- a list of lists. Each list entry is a list of the
                form [formula, line_number, [references_to_preceding_lines]].
                The references indicate which preceding lines are used in the
                derivation of the current line.
        """
        self.syntax = syntax
        self.proof = formula_list

    def __repr__(self):
        """
        Display a proof as a list of lines.
        """
        st = '\nProof(syntax=\"' + self.syntax + '\", formula_list=[\n'
        for l in self.proof[:-1]:
            st += str(l) + ',\n'
        return st + str(self.proof[-1]) + '])'
        
def proofstep2list(st):
    # convert a line of the Prover9 proof to a list
    li = st.split('.')
    ind = li[0].find(' ')
    return [eval(li[0][:ind])] + [li[0][ind + 1:]] + [eval(li[-2])]
    # return [li[0][ind+1:]]+[eval(li[0][:ind])]+[eval(li[-2])]


class Mace4():
    def __init__(self, mace_input, mace_seconds=2, domain_cardinality=None, one=False, noniso=True):        
        self.apps = [] # subprocesos
        self.ts = [] # hilos
        
        self.__aborting = False
        self.macerunning = True
        self.parsing = True
        
        self.models = []
        self.count = 0
        
        maceargs = []
        if domain_cardinality:
            st = str(domain_cardinality)
            maceargs = ["-n",st,"-N",st] + ([] if one else ["-m","-1"]) + ["-S", "1"]  # set skolem_last
        mace4app = sp.Popen([config.ladrpath + "mace4","-t",str(mace_seconds)]+maceargs, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        mace4app.stdin.write(mace_input)
        mace4app.stdin.close() # TENGO QUE MANDAR EL EOF!
        self.apps.append(mace4app)
        

        if domain_cardinality != None and not one and noniso:
            interp1app = sp.Popen([config.ladrpath + "interpformat", "standard"], stdin=mace4app.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
            isofilterapp = sp.Popen([config.ladrpath + 'isofilter',
                                     'check',
                                     "+ * v ^ ' - ~ \\ / -> B C D E F G H I J K P Q R S T U V W b c d e f g h i j k p q r s t 0 1 <= -<",
                                     'output',
                                     "+ * v ^ ' - ~ \\ / -> B C D E F G H I J K P Q R S T U V W b c d e f g h i j k p q r s t 0 1 <= -<"]
                                    , stdin=interp1app.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
            interp2app = sp.Popen([config.ladrpath + "interpformat", "portable"], stdin=isofilterapp.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
            self.apps += [interp1app,isofilterapp,interp2app]
            self.__stdout = interp2app.stdout
        else:
            interpapp = sp.Popen([config.ladrpath + "interpformat", "portable"], stdin=mace4app.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
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
        
    def __parse_stdout(self):
        if not self.__aborting:
            self.__stdout.readline() # quita el [ del principio
            buf = ""
            for line in iter(self.__stdout.readline, b''):
                buf += line
                if buf.count("[")==buf.count("]"):
                    # hay un modelo completo
                    buf = buf.replace("\n","") #quito saltos de linea
                    buf = buf.strip() # quito espacios para poder sacar la coma
                    if buf[-1] == ",":
                        buf=buf[:-1] # saco la coma!
                                    
                    m = eval(buf)

                    self.__qmodels.put(Model(m[0],self.count,getops(m[2],'function'),getops(m[2],'relation')))
                    self.count+=1
                    buf = "" 
            self.parsing = False #hubo eof
            self.__qmodels.put(None) # para marcar el final

    def __parse_stderr(self):
        if not self.__aborting:
            for line in iter(self.__stderr.readline, b''):
                if "exit" in line:
                    self.macerunning = False
                    self.exitcomment = re.search("\((.+)\)",line).group(1)

    def __iter__(self):
        if self.models:
            for m in self.models:
                yield m
        else:
            while self.parsing or not self.__qmodels.empty():
                m = self.__qmodels.get()
                if m != None:
                    self.models.append(m)
                    yield m
                else:
                    break

    def __len__(self):
        if self.parsing:
            self.ts[1].join() # este es el que parsea la stdout
        return self.count
        
    def abort(self):
        self.__aborting = True
        for app in self.apps:
            app.kill()
            app.wait()
            del app

    def __del__(self):
        self.abort()


class Prover9():
    def __init__(self, prover9_input, prover_seconds=60):
        self.apps = [] # subprocesos
        self.ts = [] # hilos
        
        self.aborting = False
        self.proverrunning = True
        self.parsing = True
        
        self.proofs = []
        self.count = 0
        
        prover9app = sp.Popen([config.ladrpath + "prover9", "-t", str(prover_seconds)], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        prover9app.stdin.write(prover9_input)
        prover9app.stdin.close() # TENGO QUE MANDAR EL EOF!

        ptransapp = sp.Popen([config.ladrpath + "prooftrans",
                              "expand", "renumber", "parents_only"], stdin=prover9app.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
        self.apps = [prover9app,ptransapp]
        self.stderr = prover9app.stderr
        self.stdout = ptransapp.stdout
        
        tparseerr = threading.Thread(target=self.__parse_stderr, args=())
        tparseerr.start()
        self.ts.append(tparseerr)
        
        self.qproofs = Queue.Queue()
        tparseout = threading.Thread(target=self.__parse_stdout, args=())
        tparseout.start()
        self.ts.append(tparseout)

    def __parse_stderr(self):
        if not self.aborting:
            for line in iter(self.stderr.readline, b''):
                if "exit" in line:
                    self.proverrunning = False
                    self.exitcomment = re.search("\((.+)\)",line).group(1)

    def __parse_stdout(self):
        if not self.aborting:
            buf = []
            for line in iter(self.stdout.readline, b''):
                buf.append(line)
                if "= PROOF =" in buf[-1]:
                    buf = buf[-1:] # borro todo lo otro que ha sido el encabezado
                if "= end of proof =" in buf[-1]:
                    # esta entera una prueba
                    self.qproofs.put(Proof(map(proofstep2list, buf[10:-2])))
                    
                    self.count+=1
                    buf = [] # vacio el buffer
            self.parsing = False #hubo eof
            self.qproofs.put(None) # para marcar el fina
            
            
            
    def __iter__(self):
        if self.proofs:
            for p in self.proofs:
                yield p
        else:
            while self.parsing or not self.qproofs.empty():
                p = self.qproofs.get()
                if p != None:
                    self.proofs.append(p)
                    yield p
                else:
                    break

                
    def __len__(self):
        if self.parsing:
            self.ts[1].join() # este es el que parsea la stdout
        return self.count
        
    def abort(self):
        self.aborting = True
        for app in self.apps:
            app.kill()
            app.wait()
            del app

    def __del__(self):
        self.abort()



class ProverMaceSol():
    def __init__(self,assume_list, goal_list, mace_seconds=2, prover_seconds=60, domain_cardinality=None, one=False, options=[], noniso=True):
        """
        Invoke Prover9/Mace4 with lists of formulas and some (limited) options

        INPUT:
            assume_list -- list of Prover9 formulas that assumptions
            goal_list -- list of Prover9 formulas that goals
            mace_seconds -- number of seconds to run Mace4
            prover_seconds -- number of seconds to run Prover9
            domain_cardinality -- if None, search for 1 counter model staring from cardinality 2
                if domain_cardinality = n (>=2), search for all nonisomorphic models of
                cardinality n.
            options -- list of prover9 options (default [], i.e. none)
            hints_list, keep_list, delete_list -- additional lists of formulas.
                See Prover9 manual (prover9.org) for details

        EXAMPLES:
            >>> prover9(['x=x'], ['x=x']) # trivial proof

            >>> prover9(['x=x'], ['x=y']) # trivial counterexample

            >>> Group = ['(x*y)*z = x*(y*z)', 'x*1 = x', "x*i(x) = 1"]
            >>> BooleanGroup = Group + ['x*x = 1']
            >>> prover9(BooleanGroup, ['x*y = y*x']) # Boolean groups are abelian

            >>> prover9(BooleanGroup, [], 3, 0, 50) # No model of cardinality 50
                                                    # Boolean groups have cardinality 2^k
        """
        inputp9m4 = self.generateinput(assume_list,goal_list,options)

        self.models = None
        self.proofs = None

        if mace_seconds:
            self.models = Mace4(inputp9m4, mace_seconds, domain_cardinality, one, noniso)

        if prover_seconds:
            self.proofs = Prover9(inputp9m4, prover_seconds)
            
    def __nonzero__(self):
        # define la conversion a bool
        while self.models.count + self.proofs.count <= 0:
            pass
        if self.proofs.count:
            return True
        else:
            return False

    def generateinput(self, assume_list,goal_list,options):
        result = ""
        for st in options:
            result += st + ".\n"
        result += 'formulas(assumptions).\n'        
        for st in assume_list:
            result += st + '.\n'
        result += 'end_of_list.\nformulas(goals).\n'        
        for st in goal_list:
            result += st + '.\n'
        result += 'end_of_list.\n'
        return result

