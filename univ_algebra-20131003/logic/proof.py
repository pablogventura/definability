import os
import subprocess as sp

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


def prover9(assume_list, goal_list, mace_seconds=2, prover_seconds=60, domain_cardinality=None,
             one=False, options=[], noniso=True, hints_list=None, keep_list=None, delete_list=None):
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
    inputp9m4 = generateinput(assume_list,goal_list,options)
    #writefile("tmp.in", inputp9m4)
    

    if mace_seconds:
        maceargs = []
        if domain_cardinality:
            st = str(domain_cardinality)
            maceargs = ["-n",st,"-N",st] + ([] if one else ["-m","-1"]) + ["-S", "1"]  # set skolem_last
        mace4app = sp.Popen([config.uapth + "mace4","-t",str(mace_seconds)]+maceargs, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        mace4app.stdin.write(inputp9m4)
        mace4app.stdin.close() # TENGO QUE MANDAR EL EOF!

        #TODO ASI ERA ANTES res = os.system(config.uapth + 'mace4 -t ' + str(mace_seconds) + mace_params + ' -f tmp.in >tmp.out 2>tmpe')

        out_str = mace4app.stdout.read()
        
        if "%%ERROR" in out_str:
            print out_str[ind + 2:]
            return
        if 'Exiting with failure' not in out_str:
            if domain_cardinality != None and not one and noniso:
                interp1app = sp.Popen([config.uapth + "interpformat", "standard"], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
                isofilterapp = sp.Popen([config.uapth + 'isofilter',
                                         'check',
                                         "+ * v ^ ' - ~ \\ / -> B C D E F G H I J K P Q R S T U V W b c d e f g h i j k p q r s t 0 1 <= -<",
                                         'output',
                                         "+ * v ^ ' - ~ \\ / -> B C D E F G H I J K P Q R S T U V W b c d e f g h i j k p q r s t 0 1 <= -<"]
                                        , stdin=interp1app.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
                interp2app = sp.Popen([config.uapth + "interpformat", "portable"], stdin=isofilterapp.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
                interp1app.stdin.write(out_str)
                interp1app.stdin.close()
                out_str = interp2app.stdout.read()
            else:
                interpapp = sp.Popen([config.uapth + "interpformat", "portable"], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
                interpapp.stdin.write(out_str)
                interpapp.stdin.close()
                out_str = interpapp.stdout.read()
            #interpformatapp = sp.Popen([config.uapth + "mace4"]+maceargs, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
            #out_str = readfile("tmpe")

            if out_str != "":
                li = eval(out_str.replace("\\", "\\\\")) # como viene habiendo pasado por interpformat portable tiene "un poco" de sentido
            else:
                print "No models found (so far)"
                return
            models = []
            for m in li:
                models += [Model(m[0], len(models), getops(m[2], 'function'), getops(m[2], 'relation'))]
            if domain_cardinality != None and not one:
                print "Number of " + ("nonisomorphic " if noniso else "") + "models of cardinality", domain_cardinality, " is ", len(models)
            # else: print "(Counter)example of minimal cardinality:"
            return models
        elif domain_cardinality != None and out_str.find('exit (exhausted)') != -1:
            if not one:
                print 'No model of cardinality ' + str(domain_cardinality)
            return []
    prover9app = sp.Popen([config.uapth + "prover9", "-t", str(prover_seconds)], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    prover9app.stdin.write(inputp9m4)
    prover9app.stdin.close() # TENGO QUE MANDAR EL EOF!
    #res = os.system(config.uapth + 'prover9 -t ' + str(prover_seconds) + ' -f tmp.in >tmp.out')
    
    out_str = prover9app.stdout.read()
    ind = out_str.find("%%ERROR")
    if ind != -1:
        print out_str[ind + 2:]
        return
    if True:  # res==0 or res==1 or res==256:
        ptransapp = sp.Popen([config.uapth + "prooftrans",
                              "expand", "renumber", "parents_only"], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        #os.system(config.uapth + 'prooftrans expand renumber parents_only -f tmp.out >tmpe')
        ptransapp.stdin.write(out_str)
        ptransapp.stdin.close() # TENGO QUE MANDAR EL EOF!
        out_str = ptransapp.stdout.read()
        lst = []
        ind1 = out_str.find("PROOF ===")
        ind2 = out_str.find("end of proof ===")
        while ind1 != -1:
            lst.append([proofstep2list(x) for x in out_str[ind1:ind2].split('\n')[10:-2]])
            ind1 = out_str.find("PROOF ===", ind2)
            ind2 = out_str.find("end of proof ===", ind2 + 1)
        return [Proof(li) for li in lst]
    print 'No conclusion (timeout)'
    return 'No conclusion (timeout)'

def generateinput(assume_list,goal_list,options):
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

