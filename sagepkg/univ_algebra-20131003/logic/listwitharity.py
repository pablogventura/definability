import numpy as np
from itertools import product

class ListWithArity(object):

    """
    Define a las listas que se usan para tener operaciones y relaciones.
    Las relaciones simplemente son operaciones con 0 o 1 como salida.
    """
    def __init__(self, l):
        if issubclass(type(l),ListWithArity):
            # clono el arreglo
            self.array = np.copy(l.array)
        else:
            # nuevo array
            self.array = np.array(l)
    
    def domain(self):
        """
        Un generador del dominio
        """
        return product(range(len(self)), repeat=self.arity())

    def arity(self):
        return self.array.ndim
    def __len__(self):
        return len(self.array)
    def restrict(self,elements):
        """
        Restringe el dominio a sorted(elements).
        """
        elements.sort() # lo ordeno para tener una forma clara de armar el embedding

        # tengo que hacer reemplazos de nombre
        result = np.copy(self.array)
        i=0
        for k in elements:
            result[self.array==k] = i
            i+=1
        
        # tengo que borrar filas y columnas
        args = [elements for i in range(self.arity())]
        return ListWithArity(result[np.ix_(*args)].tolist())

            
    def composition(self,g):
        """
        Compone con otra list with arity, F.compone(G) = F o G
        y devuelve una nueva list with arity
        """
        assert self.arity() == 1 and g.arity() == 1
        result = ListWithArity(g)
        result.map_in_place(self)
        return result
        
        
    def map_in_place(self, f):
        """
        Funciona como un map, pero respeta la estructura de la matriz.
        """
        a = self.array.reshape(-1)
        for i, v in enumerate(a):
            a[i] = f(v)

    def __call__(self, *args):
        assert len(args) == self.arity()
        if len(args)==0:
            args = [0]
        result = self.array
        for i in args:
            result = result[i]
        return result

    def __repr__(self):
        result = "ListWithArity([\n"
        for row in self.array:
            result += str(row) + ",\n"
        result += "]"
        return result

    def minion_table(self, table_name, relation=False):
        """
        Devuelve un string con la tabla que representa a la relacion/operacion en minion
        """
        table = self.table(relation)
        height = len(table)
        width = len(table[0])
        result = ""
        for row in table:
            result += " ".join(map(str, row)) + "\n"
        result = "%s %s %s\n" % (table_name, height, width) + result
        return result

    def table(self, relation=False):
        """
        Devuelve una lista de listas con la tabla que representa a la relacion/operacion
        """
            
        cardinality = len(self)
        result = []
        for t in self.domain():
            if not relation or self(*t):
                result.append(list(t))
                if not relation:
                    result[-1].append(self(*t))
        if len(result)==0:
            result.append([])
        return result
    def is_constant(self):
        return self.arity() == 0
    def is_relation(self):
        return not self.is_constant() and set([x[-1] for x in self.table()]) == set([0,1])
    def is_operation(self):
        return not self.is_constant() and not self.is_relation()
