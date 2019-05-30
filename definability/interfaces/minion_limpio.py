#!/usr/bin/env python
# -*- coding: utf8 -*-

# Minion interface code Peter Jipsen 2011-03-26 alpha version
# requires sage.chapman.edu/sage/minion_20110326.spkg

import codecs
import subprocess as sp
from select import poll, POLLIN

from ..interfaces import config
from ..interfaces import files
from itertools import product
from collections import defaultdict
from ..misc import misc


class MinionSolLimpio(object):
    count = 0

    def __init__(self, input_data, allsols=True, fun=lambda x: x):
        """
        Toma el input para minion, si espera todas las soluciones y una funcion para aplicar
        a las listas que van a ir siendo soluciones.
        """
        self.id = MinionSolLimpio.count
        MinionSolLimpio.count += 1

        self.fun = fun
        self.allsols = allsols

        self.input_filename = config.minion_path + "input_minion%s" % self.id
        files.create_pipe(self.input_filename)

        minionargs = ["-printsolsonly", "-randomseed", "0"]
        if allsols:
            minionargs += ["-findallsols"]
        minionargs += [self.input_filename]

        self.minionapp = sp.Popen([config.minion_path + "minion"] + minionargs,
                                  stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        files.write(self.input_filename, input_data)
        self.EOF = False
        self.solutions = []

    def __parse_solution(self):
        """
        Bloquea hasta conseguir una solucion, o el EOF
        La parsea y devuelve una lista
        """
        str_sol = self.minionapp.stdout.readline().decode('utf-8')
        if str_sol:
            str_sol = str_sol[:-1]  # borro el \n
            try:
                result = list(map(int, str_sol.strip().split(" ")))
                for i, v in enumerate(result):
                    if v == -1:
                        result[i] = None
                result = {(i,):v for i,v in enumerate(result)}
                # ACA IRIAN LAS TRADUCCIONES DE NOMBRES EN EL FUTURO
            except ValueError:
                str_sol += "\n"
                # leo toda la respuesta de minion para saber que paso
                str_sol += self.minionapp.stdout.read().decode('utf-8')
                raise ValueError("Minion Error:\n%s" % str_sol)
            if not self.allsols:
                self.EOF = True
                self.__terminate()
            return result
        else:
            str_err = self.minionapp.stderr.read().decode('utf-8')
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
            for i, solution in enumerate(self):
                if i == index:
                    # no hace falta aplicar self.fun porque esta llamando a
                    # __iter__
                    return solution
            raise IndexError("There aren't so many solutions.")

    def __bool__(self):
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
        """
        Mata a Minion
        """
        if hasattr(self, 'minionapp'):
            self.minionapp.stdout.close()
            self.minionapp.stdin.close()
            self.minionapp.stderr.close()
            self.minionapp.kill()

            del self.minionapp
        files.remove(self.input_filename)

    def __del__(self):
        """
        Si no lo habia matado, mata a Minion.
        """
        if not self.EOF:
            self.__terminate()

class ParallelMinionSolLimpio(object):

    """
    Maneja varias consultas del mismo tipo a Minion que corren en paralelo.
    """

    def __init__(self, minion_inputs, allsols=False, cores=10):

        self.minion_inputs = iter(minion_inputs)
        self.allsols = allsols
        self.solution = None

        self.poll = poll()
        self.minions = {}
        self.iterators = {}

        for i in range(cores):
            self.next_to_running()

    def next_to_running(self):
        """
        Pone a la siguiente instancia de Minion a andar
        """
        try:
            minion_input = next(self.minion_inputs)
            new_minion = MinionSolLimpio(minion_input,allsols=self.allsols)
            fd = new_minion.minionapp.stdout.fileno()
            self.minions[fd] = new_minion
            self.iterators[fd] = iter(new_minion)
            self.poll.register(fd, POLLIN)
        except StopIteration:
            return

    def read(self, fd):
        """
        Lee un file descriptor y lo vuelve a poner en el poll
        """
        if self.minions[fd]:
            result = self.minions[fd][0]
        else:
            result = False
        del self.minions[fd]
        del self.iterators[fd]
        self.poll.unregister(fd)
        return result

    def solve(self):
        """
        Devuelve si hay una solucion, en cuyo caso la devuelve.
        """
        if self.solution is None:
            while self.queue or self.minions:
                for (fd, event) in self.poll.poll():
                    result = self.read(fd)
                    if result:
                        self.solution = result
                        if not self.allsols:
                            for f in list(self.minions.keys()):
                                self.minions[f].__del__()
                        return self.solution
                    else:
                        if self.queue:
                            self.next_to_running()
            self.solution = False
            return False
        else:
            return self.solution

    def __iter__(self):
        while self.minions:
            for (fd, event) in self.poll.poll():
                try:
                    result = next(self.iterators[fd])
                    assert not self.minions[fd].EOF
                    self.poll.register(fd, POLLIN)
                    yield result
                except StopIteration:
                    assert self.minions[fd].EOF
                    self.poll.unregister(fd)
                    self.minions[fd].__del__()
                    del self.minions[fd]
                    self.next_to_running()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
