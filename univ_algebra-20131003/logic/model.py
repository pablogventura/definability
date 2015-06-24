import os # TODO NO DEBERIA USARSE

import config
from display import opstr, oprelstr, xmlopstr
from misc import readfile, writefile
import subprocess as sp
import threading


def UASol(inputua, example, options=[]):

    inputfn = config.clspth + "inputUA.ua"
    os.mkfifo(inputfn)
    
    uaapp = sp.Popen(["java", "-classpath", config.clspth + "uacalc/classes/",
                      "org.uacalc.example.%s" % example, inputfn] + options, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    writefile(inputfn,inputua)
    
    result = uaapp.stdout.read()
    os.remove(inputfn)
    return result


class Model():

    def __init__(self, cardinality, index=None, operations={}, relations={},
                 **kwargs):
        """
        Construct a finite first-order model.

        INPUT:
            cardinality -- number of elements of the model's base set
            index -- a natural number giving the position of the model 
                in a list of models
            operations  -- a dictionary of operations on [0..cardinality-1].
                Entries are symbol:table pairs where symbol is a string 
                that denotes the operation symbol, e.g. '+', and table is
                an n-dimensional array with entries from [0..cardinality-1].
                n >= 0 is the arity of the operation (not explicitly coded 
                but can be computed from the table).
            relations -- a dictionary of relations on [0..cardinality-1].
                Entries are symbol:table pairs where symbol is a string 
                that denotes the relation symbol, e.g. '<', and table is
                an n-dimensional array with entries from [0,1] (coding 
                False/True). Alternatively the table can be an 
                (n-2)-dimensional array with entries that are dictionaries
                with keys [0..cardinality-1] and values subsets of [0..cardinality-1],
                given as ordered lists.
                n >= 0 is the arity of the relation (not explicitly coded 
                but can be computed from the table).
            other optional arguments --
                uc  -- a dictionary with keys [0..cardinality-1] and values 
                    an ordered list of upper covers. Used for posets.
                pos -- list of [x,y] coordinates for element positions
                labels -- list of n strings that give a label for each element
                is_... -- True/False properties are stored here
        """

        self.cardinality = cardinality
        self.index = index
        self.operations = operations
        self.relations = relations
        for attr in kwargs:
            setattr(self, attr, kwargs[attr])

    def __repr__(self):
        """
        display a model
        """
        st = '\nModel(cardinality = ' + str(self.cardinality) +\
             (', index = ' + str(self.index) if self.index != None else '')
        if self.operations != {}:
            st += ', operations = {' + oprelstr(self.operations) + '}'
        if self.relations != {}:
            st += ', relations = {' + oprelstr(self.relations) + '}'
        other = set(vars(self)) - set(["cardinality", "index", "operations", "relations"])
        for attr in other:
            st += ',\n' + attr + ' = ' + str(getattr(self, attr))
        return st + ')'

    def positive_diagram(self, c):
        """
        Return the positive diagram of the algebra or structure, prefix c
        """
        li = []
        for x in self.operations:
            li += self.__op_var_pos_diag(x, c)
        for x in self.relations:
            li += self.__rel_var_pos_diag(x, c)
        return li

    def diagram(self, c, s=0):
        """
        Return the diagram of the algebra or structure, prefix c, shift s
        """
        li = []
        for x in range(self.cardinality):
            for y in range(x + 1, self.cardinality):
                li += ["-(" + c + str(x + s) + "=" + c + str(y + s) + ")"]
        for x in self.operations:
            li += self.__op_var_diag(x, c, s)
        for x in self.relations:
            li += rel_var_diag(self.relations, x, c, s)
        return li

    def find_extensions(self, cls, cardinality, mace_time=60):
        """
        Find extensions of this model of given cardinality card in FOclass cls
        """
        n = self.cardinality
        ne = ['c' + str(x) + '!=c' + str(y) for x in range(n) for y in range(x + 1, n)]
        return prover9(cls.axioms + ne + self.positive_diagram('c'), [],
                       mace_time, 0, cardinality)

    def inS(self, B, info=False):
        """
        check if self is a subalgebra of B, if so return sublist of B
        """
        if self.cardinality > B.cardinality:
            return False
        if info:
            print self.diagram('a') + B.diagram('')
        m = prover9(self.diagram('a') + B.diagram(''), [], 6000, 0, B.cardinality, True)
        if len(m) == 0:
            return False
        return [m[0].operations['a' + str(i)] for i in range(self.cardinality)]

    def inH(self, B, info=False):
        """
        check if self is a homomorphic image of B, if so return homomorphism
        """
        if self.cardinality > B.cardinality:
            return False
        formulas = self.diagram('') + B.diagram('', self.cardinality) +\
            ['A(' + str(i) + ')' for i in range(self.cardinality)] +\
            ['-B(' + str(i) + ')' for i in range(self.cardinality)] +\
            ['B(' + str(i) + ')' for i in range(self.cardinality, self.cardinality + B.cardinality)] +\
            ['-A(' + str(i) + ')' for i in range(self.cardinality, self.cardinality + B.cardinality)] +\
            ['B(x) & B(y) -> A(h(x)) & A(h(y))' + self.__op_hom(B),
             'A(y) -> exists x (B(x) & h(x) = y)']
        if info:
            print formulas
        m = prover9(formulas, [], 6000, 0, self.cardinality + B.cardinality, True)
        if len(m) == 0:
            return False
        return m[0].operations['h'][self.cardinality:]

    def uacalc_format(self, name):
        """
        display a model in UAcalc format (uacalc.org)
        """
        st = '<?xml version="1.0"?>\n<algebra>\n  <basicAlgebra>\n    <algName>' +\
             name + (str(self.index) if self.index != None else '') +\
             '</algName>\n    <cardinality>' + str(self.cardinality) +\
             '</cardinality>\n    <operations>\n'
        for x in self.operations:
            st += '      <op>\n        <opSymbol>\n          <opName>' +\
                  x + '</opName>\n'
            oplst = type(self.operations[x]) == list
            if oplst and type(self.operations[x][0]) == list:
                st += '          <arity>2</arity>\n        </opSymbol>\n        <opTable>\n          <intArray>\n' + xmlopstr(self.operations[x])
            else:
                st += '          <arity>' + ('1' if oplst else '0') + '</arity>\n        </opSymbol>\n        <opTable>\n          <intArray>\n            <row>' + \
                    (str(self.operations[x])[1:-1] if oplst else str(self.operations[x])) + '</row>\n'
            st += '          </intArray>\n        </opTable>\n      </op>\n'
        return st + '    </operations>\n  </basicAlgebra>\n</algebra>\n'

    def ConUACalc(self):
        """
        use the uacalculator to compute the congruences of self
        """
        if hasattr(self, "con"):
            return self.con
        st = self.uacalc_format("A" + str(self.index))

        st = UASol(st,"ConUACalc")
        st = st[st.index("["):]     # remove diagnostic output
        self.con = eval(st)
        return self.con

    def JConUACalc(self):
        """
        use the uacalculator to compute the joinirreducible congruences of self
        """
        if hasattr(self, "jcon"):
            return self.jcon
        st = self.uacalc_format("A" + str(self.index))
        st = UASol(st,"JConUACalc")
        while st[0] == "k":
            st = st[st.index("\n") + 1:]  # remove diagnostic output
        self.jcon = eval(st)
        return self.jcon

    def MConUACalc(self):
        """
        use the uacalculator to compute the meetirreducible congruences of self
        """
        if hasattr(self, "mcon"):
            return self.mcon
        st = self.uacalc_format("A" + str(self.index))
        st = UASol(st,"MConUACalc")
        while st[0] == "k":
            st = st[st.index("\n") + 1:]  # remove diagnostic output
        self.mcon = eval(st)
        return self.mcon

    def SubUACalc(self):
        """
        use the uacalculator to compute the subalgebras of self
        """
        st = self.uacalc_format("A" + str(self.index))
        st = UASol(st,"SubUACalc")
        while st[0] != "[" and st[0] != "]":
            st = st[st.index("\n") + 1:]  # remove diagnostic output
        li = eval(st)
        cardf = {}
        for x in li:
            if len(x) in cardf:
                cardf[len(x)].append(x)
            else:
                cardf[len(x)] = [x]
        li = [x for y in cardf for x in sorted(cardf[y])]
        return li

    def FindTypeSet(self):
        """
        use the uacalculator to compute the type set of self
        """
        st = self.uacalc_format("A" + str(self.index))
        st = UASol(st,"FindTypeSet")
        st = st[st.index("type set: ") + 10:]     # remove diagnostic output
        return eval(st)

    def inVar(self, B, info=False):
        #TODO ESTE FALTA, PORQUE TOMA DOS COSAS
        """
        use the uacalculator to compute if self is in the variety gen by B
        """
        stA = self.uacalc_format("A" + str(self.index))
        stB = B.uacalc_format("B" + str(B.index))

        st = UASol([stA,stB],"FindTypeSet")

        if info:
            print st
        return "eq is null" in st

    def Free(self, n, info=False):
        """
        use the uacalculator to compute the free algebra on n gens over self
        """
        st = self.uacalc_format("A" + str(self.index))
        writefile('tmpalgA.ua', st)
        os.system('java -classpath ' + config.clspth + 'uacalc/classes/ org.uacalc.example.FreeAlg tmpalgA.ua ' + str(n) + ' >tmpout.txt')
        st = readfile('tmpout.txt')
        
        if info:
            print st
        return int(st[st.find("fr size = ") + 10:st.find(" elements")])

    def product(self, B, info=False):
        base = [[x, y] for x in range(self.cardinality) for y in range(B.cardinality)]
        if info:
            print base
        op = {}
        for f in B.operations:
            fA = self.operations[f]
            fB = B.operations[f]
            if type(fB) == list:
                if type(fB[0]) == list:
                    op[f] = [[base.index([fA[p[0]][q[0]], fB[p[1]][q[1]]])
                              for p in base] for q in base]
                else:
                    op[f] = [base.index([fA[p[0]], fB[p[1]]]) for p in base]
            else:
                op[f] = base.index([fA, fB])
        rel = {}
        for r in B.relations:
            rA = self.relations[r]
            rB = B.relations[r]
            if type(rB[0]) == list:
                rel[r] = [[1 if rA[p[0]][q[0]] == 1 and rB[p[1]][q[1]] == 1 else 0
                           for p in base] for q in base]
            else:
                rel[r] = [1 if rA[p[0]] == 1 and rB[p[1]] == 1 else 0 for p in base]
        return Model(len(base), None, op, rel)

    def subuniverses(A):
        # A=self is a finite algebra (Python Model)
        subl = []
        sub = [2 for i in range(A.cardinality)]
        completeSubalgebra(A, sub, 0, subl)
        return subl

    def subalgebra(A, sub, index=None):
        # sub is a sublist of [0,..,A.cardinality-1]
        f = [0 for i in range(A.cardinality)]  # inverse map
        for i in range(len(sub)):
            f[sub[i]] = i
        opB = dict([s, []] for s in A.operations)
        for s in A.operations:
            op = A.operations[s]
            alg = op  # used if constant
            if type(op) == list:
                alg = []
                for i in range(len(sub)):
                    if type(op[0]) != list:
                        alg.append(f[op[sub[i]]])
                    else:
                        alg.append([])
                        for j in range(len(sub)):
                            alg[i].append(f[op[sub[i]][sub[j]]])
                opB[s] = alg
            else:
                opB[s] = f[alg]
        return Model(len(sub), index, opB)

    def subalgebras(A, info=False):
        li = A.SubUACalc()
        li = [A.subalgebra(li[i], i) for i in range(len(li)) if li[i] != []]
        if info:
            print len(li)
        return isofilter(li)

    def inHS(self, B, info=False):
        li = B.subalgebras(info)
        for x in li:
            if self.inH(x):
                return (True, li.index(x)) if info else True
        return False

    def is_commutative(self, s):
        """
        Check if the binary symbol  s  is a commutative operation in the model
        """
        return all(self.operations[s][x][y] == self.operations[s][y][x]
                   for x in range(self.cardinality) for y in range(self.cardinality))

    def is_associative(self, s):
        """
        Check if the binary symbol  s  is an associative operation in the model
        """
        base = range(self.cardinality)
        return all(self.operations[s][self.operations[s][x][y]][z] ==
                   self.operations[s][x][self.operations[s][y][z]]
                   for x in base for y in base for z in base)

    def sage_poset(self, rel_symbol="<="):
        from sage.combinat.posets.posets import Poset
        if rel_symbol in self.relations:
            M = self.relations[rel_symbol]
            base = range(len(M))
            P = Poset((base, [[x, y] for x in base for y in base
                              if x != y and M[x][y] == 1]), cover_relations=False)
        else:  # for semilattices
            M = self.operations[rel_symbol]
            base = range(len(M))
            P = Poset((base, [[x, y] for x in base for y in base if x != y and
                              M[x][y] == (y if rel_symbol in ['v', '+'] else x)]),
                      cover_relations=False)
        if hasattr(self, "name"):
            P.name = self.name
        return P

    def sage_lattice(self, op_symbol="^"):
        from sage.combinat.posets.lattices import LatticePoset
        M = self.operations[op_symbol]
        base = range(len(M))
        L = LatticePoset((base, [[x, y] for x in base for y in base if x != y
                                 and M[x][y] == (y if op_symbol in ['v', '+'] else x)]))
        if hasattr(self, "name"):
            L.name = self.name
        return L

    def get_leq(self):
        if "<=" in self.relations:
            return self.relations["<="]
        n = self.cardinality
        leq = [[0 for y in range(n)] for x in range(n)]
        for i in range(n):
            leq[i][i] = 1
            for j in self.uc[i]:
                leq[i][j] = 1
        for i in range(n):
            for j in range(i + 1, n):
                if leq[i][j]:
                    for k in range(j + 1, n):
                        if leq[j][k]:
                            leq[i][k] = 1
        #self.relations["<="] = leq
        return leq

    def downset(self, y):
        n = self.cardinality
        le = self.get_leq()
        return set([x for x in range(n) if le[x][y] == 1])

    def upset(self, x):
        n = self.cardinality
        le = self.get_leq()
        return set([y for y in range(n) if le[x][y] == 1])

    def get_downsets(self):
        if hasattr(self, 'down'):
            return self.down
        n = self.cardinality
        le = self.get_leq()
        down = [set([x for x in range(n) if le[x][y] == 1]) for y in range(n)]
        self.down = down
        return down

    def is_ordinal_sum(self):
        n = self.cardinality
        le = self.get_leq()
        for i in range(1, n - 1):
            if all([le[i][j] for j in range(i + 1, n - 1)]) and\
               all([le[j][i] for j in range(1, i)]):
                   return True
        return False

    def ordinal_sum_count(self):
        n = self.cardinality
        count = 1
        le = self.get_leq()
        for i in range(1, n - 1):
            if all([le[i][j] for j in range(i + 1, n - 1)]) and\
               all([le[j][i] for j in range(1, i)]):
                   count += 1
        return count

    def get_lowercovers(self):
        if hasattr(self, 'lc'):
            return self.lc
        lc = dict((x, []) for x in range(self.cardinality))
        for i in range(self.cardinality):
            for j in self.uc[i]:
                lc[j].append(i)
        self.lc = lc
        return lc

    def get_join(self):  # Freese-Jezek-Nation p217
        if "v" in self.operations:
            return self.operations["v"]
        n = self.cardinality
        join = [[0 for x in range(n)] for x in range(n)]
        le = self.get_leq()
        if not all([le[x][n - 1] == 1 for x in range(n)]):
            return "poset has no top element"
        p = range(n - 1, -1, -1)
        uc = [sorted([p[y] for y in self.uc[x]]) for x in p]
        S = []
        for x in range(n):  # x=x_k
            join[x][x] = x
            for y in S:
                T = []
                for z in uc[x]:
                    T.append(join[y][z])  # T = {x_i \vee z : z>-x_k}
                q = T[0]
                for z in T[1:]:
                    if z > q:
                        q = z  # error in Listing 11.9
                for z in T:
                    if not le[p[q]][p[z]]:
                        return "not a join semilattice: x=" + str(x) + " y=" + str(y)
                join[x][y] = q
                join[y][x] = q
            S.append(x)
        self.operations["v"] = self.__permuted_binary_op(join, p)
        return self.operations["v"]

    def get_meet(self):  # Freese-Jezek-Nation p217
        if "^" in self.operations:
            return self.operations["^"]
        n = self.cardinality
        meet = [[0 for x in range(n)] for x in range(n)]
        le = self.get_leq()
        if not all([le[0][x] == 1 for x in range(n)]):
            return "poset has no bottom element"
        lc = self.get_lowercovers()
        S = []
        for x in range(n):  # x=x_k
            meet[x][x] = x
            for y in S:
                T = []
                for z in lc[x]:
                    T.append(meet[y][z])  # T = {x_i \wedge z : z>-x_k}
                q = T[0]
                for z in T[1:]:
                    if z > q:
                        q = z
                for z in T:
                    if not le[z][q]:
                        return "not a meet semilattice: x=" + str(x) + " y=" + str(y)
                meet[x][y] = q
                meet[y][x] = q
            S.append(x)
        self.operations["^"] = meet
        return meet

    def is_lattice(self):
        """
        Check if  self  is a lattice, i.e. has a top and meet operation
        """
        return len(self.maximals()) == 1 and type(self.get_meet()) != str

    def is_distributive(self):
        jn = self.get_join()
        mt = self.get_meet()
        n = self.cardinality
        for x in range(n):
            for y in range(n):
                for z in range(n):
                    if mt[x][jn[y][z]] != jn[mt[x][y]][mt[x][z]]:
                        return False
        return True

    def is_join_semidistributive(self):
        jn = self.get_join()
        mt = self.get_meet()
        n = self.cardinality
        for x in range(n):
            for y in range(n):
                for z in range(n):
                    if jn[x][y] == jn[x][z] and jn[x][y] != jn[x][mt[y][z]]:
                        return False
        return True

    def is_meet_semidistributive(self):
        jn = self.get_join()
        mt = self.get_meet()
        n = self.cardinality
        for x in range(n):
            for y in range(n):
                for z in range(n):
                    if mt[x][y] == mt[x][z] and mt[x][y] != mt[x][jn[y][z]]:
                        return False
        return True

    def is_semidistributive(self):
        return self.is_join_semidistributive() and self.is_meet_semidistributive()

    def is_modular(self):
        jn = self.get_join()
        mt = self.get_meet()
        n = self.cardinality
        for x in range(n):
            for y in range(n):
                for z in range(n):
                    if mt[x][jn[y][mt[x][z]]] != jn[mt[x][y]][mt[x][z]]:
                        return False
        return True

    def is_chain(self):
        return all(self.uc[x] == [x + 1] for x in range(len(self.uc) - 1))

    def is_selfdual(self):  # assumes self has a top and bottom
        lc = self.get_lowercovers()
        n = self.cardinality
        perms = [[n - 1] + p + [0] for p in permutations(1, n - 1)]
        for p in perms:
            plc = {}
            for i in range(n):
                plc[p[i]] = sorted([p[y] for y in lc[i]])
            if plc == self.uc:
                return True
        return False

    def make_canonical(self):
        """
        Return a list of (sorted) upper covers that is lex minimal.
        Assumes self has a top and bottom.
        """
        n = self.cardinality
        minuc = [self.uc[i] for i in range(n)]
        perms = [[0] + p + [n - 1] for p in permutations(1, n - 1)]
        for p in perms:
            puc = range(n)
            for i in range(n):
                puc[p[i]] = sorted([p[y] for y in self.uc[i]])
            if puc < minuc:
                minuc = puc
        return minuc

    def join_irreducibles(self):  # find elements with unique lower cover
        lc = self.get_lowercovers()
        return [x for x in range(self.cardinality) if len(lc[x]) == 1]

    def meet_irreducibles(self):
        return [x for x in range(self.cardinality) if len(self.uc[x]) == 1]

    def strong_covers(self):
        J = set(self.join_irreducibles())
        M = self.meet_irreducibles()
        return [x for x in M if self.uc[x][0] in J]

    def is_SI(self):
        if hasattr(self, "uc"):
            # works for lattices only (but not checking if poset is a lattice)
            # check if D(L) has a unique source connected component, i.e.
            # if trans closure has unique component with no outside indegree
            from sage.graphs.digraph import DiGraph
            G = DiGraph(self.D()).transitive_closure()
            C = G.strongly_connected_components()
            return len([c[0] for c in C if G.in_degree(c[0]) == len(c)]) == 1
        # rather check JCon(A) has least element
        return len(ConLat(self).uc[0]) == 1

    def is_simple(self):
        return len(Con(self)) == 2

    def is_lower_bounded(self):
        # check if D(L) is acyclic Cor. 2.39 in Freese-Jezek-Nation
        from sage.graphs.digraph import DiGraph
        G = DiGraph(D(self))
        G.remove_loops()
        return G.is_directed_acyclic()

    def is_upper_bounded(self):
        # check if D(L)dual is acyclic Cor. 2.39 in Freese-Jezek-Nation
        from sage.graphs.digraph import DiGraph
        G = DiGraph(D(self.dual()))
        G.remove_loops()
        return G.is_directed_acyclic()

    def is_bounded(self):
        return self.is_lower_bounded() and self.is_upper_bounded()

    def get_basicsets(self):
        le = self.get_leq()
        J = self.join_irreducibles()
        M = self.meet_irreducibles()
        return [[x for x in J if le[x][y] == 1] for y in M]

    def get_dualbasicsets(self):
        le = self.get_leq()
        J = self.join_irreducibles()
        M = self.meet_irreducibles()
        return [[y for y in M if le[x][y] == 1] for x in J]

    def get_intersectionsystem(self):
        le = self.get_leq()
        J = self.join_irreducibles()
        M = self.meet_irreducibles()
        return [[J.index(x) for x in J if le[x][y] == 1] for y in M]

    def get_unionsystem(self):
        le = self.get_leq()
        J = self.join_irreducibles()
        M = self.meet_irreducibles()
        return [[M.index(y) for y in M if le[x][y] == 1] for x in J]

    def get_galois_str(self):
        # for l in find_lattices(3): print l.get_galois_str().Y
        ji = self.join_irreducibles()
        X = range(len(ji))   # ji[i] is the ith element so ji : X -> self
        f = dict([i, ji.index(i)] for i in ji)  # f is the inverse of ji
        Y = [[f[y] for y in b] for b in self.get_basicsets()]
        return GaloisStr(X, Y, self.num if hasattr(self, 'num') else None)

    def subposet(self, S):  # S a subset of the elements of self
        leq = self.get_leq()
        leq = [[leq[x][y] for y in S] for x in S]
        Q = Posetuc(leq2uc(leq))
        if hasattr(self, 'labels'):
            Q.label = [self.labels[x] for x in S]
        return Q

    def maximals(self):
        return [x for x in range(self.cardinality) if self.uc[x] == []]

    def get_labels(self):
        if hasattr(self, 'labels'):
            return self.labels
        return range(self.cardinality)

    def heights(self):  # assumes P is topologically sorted
        l = [0 for x in range(self.cardinality)]
        for i in range(self.cardinality):
            for j in self.uc[i]:
                if l[j] < l[i] + 1:
                    l[j] = l[i] + 1
        lc = self.get_lowercovers()
        for i in range(self.cardinality):
            if lc[i] == []:
                l[i] = min(l[x] for x in self.uc[i]) - 1
        return l

    def length(self):  # assumes P is topologically sorted
        return max(self.heights())

    def depths(self):  # assumes P is topologically sorted
        l = [0 for x in range(self.cardinality)]
        lc = self.get_lowercovers()
        for i in range(self.cardinality - 1, -1, -1):
            for j in lc[i]:
                if l[j] < l[i] + 1:
                    l[j] = l[i] + 1
        return l

    def ypos(self):
        d = self.depths()
        h = self.heights()
        lth = self.length()
        return [(h[i] + lth - d[i])/2.0 for i in range(self.cardinality)] # antes en vez de hacer /2.0, hacia half

    def dlevels(self):  # P topological
        d = self.depths()
        m = max(d)
        l = [[] for x in range(m + 1)]
        for x in range(self.cardinality):
            l[m - d[x]].append(x)
        return l

    def hlevels(self):  # P topological
        y = self.ypos()
        m = self.length()
        l = [[] for x in range(m + 1)]
        for x in range(self.cardinality):
            l[int(round(y[x]))].append(x)
        return l

    def get_pos(self):  # get [x,y] position for each element
        if hasattr(self, 'pos'):
            return self.pos
        y = self.ypos()
        lev = self.hlevels()
        lengths = [len(x) for x in lev]
        m = max(lengths)
        pos = [[] for i in range(self.cardinality)]
        for l in range(len(lev)):
            n = len(lev[l])
            for i in range(n):
                pos[lev[l][i]] = [i - (n - 1)/2.0, y[lev[l][i]]] # antes en vez de hacer /2.0, hacia half
        self.pos = pos
        return pos

    def linelength(self):
        import math
        emb = self.get_pos()
        n = len(emb)
        l = 0
        for i in range(n):
            for j in self.uc[i]:
                l = l + math.sqrt((emb[i][0] - emb[j][0])**2 + (emb[i][1] - emb[j][1])**2)
        return l

    def is_auto(self, p):
        for i in range(len(p)):
            for j in self.uc[i]:
                if not(p[j] in self.uc[p[i]]):
                    return False
        return True

    def Aut(self):
        n = len(self.uc)
        auto = [p for p in permutations(0, n) if self.is_auto(p)]
        return auto

    def permuted(self, p):  # return permuted copy of self
        puc = range(len(p))
        for i in range(len(p)):
            puc[p[i]] = [p[x] for x in self.uc[i]]
        return Posetuc(puc)

    def dual(self):
        p = range(len(self.uc) - 1, -1, -1)
        lc = self.get_lowercovers()
        return Posetuc(lc).permuted(p)

    def is_lin_ext(self, p):
        puc = self.permuted(p).uc
        for i in range(len(p)):
            for j in puc[i]:
                if not i < j:
                    return False
        return True

    def lin_ext(self):
        n = len(self.uc)
        lin_ext = [p for p in permutations(0, n) if self.is_lin_ext(p)]
        return lin_ext

    def minimize_linelength(self):
        minp = range(len(self.uc))
        minl = self.linelength()
        for p in self.lin_ext():
            ll = self.permuted(p).linelength()
            if ll < minl:
                minl = ll
                minp = p
        return self.permuted(minp)

    def show(self):
        if hasattr(self, "uc"):
            if self.is_lattice():
                self.sage_lattice().show()
            else:
                self.sage_poset().show()
        else:
            print self

    def show3d(self):
        if hasattr(self, "uc"):
            if self.is_lattice():
                self.sage_lattice().show3d()
            else:
                self.sage_poset().show3d()
        else:
            print self

    def mace4format(self):
        if self.is_lattice():
            self.get_join()
        st = "interpretation(" + str(self.cardinality) + ", [number = " + str(self.index) + ", seconds = 0], [\n"
        st += ',\n'.join([" function(" + s + self.aritystr(self.operations[s]) + ", " + str(self.op2li(self.operations[s])).replace(" ", "") + ")" for s in self.operations])
        if len(self.operations) > 0 and len(self.relations) > 0:
            st += ',\n'
        st += ',\n'.join([" relation(" + s + self.aritystr(self.relations[s]) + ", " + str(self.op2li(self.relations[s])).replace(" ", "") + ")" for s in self.relations])
        return st + "])."
    def __op_var_pos_diag(self, s, c):
        """
        Genera una lista de formulas con el diagrama positivo, de la operacion (funcion) s, usando el prefijo c
        """
        op = self.operations
        if type(op[s]) == list:
            base = range(len(op[s]))
            if type(op[s][0]) == list:
                return [c + str(x) + " " + s + " " + c + str(y) + " = " + c + str(op[s][x][y])
                        for x in base for y in base]
            elif s == "'":
                return [c + str(x) + s + " = " + c + str(op[s][x]) for x in base]
            else:
                return [s + "(" + c + str(x) + ") = " + c + str(op[s][x]) for x in base]
        else:
            return [s + " = " + c + str(op[s])]
    def __rel_var_pos_diag(self, s, c):
        """
        Genera una lista de formulas con el diagrama positivo, de la relacion s, usando el prefijo c
        """
        rel = self.relations
        if type(rel[s]) == list:
            base = range(len(rel[s]))
            if type(rel[s][0]) == list:
                if type(rel[s][0][0]) == list:  # if prefix ternary relation
                    return [s + "(" + c + str(x) + "," + c + str(y) + "," + c + str(z) + ")"
                            for x in base for y in base for z in base if rel[s][x][y][z]]
                else:  # if infix binary relation
                    return [c + str(x) + " " + s + " " + c + str(y)
                            for x in base for y in base if rel[s][x][y]]
            else:
                return [s + "(" + c + str(x) + ")" for x in base if rel[s][x]]
        else:
            return "not a relation"
    def __op_var_diag(self, s, c, n=0):
        """
        Genera una lista de formulas con el diagrama positivo, de la operacion (funcion) s, usando el prefijo c, y sumando n a cada elemento
        """
        op=self.operations
        if type(op[s]) == list:
            base = range(len(op[s]))
            if type(op[s][0]) == list:
                return [c + str(x + n) + " " + s + " " + c + str(y + n) + " = " + c + str(op[s][x][y] + n)
                        for x in base for y in base]
            elif s == "'":
                return [c + str(x + n) + s + " = " + c + str(op[s][x] + n) for x in base]
            else:
                return [s + "(" + c + str(x + n) + ") = " + c + str(op[s][x] + n) for x in base]
        else:
            return [s + " = " + c + str(op[s] + n)]
            
    def __rel_var_diag(s, c, n=0):
        """
        Genera una lista de formulas con el diagrama, de la relacion s de rel, usando el prefijo c, y sumando n a cada elemento
        """
        rel = self.relations
        if type(rel[s]) == list:
            base = range(len(rel[s]))
            if type(rel[s][0]) == list:
                if type(rel[s][0][0]) == list:  # prefix ternary relation
                    return [("" if rel[s][x][y][z] else "-") + s + "(" + c + str(x + n) +
                            "," + c + str(y + n) + "," + c + str(z + n) + ")"
                            for x in base for y in base for z in base]
                elif s >= "A" and s <= "Z":  # prefix binary relation
                    return [("" if rel[s][x][y] else "-") + s + "(" + c + str(x + n) +
                            "," + c + str(y + n) + ")" for x in base for y in base]
                else:  # infix binary relation
                    return [("(" if rel[s][x][y] else "-(") + c + str(x + n) + " " +
                            s + " " + c + str(y + n) + ")" for x in base for y in base]
            else:
                return [("" if rel[s][x] else "-") + s + "(" + c + str(x + n) + ")"
                        for x in base]
        else:
            return "not a relation"
    def __op_hom(self, B):
        """
        return string of homomorphism equations
        """
        st = ''
        for s in B.operations:
            if type(B.operations[s]) == list:
                base = range(len(B.operations[s]))
                if type(B.operations[s][0]) == list:
                    st += " & h(x " + s + " y) = h(x) " + s + " h(y)"
                elif s == "'":
                    st += " & h(x') = h(x)'"
                else:
                    st += " & h(" + s + "(x)) = " + s + "(h(x))"
            else:
                st += " & h(" + str(B.operations[s] + A.cardinality) + ") = " + str(self.operations[s])
        return st
    def __permuted_binary_op(self, m, q):

        qi = inverse_permutation(q)
        return [[q[m[qi[x]][qi[y]]] for y in range(len(m))] for x in range(len(m))]

    def D(self):
        # TODO que sera esto?????
        le = self.get_leq()
        uc = self.uc
        lc = self.get_lowercovers()
        J = self.join_irreducibles()
        M = self.meet_irreducibles()
        D = {}
        for a in J:
            D[a] = [b for b in J if any([le[a][uc[q][0]] and not le[a][q] and
                                         le[lc[b][0]][q] and not le[b][q] for q in M])]
        return D

    def aritystr(self, t):
        # lo usa para generar una entrada para mace4
        if type(t) == list:
            if type(t[0]):
                return "(_,_)"
            else:
                "(_)"
        else:
            return ""
    def op2li(self, t):
        # lo usa para generar una entrada para mace4
        if type(t) == list:
            if type(t[0])==list:
                return [x for y in t for x in y]
            else:
                t
        else:
            return [t]
