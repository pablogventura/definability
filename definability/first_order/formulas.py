#!/usr/bin/env python
# -*- coding: utf8 -*-

# TERMS

from ..misc.unicode import subscript
from itertools import product

class Term(object):
    """
    Clase general de los terminos de primer orden
    """
    def __init__(self):
        pass
    
    def free_vars(self):
        raise NotImplemented
    
    def evaluate(self, model, vector):
        """
        Evalua el termino en el modelo para el vector de valores
        """
        raise NotImplemented

class Variable(Term):
    """
    Variable de primer orden
    """
    def __init__(self, sym):
        if isinstance(sym,int):
            self.sym = "x" + subscript(sym)
        else:
            self.sym = sym
    
    def __repr__(self):
        return self.sym
    
    def free_vars(self):
        return {self}
    
    def evaluate(self, model, vector):
        try:
            return vector[self]
        except KeyError:
            raise ValueError("Free variable %s is not defined" % (self))
        
class OpSym(object):
    """
    Simbolo de operacion de primer orden
    """
    def __init__(self, op, arity):
        self.op = op
        self.arity = arity

    def __call__(self, *args):
        if len(args) != self.arity or any((not isinstance(a, Term)) for a in args):
            raise ValueError("Arity not correct or any isn't a term")
        
        return OpTerm(self,args)

    def __repr__(self):
        return self.op

class OpTerm(Term):
    """
    Termino de primer orden de la aplicacion de una funcion
    """
    def __init__(self, sym, args):
        self.sym = sym
        self.args = args
    
    def __repr__(self):
        result = repr(self.sym)
        result += "("
        result += ", ".join(map(repr,self.args))
        result += ")"
        return result
    
    def free_vars(self):
        return set.union(*[f.free_vars() for f in self.args])

    def evaluate(self, model, vector):
        args = [t.evaluate(model,vector) for t in self.args]
        return model.operations[self.sym.op](*args)
        
# FORMULAS
    
class Formula(object):
    """
    Clase general de las formulas de primer orden
    
    >>> x,y,z = variables("x","y","z") # declaracion de variables de primer orden
    
    >>> R = RelSym("R",2) # declaro una relacion R de aridad 2
    
    >>> f = OpSym("f",3) # declaro una operacion f de aridad 3
    
    >>> R(x,y) | R(y,x) & R(y,z)
    (R(x, y) ∨ (R(y, x) ∧ R(y, z)))
    
    >>> -R(f(x,y,z),y) | R(y,x) & R(y,z)
    (¬ R(f(x, y, z), y) ∨ (R(y, x) ∧ R(y, z)))

    >>> a = forall(x, -R(f(x,y,z),y))
    >>> a
    ∀ x ¬ R(f(x, y, z), y)
    >>> a.free_vars() == {y,z}
    True
    
    >>> a = R(x,x) & a
    >>> a
    (R(x, x) ∧ ∀ x ¬ R(f(x, y, z), y))
    >>> a.free_vars() == {x, y, z}
    True

    >>> exists(x, R(f(x,y,z),y))
    ∃ x R(f(x, y, z), y)
    """
    def __init__(self):
        pass
    
    def __and__(self, other):
        return AndFormula(self,other)

    def __or__(self, other):
        return OrFormula(self,other)
    
    def __neg__(self):
        return NegFormula(self)
        
    def free_vars(self):
        raise NotImplemented
    
    def satisfy(self,model,vector):
        raise NotImplemented

class NegFormula(Formula):
    """
    Negacion de una formula
    """
    def __init__(self, f):
        self.f = f
    
    def __repr__(self):
        return "¬ %s" % self.f
    
    def free_vars(self):
        return self.f.free_vars()

    def satisfy(self,model,vector):
        return not self.f.satisfy(model,vector)
    

class BinaryOpFormula(Formula):
    """
    Clase general de las formulas tipo f1 η f2
    """
    def __init__(self, f1, f2):
        self.f1 = f1
        self.f2 = f2

    def free_vars(self):
        return self.f1.free_vars().union(self.f2.free_vars())
        
