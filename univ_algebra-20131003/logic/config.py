import os

uapth = 'ua-'
clspth = os.path.join(os.getenv('SAGE_LOCAL'),'bin/')
home = os.getenv('HOME')
print os.getenv('SAGE_LOCAL')
print clspth
print home
datapth = os.path.join(os.getenv('SAGE_ROOT'),'data/univ_algebra/') # solo se usa en readlistfromfile(st), no queda clara la utilidad

minionpath = os.path.join(home,"minion-1.8/bin/") # siempre tienen que terminar en barra
ladrpath = os.path.join(home,"LADR-2009-11A/bin/")
uapath = ""


print "Minion path: %s" % minionpath
print "LADR path: %s" % ladrpath
