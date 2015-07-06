import pickle

DEBUG = True

def printlog(text):
    global DEBUG
    if DEBUG:
        print "DEBUG MSG: %s" % text

def readfile(fname):
    fh = open(fname)
    st = fh.read()
    fh.close()
    return st

def writefile(fname, st):
    fh = open(fname, 'w')
    fh.write(st)
    fh.close()
    
def objtofile(obj,path):
    f = open(path,"w")
    pickle.dump(obj, f)
    f.close()

def filetoobj(path):
    f = open(path,"r")
    result = pickle.load(f)
    f.close()
    return result


