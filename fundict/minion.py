#!/usr/bin/env python
# -*- coding: utf8 -*-

# Minion interface code Peter Jipsen 2011-03-26 alpha version
# requires sage.chapman.edu/sage/minion_20110326.spkg

import subprocess as sp
from itertools import product
from select import poll, POLLIN

from morphisms import *
import config
import files


class MinionSol(object):
    count = 0
    def __init__(self, input_data, allsols=True, fun=lambda x: x):
        self.id = MinionSol.count
        self.fun = fun
        MinionSol.count += 1
        self.input_filename = config.minion_path + "input_minion%s" % self.id
        # print self.input_filename

        files.create_pipe(self.input_filename)

        minionargs = ["-printsolsonly","-randomseed","0"] 
        if allsols:
            minionargs += ["-findallsols"]
        minionargs += [self.input_filename]

        self.minionapp = sp.Popen([config.minion_path + "minion"] + minionargs,
                                  stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        files.write(self.input_filename, input_data)
        self.EOF = False
        self.solutions = []

    def __parse_solution(self):
        str_sol = self.minionapp.stdout.readline()
        if str_sol:
            str_sol = str_sol[:-1] # borro el \n
            try:
                result = map(int, str_sol.strip().split(" "))
                # ACA IRIAN LAS TRADUCCIONES DE NOMBRES EN EL FUTURO
                for i,v in enumerate(result):
                    if v == -1:
                        result[i]=None
            except ValueError:
                str_sol += "\n"
                str_sol += self.minionapp.stdout.read() # leo toda la respuesta de minion para saber que paso
                raise ValueError("Minion Error:\n%s" % str_sol)
            return result
        else:
            str_err = self.minionapp.stderr.read()
            if str_err:
                raise ValueError("Minion Error:\n%s" % str_err)
            self.EOF = True
            self.__terminate()

    def __iter__(self):
        for solution in self.solutions:
            yield self.fun(solution)

        while not self.EOF:
            solution = self.__parse_solution()
            if solution:
                self.solutions.append(solution)
                yield self.fun(solution)
            
    def __getitem__(self, index):
        try:
            return self.fun(self.solutions[index])
        except IndexError:
            for i,solution in enumerate(self):
                if i==index:
                    return solution # no hace falta aplicar self.fun porque esta llamando a __iter__
            raise IndexError("There aren't so many solutions.")
                
    def __nonzero__(self):
        if self.solutions or self.EOF:
            return bool(self.solutions)
        else:
            solution = self.__parse_solution()
            if solution:
                self.solutions.append(solution)
                return True
            else:
                return False
                
    def __len__(self):
        if not self.EOF:
            for i in self:
                pass
        return len(self.solutions)

    def __terminate(self):
        self.minionapp.kill()
        del self.minionapp
        files.remove(self.input_filename)
    
    def __del__(self):
        if not self.EOF:
            self.__terminate()


class MorphMinionSol(MinionSol):
    def __init__(self, morph_type, subtype, source, target, inj=None, surj=None, allsols=True):
        self.morph_type = morph_type
        self.subtype = subtype
        self.source = source
        self.target = target
        self.inj = inj
        self.surj = surj
        
        if self.morph_type == Homomorphism:
            input_data = self.__input_homo()
        elif self.morph_type == Embedding:
            self.inj = True
            input_data = self.__input_embedd()
        elif self.morph_type == Isomorphism:
            self.inj = True
            self.surj = True
            input_data = self.__input_embedd()
        else:
            raise IndexError("Morphism unknown")

        self.fun = lambda x: self.morph_type(x,
                                             self.source,
                                             self.target,
                                             self.subtype,
                                             self.inj,
                                             self.surj) # funcion que tipa los morfismos
        super(MorphMinionSol, self).__init__(input_data, allsols,fun=self.fun)

    def __minion_name(self, oprel):
        """
        Traduce los nombres de las operaciones/relaciones
        """
        # Minion accepts only letters for first character of names
        if oprel.isalpha():
            return oprel
            
        ops = {"^": "m", "+": "p", "-": "s", "*": "t", "<=": "leq"}
        if oprel in ops:
            return ops[oprel]
        else:
            oprel += " " * ((3-len(oprel))%3) # le agrego espacios para evitar los = que mete b64
            return oprel.encode("base64")[:-1]

    def __oprel_table(self, symbol, oprel, prefix=""):
        """
        Devuelve un string con la tabla que representa a la relacion/operacion en minion
        """
        table = oprel.table()
        table_name = prefix + self.__minion_name(symbol)
        height = len(table)
        width = len(table[0])
        result = ""
        for row in table:
            result += " ".join(map(str, row)) + "\n"
        result = "%s %s %s\n" % (table_name, height, width) + result
        return result

    def __input_homo(self):
        """
        Genera un string para darle a Minion para tener los homomorfismos de source en target
        """
        A = self.source
        B = self.target
        
        result = "MINION 3\n\n"
        result += "# Busca homomorfismos de a en b\n"
        if self.inj:
            result += "# que sean inyectivos\n"
        if self.surj:
            result += "# que sean suryectivos\n"
        result += "\n"
        result += "**VARIABLES**\n"
        result += "DISCRETE f[%s]{-1..%s}\n\n" % (max(A.universe)+1, max(B.universe))
        result += "**TUPLELIST**\n"
        for op in self.subtype.operations:
            result += self.__oprel_table(op,B.operations[op]) + "\n"
        for rel in self.subtype.relations:
            result += self.__oprel_table(rel,B.relations[rel]) + "\n"
        result += "**CONSTRAINTS**\n"
        if self.inj:
            result += "alldiff([f[%s]])\n" % "],f[".join(map(str, A.universe))  # exige que todos los valores de f
                                                                               # sean distintos para el univ de partida
        if self.surj:
            for i in B.universe:
                result += "occurrencegeq(f, " + str(i) + ", 1)\n"  # exige que i aparezca al menos una vez en el "vector" f

        for op in self.subtype.operations:
            cons = A.operations[op].table()
            for row in cons:
                result += "table([f[" + "],f[".join(map(str, row)) + "]],%s)\n" % self.__minion_name(op)
            result += "\n"
        for rel in self.subtype.relations:
            cons = A.relations[rel].table()
            for row in cons:
                result += "table([f[" + "],f[".join(map(str, row)) + "]],%s)\n" % self.__minion_name(rel)
            result += "\n"
        result += "occurrencegeq(f, -1, %s)\n" % (max(A.universe)+1 - A.cardinality)
        result += "**EOF**\n"
        return result

    def __input_embedd(self):
        """
        Genera un string para darle a Minion para tener los embeddings de A en B
        """
        A = self.source
        B = self.target
        
        result = "MINION 3\n\n"
        result += "# Busca embeddings de a en b\n" 
        if self.inj:
            result += "# que sean inyectivos\n"
        if self.surj:
            result += "# que sean suryectivos\n"
        result += "\n"
        result += "**VARIABLES**\n"
        result += "DISCRETE f[%s]{-1..%s}\n\n" % (max(A.universe)+1, max(B.universe))
        result += "DISCRETE g[%s]{-1..%s}\n\n" % (max(B.universe)+1, max(A.universe))
        result += "**SEARCH**\n"
        result += "PRINT [f]\n\n" # para que no me imprima los valores de g
        result += "**TUPLELIST**\n"
        
        for op in self.subtype.operations:
            result += self.__oprel_table(op,B.operations[op],prefix="b") + "\n"
        for rel in self.subtype.relations:
            result += self.__oprel_table(rel,B.relations[rel],prefix="b") + "\n"
        for rel in self.subtype.relations:
            result += self.__oprel_table(rel,A.relations[rel],prefix="a") + "\n"
            
        result += "**CONSTRAINTS**\n"
        if self.inj:
            result += "alldiff([f[%s]])\n" % "],f[".join(map(str, A.universe))  # exige que todos los valores de f
                                                                               # sean distintos para el univ de partida
        if self.surj:
            for i in B.universe:
                result += "occurrencegeq(f, " + str(i) + ", 1)\n"  # exige que i aparezca al menos una vez en el "vector" f

        for op in self.subtype.operations:
            cons =A.operations[op].table()
            for row in cons:
                result += "table([f[" + "],f[".join(map(str, row)) + "]],%s)\n" % ("b"+self.__minion_name(op))
            result += "\n"
        for rel in self.subtype.relations:
            cons = A.relations[rel].table()
            for row in cons:
                result += "table([f[" + "],f[".join(map(str, row)) + "]],%s)\n" % ("b"+self.__minion_name(rel))
            result += "\n"
        for rel in self.subtype.relations:
            cons = B.relations[rel].table()
            for row in cons:
                result += "watched-or({"
                for i in row:
                    result += "element(g, %s, -1)," % i
                result += "table([g[" + "],g[".join(map(str, row)) + "]],%s)})\n" % ("a"+self.__minion_name(rel))
            result += "\n"
        for i in A.universe:
            result += "element(g, f[%s], %s)\n" % (i,i) # g(f(x))=X
        
        result += "occurrencegeq(f, -1, %s)\n" % (max(A.universe)+1 - A.cardinality) # cant de valores en el rango no en dominio 
        result += "occurrencegeq(g, -1, %s)\n" % (max(B.universe)+1 - A.cardinality) # cant de valores en el rango no en dominio
        result += "**EOF**\n"
        return result

class ParallelMorphMinionSol(object):
    def __init__(self, morph_type, subtype, source, targets, inj=None, surj=None, allsols=False, cores=0):

        self.queue = list(targets)
        self.morph_type = morph_type
        self.subtype = subtype
        self.source = source
        self.inj = inj
        self.surj = surj
        self.allsols = allsols
        self.solution = None
        
        self.poll = poll()
        self.minions={}
        
        for i in range(cores):
            self.next_to_running()
        
    def next_to_running(self):
        if self.queue:
            target = self.queue.pop()
            new_minion = MorphMinionSol(self.morph_type,
                                        self.subtype,
                                        self.source,
                                        target,
                                        inj=self.inj,
                                        surj=self.inj,
                                        allsols=self.allsols)
            fd = new_minion.minionapp.stdout.fileno()
            self.minions[fd] = new_minion
            self.poll.register(fd,POLLIN)

    def read(self,fd):
        if self.minions[fd]:
            result = self.minions[fd][0]
        else:
            result = False
        del self.minions[fd]
        self.poll.unregister(fd)
        return result
            
    def solve(self):
        if self.solution is None:
            while self.queue or self.minions:
                for (fd,event) in self.poll.poll():
                    result = self.read(fd)
                    if result:
                        self.solution = result
                        return self.solution
                    else:
                        if self.queue:
                            self.next_to_running()
            self.solution = False
            return False
        else:
            return self.solution
        

def homomorphisms(source, target, subtype, inj=None, surj=None, allsols=True):
    """
    call Minion to calculate all homomorphisms from A to B
    
    >>> from examples import *
    >>> len(homomorphisms(posetcadena2,posetdiamante,posetcadena2.fo_type))
    12
    """
    return MorphMinionSol(Homomorphism, subtype, source, target, inj, surj, allsols)

def embeddings(source, target, subtype, surj=None, allsols=True):
    """
    call Minion to calculate all embeddings of A into B

    >>> from examples import *
    >>> len(embeddings(posetcadena2,posetdiamante,posetcadena2.fo_type))
    7
    """
    return MorphMinionSol(Embedding, subtype, source, target, True, surj, allsols)

def isomorphisms(source, target, subtype, allsols=True):
    """
    call Minion to calculate all homomorphisms from A to B

    >>> from examples import *
    >>> len(isomorphisms(posetcadena2,posetdiamante,posetcadena2.fo_type))
    0
    >>> len(isomorphisms(posetcadena2,posetcadena2,posetcadena2.fo_type))
    1
    >>> len(isomorphisms(posetdiamante,posetdiamante,posetdiamante.fo_type))
    6
    """
    return MorphMinionSol(Isomorphism, subtype, source, target, True, True, allsols)

def is_homomorphic_image(source, target, subtype):
    """
    return homomorphism if B is a homomorphic image of A (uses Minion)
    else returns False
    
    >>> from examples import *
    >>> bool(is_homomorphic_image(posetcadena2,posetdiamante,posetcadena2.fo_type))
    True
    >>> bool(is_homomorphic_image(posetdiamante,posetcadena2,posetcadena2.fo_type))
    True
    """
    h = homomorphisms(source, target, subtype, allsols=False)
    if h:
        return h[0]
    else:
        return False

def is_substructure(source, target, subtype):
    """
    return embedding if B is a substructure of A (uses Minion)
    else returns False
    
    >>> from examples import *
    >>> bool(is_substructure(posetcadena2,posetdiamante,posetcadena2.fo_type))
    True
    >>> bool(is_substructure(posetdiamante,posetcadena2,posetcadena2.fo_type))
    False
    """
    e = embeddings(source, target, subtype, allsols=False)
    if e:
        return e[0]
    else:
        return False

def is_isomorphic(source, target, subtype):
    """
    return isomorphism if A is isomorphic to B (uses Minion)
    else returns False
    
    >>> from examples import *
    >>> bool(is_isomorphic(posetcadena2,posetdiamante,posetcadena2.fo_type))
    False
    >>> bool(is_isomorphic(posetdiamante,posetdiamante,posetdiamante.fo_type))
    True
    """
    i = isomorphisms(source, target, subtype, allsols=False)
    if i:
        return i[0]
    else:
        return False

def is_isomorphic_to_any(source, targets, subtype, cores=1, parallel=True):
    """
    return isomorphism if A is isomorphic to B (uses Minion)
    else returns False
    """
    if not targets:
        return False
    if not parallel:
        for target in targets:
            iso = source.is_isomorphic(target,subtype)
            if iso:
                return iso
        return False
    else:
        i = ParallelMorphMinionSol(Isomorphism, subtype, source, targets,cores=cores)
        return i.solve()

    

        

if __name__ == "__main__":
    import doctest
    doctest.testmod()
