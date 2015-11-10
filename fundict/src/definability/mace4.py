import subprocess as sp
import re
import config
from model import FO_Model  # para los contraejemplos
from fofunctions import FO_Operation, FO_Relation
from fotype import FO_Type


def getops(li, st):
    # TODO , PARECIERA QUE DEBERIA SER UN METODO INTERNO DE LOS MODELOS QUE
    # DEVUELVE MACE4
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


class Mace4Sol(object):

    """
    Maneja las soluciones que genera Mace4 sin usar threads
    """

    def __init__(self, assume_list, mace_seconds=30, domain_cardinality=None, one=False, noniso=True, options=[]):

        self.EOF = False
        self.solutions = []

        self.apps = []  # subprocesos

        self.assume_list = assume_list
        self.options = options
        self.goal_list = []
        maceargs = []
        if domain_cardinality:
            st = str(domain_cardinality)
            # set skolem_last
            maceargs = ["-n", st, "-N", st] + \
                ([] if one else ["-m", "-1"]) + ["-S", "1"]
        mace4app = sp.Popen([config.ladr_path + "mace4", "-t", str(mace_seconds)
                             ] + maceargs, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        mace4app.stdin.write(self.generate_input())
        mace4app.stdin.close()  # TENGO QUE MANDAR EL EOF!
        self.apps.append(mace4app)

        if domain_cardinality is not None and not one and noniso:
            interp1app = sp.Popen(
                [config.ladr_path + "interpformat", "standard"], stdin=mace4app.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
            isofilterapp = sp.Popen([config.ladr_path + 'isofilter',
                                     'check',
                                     "+ * v ^ ' - ~ \\ / -> B C D E F G H I J K P Q R S T U V W b c d e f g h i j k p q r s t 0 1 <= -<",
                                     'output',
                                     "+ * v ^ ' - ~ \\ / -> B C D E F G H I J K P Q R S T U V W b c d e f g h i j k p q r s t 0 1 <= -<"],
                                    stdin=interp1app.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
            interp2app = sp.Popen([config.ladr_path + "interpformat", "portable"],
                                  stdin=isofilterapp.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
            self.apps += [interp1app, isofilterapp, interp2app]
            self.__stdout = interp2app.stdout
        else:
            interpapp = sp.Popen([config.ladr_path + "interpformat", "portable"],
                                 stdin=mace4app.stdout, stdout=sp.PIPE, stderr=sp.PIPE)
            self.apps.append(interpapp)
            self.__stdout = interpapp.stdout
        self.__stderr = mace4app.stderr

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

    def __parse_solution(self):
        buf = ""
        line = self.__stdout.readline()  # quita el [ del principio
        while line:
            # No hubo EOF
            if line == "[\n" or line == "]\n":
                # son las lineas del principio o del final
                line = self.__stdout.readline()
                continue
            else:
                buf += line

            if buf.count("[") and buf.count("[") == buf.count("]"):
                # hay un modelo completo
                buf = buf.replace("\n", "")  # quito saltos de linea
                buf = buf.strip()  # quito espacios para poder sacar la coma
                if buf[-1] == ",":
                    buf = buf[:-1]  # saco la coma!
                m = eval(buf)
                operations = getops(m[2], 'function')
                relations = getops(m[2], 'relation')
                fo_type = FO_Type({name: operations[name].arity() for name in operations.iterkeys()},
                                  {name: relations[name].arity()
                                   for name in relations.iterkeys()}
                                  )
                return FO_Model(fo_type, range(m[0]), getops(m[2], 'function'), getops(m[2], 'relation'))
            else:
                # no hay un modelo completo
                line = self.__stdout.readline()  # necesita otra linea
                continue

        assert not line
        # Hubo EOF
        self.EOF = True
        self.__terminate()

    def __iter__(self):
        """
        Itera sobre las soluciones ya parseadas y despues
        sigue con las sin parsear.
        """
        for solution in self.solutions:
            yield solution

        while not self.EOF:
            solution = self.__parse_solution()
            if solution:
                self.solutions.append(solution)
                yield solution

    def __getitem__(self, index):
        """
        Toma un elemento usando __iter__
        """
        try:
            return self.solutions[index]
        except IndexError:
            for i, solution in enumerate(self):
                if i == index:
                    # no hace falta aplicar self.fun porque esta llamando a
                    # __iter__
                    return solution
            raise IndexError("There aren't so many solutions.")

    def __nonzero__(self):
        """
        Devuelve True si hay soluciones, o bloquea hasta confirmar que no
        hay y devuelve False.
        """
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
        """
        Bloquea hasta parsear todas las soluciones y devuelve la cantidad.
        """
        if not self.EOF:
            for i in self:
                pass
        return len(self.solutions)

    def __terminate(self):
        self.EOF = True
        for app in self.apps:
            app.kill()
            app.wait()
            del app

    def __del__(self):
        if not self.EOF:
            self.__terminate()
