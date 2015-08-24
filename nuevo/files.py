#!/usr/bin/env python
# -*- coding: utf8 -*-

import os

def create_pipe(path):
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
    f = open(path, 'w')
    f.write(data)
    f.close()

