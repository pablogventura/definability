#!/usr/bin/env python
# -*- coding: utf8 -*-

import os


def create_pipe(path):
    """
    Crea un named pipe
    """
    try:
        os.mkfifo(path)
    except OSError:
        # ya existe
        pass


def remove(path):
    try:
        os.remove(path)
    except OSError:
        # no existe
        pass


def read(path):
    f = open(path)
    data = f.read()
    f.close()
    return data


def write(path, data):
    """
    Escribe datos en un archivo
    """
    f = open(path, 'w')
    f.write(data)
    f.close()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
