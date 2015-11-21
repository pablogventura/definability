from model import *
posetdiamante = Model(5,relations={"<=":ListWithArity([[1,1,1,1,1],[0,1,0,0,0],[0,1,1,0,0],[0,1,0,1,0],[0,1,0,0,1]])})
posetcadena2 = Model(2,relations = {'<=':ListWithArity([[1, 0],[1, 1]])})


import random
from model import Model
def random_examples(models=1,cardinality=None,cantop=1,cantrel=1,seed=None):
    """
    Solo genera cosas con aridad 2
    """
    random.seed(seed)
    for n_model in range(models):
        operations = {}
        for op in range(cantop):
            name = "o%s" % op
            operations[name] = []
            for i in range(cardinality):
                operations[name].append([random.randrange(cardinality) for j in range(cardinality)])
        relations = {}
        for rel in range(cantrel):
            name = "r%s" % rel
            relations[name] = []
            for i in range(cardinality):
                relations[name].append([random.randint(0,1) for j in range(cardinality)])

        yield Model(cardinality, None, operations, relations )
    
