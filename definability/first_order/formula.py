#!/usr/bin/env python
# -*- coding: utf8 -*-

# TERMS
class Term(object):
    """
    Clase general de los terminos de primer orden
    """
    def __init__(self):
        pass

class Variable(Term):
    """
    Variable de primer orden
    """
    def __init__(self, sym):
        self.sym = sym
    
    def __repr__(self):
        return self.sym
        
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
    (¬ (R(f(x, y, z), y)) ∨ (R(y, x) ∧ R(y, z)))

    >>> forall(x, -R(f(x,y,z),y))
    ∀ x ¬ (R(f(x, y, z), y))

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

class NegFormula(Formula):
    """
    Negacion de una formula
    """
    def __init__(self, f):
        self.f = f
    
    def __repr__(self):
        return "¬ (%s)" % self.f

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

class ForAllFormula(Formula):
    """
    Formula Universal
    """
    def __init__(self, var, f):
        self.var = var
        self.f = f
    
    def __repr__(self):
        return "∀ %s %s" % (self.var, self.f)

class ExistsFormula(Formula):
    """
    Formula Existencial
    """
    def __init__(self, var, f):
        self.var = var
        self.f = f
    
    def __repr__(self):
        return "∃ %s %s" % (self.var, self.f)

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
