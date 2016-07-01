#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
Modulo de configuracion
"""

import os

home = os.getenv('HOME')

# siempre tienen que terminar en barra
minion_path = os.path.join(home, "minion-1.8/bin/")

ladr_path = os.path.join(home, "LADR-2009-11A/bin/")

lat_draw_path = os.path.join(home, "LatDraw2.0/dist/lib/")
# print "Minion path: %s" % minion_path
