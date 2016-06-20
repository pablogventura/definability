#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import pickle

def object_to_file(obj, path):
    f = file(path,"a")
    pickle.dump(obj,f)
    f.close()

def file_to_object(path):
    f = file(path,"r")
    obj = pickle.load(f)
    f.close()
    return obj

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
