from mace4 import Mace4Sol


class FO_Theory():
    FO_Theories = []
    FirstOrderClasses = []

    def __init__(self, abbr, name, axioms, results=[], options=[], syntax='Prover9'):
        """
        Define a first-order class of models by a list of first-order axioms

        INPUT:
            abbr    -- a short string without spaces abbreviating the name
            name    -- a string giving the name of the class
            axioms  -- list of strings in the given syntax
            results -- list of strings in the given syntax
            options -- list of strings defining the syntax
            syntax  -- a string indicating which program can parse the 
                       axioms, results and options
        """
        self.abbr = abbr
        self.name = name
        self.syntax = syntax
        self.axioms = axioms
        self.results = results
        self.options = options
        FO_Theory.FO_Theories.append(abbr)
        FO_Theory.FO_Theories.sort(key=str.lower)
        FO_Theory.FirstOrderClasses.append(name + " (" + abbr + ")")
        FO_Theory.FirstOrderClasses.sort(key=str.lower)

    def __repr__(self):
        """
        Display a first-order class in a way that can be parsed by Python
        """
        st = 'FO_Theory(\"' + self.name + '\", syntax=\"' + self.syntax +\
             '\"' + ', axioms=[ \n\"' + '\",\n\"'.join(self.axioms) + '\"]'
        if self.options != []:
            st += ',\noptions=[ \n\"' + '\",\n\"'.join(self.options) + '\"]'
        if self.results != []:
            st += ',\nresults=[ \n\"' + '\",\n\"'.join(self.results) + '\"]'
        return st + ')'

    def subclass(self, abbr, name, arg, results=[], options=[]):
        """
        Add a list of axioms or another FO class to the current one.

        INPUT:
            abbr -- a short name (string) for the new FO subclass
            name -- a string naming the new FO subclass
            arg -- a list of axioms or an existing FO_Theory using same syntax
        """
        if type(arg) != list:
            arg = arg.axioms  # assume its another FO_Theory
        newaxioms = self.axioms + [a for a in arg if a not in self.axioms]
        return FO_Theory(abbr, name, newaxioms, results, options)

    def is_subclass(self, cls, seconds=60):
        """
        Return True if every axiom of cls is provable in self (in given time)
        """
        proofs = []
        for ax in cls.axioms:
            p = prover9(self.axioms, [ax], seconds, self.options)
            if type(p) == list:
                print ax, "proved"
            else:
                print ax, p
                return False, 'No conclusions'
            proofs.append(p)
        return True, proofs

    def is_not_subclass(self, cls, seconds=60):
        """
        Return True if some model of self is not a model of cls (in given time)
        """
        st = '(' + ') & ('.join(cls.axioms) + ')'
        m = prover9(self.axioms, [st], seconds, 1, options=self.options)
        if type(m) == list:
            return True, m[0]
        else:
            return False, m

    def tfae(self, lst):
        """
        Return True if all statements in lst are equivalent given self.axioms
        """
        s = lst + [lst[0]]
        for i in range(len(lst)):
            p = prover9(
                self.axioms + [s[i]], [s[i + 1]], seconds, self.options)
            if type(p) == list:
                print i, "->", i + 1, ":", s[i + 1], "proved"
            else:
                print i, "->", i + 1, ":", p
                return False, 'No conclusions'
            proofs.append(p)
        return True, proofs

    def find_models(self, cardinality, seconds=60):
        """
        Find models of given (finite) cardinality for the axioms 
        of the FO_Theory self.
        """
        return Mace4Sol(self.axioms, mace_seconds=seconds, domain_cardinality=cardinality, options=self.options)

    def count_models(self, upto=20, seconds=60000):
        """
        Find number of nonisomorphic models for the axioms of the FO_Theory self.
        """
        m = []
        for i in range(2, upto + 1):
            m.append(len(self.find_models(i)))
        return m

    def find_joint_extension(self, modelb, modelc, mace_time=10, prover_time=60):
        """
        Find models that extend the two given models in the FO_Theory self.
        """
        n = modelb.cardinality
        ne = ['b' + str(x) + '!=b' + str(y) for x in range(n)
              for y in range(x + 1, n)]
        n = modelc.cardinality
        ne += ['c' + str(x) + '!=c' + str(y) for x in range(n)
               for y in range(x + 1, n)]
        return prover9(self.axioms + ne + modelb.positive_diagram('b') +
                       modelc.positive_diagram('c'), [], mace_time, prover_time)

    def check_results(self, seconds=60, indices=None):
        if indices is None:
            indices = range(len(self.results))
        proofs = []
        for i in indices:
            p = prover9(self.axioms, [self.results[i]], seconds, self.options)
            if type(p) == list:
                print i + 1, ":", self.results[i], "proved"
            else:
                print i + 1, ":", self.results[i], p
            proofs.append(p)
        return proofs

    def check_irredundance(self, seconds=60, indices=None):
        ax = self.axioms
        ml = []
        if indices is None:
            indices = range(len(ax))
        for i in indices:
            m = prover9(
                ax[:i] + ax[i + 1:], [ax[i]], seconds, 0, options=self.options)
            if type(m) == str:
                print ax[i], "is redundant"
                return False
            else:
                ml.append(m)
        return True, ml
