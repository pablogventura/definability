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