class OrFormula(BinaryOpFormula):
    """
    Disjuncion entre formulas
    """
    def __repr__(self):
        result = "(%s ∨ %s)" % (self.f1, self.f2)
        return result
    
    def satisfy(self,model,vector):
        # el or y el and de python son lazy
        return self.f1.satisfy(model,vector) or self.f2.satisfy(model,vector)

class AndFormula(BinaryOpFormula):
    """
    Conjuncion entre formulas
    """
    def __repr__(self):
        result = "(%s ∧ %s)" % (self.f1, self.f2)
        return result

    def satisfy(self,model,vector):
        # el or y el and de python son lazy
        return self.f1.satisfy(model,vector) and self.f2.satisfy(model,vector)

class RelSym(object):
    """
    Simbolo de relacion de primer orden
    """
    def __init__(self, rel, arity):
        self.rel = rel
        self.arity = arity

    def __call__(self, *args):
        if len(args) != self.arity or any((not isinstance(a, Term)) for a in args):
            raise ValueError("Arity not correct or any isn't a term")
        
        return RelFormula(self,args)

    def __repr__(self):
        return self.rel

class RelFormula(Formula):
    """
    Formula de primer orden de la aplicacion de una relacion
    """
    def __init__(self, sym, args):
        self.sym = sym
        self.args = args
    
    def __repr__(self):
        result = repr(self.sym)
        result += "("
        result += ", ".join(map(repr,self.args))
        result += ")"
        return result
    
    def free_vars(self):
        return set.union(*[f.free_vars() for f in self.args])

    def satisfy(self, model, vector):
        args = [t.evaluate(model,vector) for t in self.args]
        return model.relations[self.sym.rel](*args)

class EqFormula(Formula):
    """
    Formula de primer orden que es una igualdad entre terminos
    """
    def __init__(self, t1, t2):
        if not (isinstance(t1, Term) and isinstance(t2, Term)):
            raise ValueError("Must be terms")
            
        self.t1=t1
        self.t2=t2
    
    def __repr__(self):
        return "%s == %s" % (self.t1,self.t2)
    
    def free_vars(self):
        return set.union(self.t1.free_vars(), self.t2.free_vars())

    def satisfy(self, model, vector):
        return self.t1.evaluate(model,vector) == self.t2.evaluate(model,vector)
        
class QuantifierFormula(Formula):
    """
    Clase general de una formula con cuantificador
    """
    def __init__(self, var, f):
        self.var = var
        self.f = f
    
    def free_vars(self):
        return self.f.free_vars() - {self.var}
        
class ForAllFormula(QuantifierFormula):
    """
    Formula Universal
    """
    def __repr__(self):
        return "∀ %s %s" % (self.var, self.f)

    def satisfy(self, model, vector):
        for i in model.universe:
            vector[self.var] = i
            if not self.f.satisfy(model,vector):
                return False
        return True

class ExistsFormula(QuantifierFormula):
    """
    Formula Existencial
    """
    def __repr__(self):
        return "∃ %s %s" % (self.var, self.f)

    def satisfy(self, model, vector):
        vector = vector.copy()
        for i in model.universe:
            vector[self.var] = i
            print(vector)
            if self.f.satisfy(model,vector):
                return True
        return False

# Shortcuts

def variables(*lvars):
    """
    Declara variables de primer orden
    """
    return tuple(Variable(x) for x in lvars)

def forall(var, formula):
    """
    Devuelve la formula universal
    """
    return ForAllFormula(var, formula)

def eq(t1,t2):
    return EqFormula(t1,t2)

def exists(var, formula):
    """
    Devuelve la formula existencial
    """
    return ExistsFormula(var, formula)

def atomics(relations, arity):
    """
    Genera todas las formulas atomicas con relations 
    de arity variables libres

    >>> R = RelSym("R",2)
    >>> list(atomics([R],2))
    [R(x₀, x₀), R(x₀, x₁), R(x₁, x₀), R(x₁, x₁)]
    """
    vs = variables(*range(arity))
    for r in relations:
        for t in product(vs,repeat=r.arity):
            yield r(*t)
        
