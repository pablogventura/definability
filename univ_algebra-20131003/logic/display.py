def opstr(m):
    """
    Convert 2-dim list to a compact string for display
    """
    nr = len(m)
    if nr == 0:
        return "[]"
    nc = len(m[0])
    s = [[str(y).replace(' ', '') for y in x] for x in m]
    width = [max([len(s[x][y]) for x in range(nr)]) for y in range(nc)]
    s = [[" " * (width[y] - len(s[x][y])) + s[x][y] for y in range(nc)]
         for x in range(nr)]
    rows = ["[" + ",".join(x) + "]" for x in s]
    s = "[\n" + ",\n".join(rows) + "]"
    return s


def oprelstr(oprel):
    """
    Convert a list of operations or relations to a string
    """
    st = ''
    for x in oprel:
        if type(oprel[x]) == list and type(oprel[x][0]) == list:
            st += '\n"' + x + '":' + opstr(oprel[x]) + ', '
        else:
            st += '"' + x + '":' + str(oprel[x]) + ', '
    return st[:-2]

def xmlopstr(m):  # convert 2-dim list to a compact string for display
    nr = len(m)
    nc = len(m[0])
    s = [[str(y).replace(' ', '') for y in x] for x in m]
    width = [max([len(s[x][y]) for x in range(nr)]) for y in range(nc)]
    s = [[" " * (width[y] - len(s[x][y])) + s[x][y] for y in range(nc)]
         for x in range(nr)]
    rows = ["            <row r=\"[" + str(i) + "]\">" + ",".join(s[i]) +
            "</row>" for i in range(len(s))]
    s = "\n".join(rows)
    return s + "\n"
