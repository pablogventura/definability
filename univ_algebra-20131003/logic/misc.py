def readfile(fname):
    fh = open(fname)
    st = fh.read()
    fh.close()
    return st


def writefile(fname, st):
    fh = open(fname, 'w')
    fh.write(st)
    fh.close()
