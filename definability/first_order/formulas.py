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

class OrFormula(Formula):
    """
    Disjuncion entre formulas
    """
    def __init__(self, f1, f2):
        self.f1 = f1
        self.f2 = f2
    
    def __repr__(self):
        result = "(%s ∨ %s)" % (self.f1, self.f2)
        return result

    def free_vars(self):
        return self.f1.free_vars().union(self.f2.free_vars())

class AndFormula(Formula):
    """
    Conjuncion entre formulas
    """
    def __init__(self, f1, f2):
        self.f1 = f1
        self.f2 = f2
    
    def __repr__(self):
        result = "(%s ∧ %s)" % (self.f1, self.f2)
        return result

    def free_vars(self):
        return self.f1.free_vars().union(self.f2.free_vars())

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
        

class ForAllFormula(Formula):
    """
    Formula Universal
    """
    def __init__(self, var, f):
        self.var = var
        self.f = f
    
    def __repr__(self):
        return "∀ %s %s" % (self.var, self.f)
    
    def free_vars(self):
        return self.f.free_vars() - {self.var}

class ExistsFormula(Formula):
    """
    Formula Existencial
    """
    def __init__(self, var, f):
        self.var = var
        self.f = f
    
    def __repr__(self):
        return "∃ %s %s" % (self.var, self.f)

    def free_vars(self):
        return self.f.free_vars() - {self.var}
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
        
