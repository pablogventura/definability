#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
Modulo de configuracion
"""

import os

home = os.getenv('HOME')

minion_path = os.path.join(home, "minion-1.8/bin/")  # siempre tienen que terminar en barra

# print "Minion path: %s" % minion_path

if __name__ == "__main__":
    import doctest
    doctest.testmod()
