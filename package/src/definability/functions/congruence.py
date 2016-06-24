#!/usr/bin/env python
# -*- coding: utf8 -*-

from ..first_order.fofunctions import FO_Relation

class Eq_Rel(FO_Relation):

	"""
	Relacion binaria que cumple los axiomas de equivalencia
	"""

	def __init__(self, d, model):
		assert d and isinstance(d,list) and isinstance(d[0],tuple)
		self.model = model
		self.d = d
		super(Eq_Rel, self).__init__(d,model.universe)
		assert self.simetrico() and self.reflexivo() and self.transitivo()

	def reflexivo(self):
		for x in self.model.universe:
			if not (x,x) in self.d:
				return False
		return True

	def simetrico(self):
		for r in self.d:
			if not (r[1],r[0]) in self.d:
				return False
		return True

	def transitivo(self):
		for r in self.d:
			for s in self.d:
				if r[1] == s[0]:
					if not (r[0],s[1]) in self.d:
						return False
		return True

		

class Congruence(Eq_Rel):

	"""
	Congruencia 
	"""

	def __init__(self, d, model):
		assert d and isinstance(d,list) and isinstance(d[0],tuple)
		assert model
		self.model = model
		self.d = d
		super(Congruence, self).__init__(d, model)
		assert self.preserva_relaciones()
		assert self.preserva_operaciones()

	def relacionados(self, t, s):
		for i in range(len(t)):
			if not (t[i],s[i]) in self.d:
				return False
		return True

	def __preserva_relacion(self, rel):
		for t in self.model.relations[rel]:
			for s in self.model.relations[rel].domain():
				if self.relacionados(t,list(s)):
					if not list(s) in self.model.relations[rel]:
						return False
		return True

	def preserva_relaciones(self):
		result = True
		for rel in self.model.relations:
			result = result and self.__preserva_relacion(rel)
		return result

	def __preserva_operacion(self,op):
		for t in self.model.operations[op].domain():
			for s in self.model.operations[op].domain():
				if self.relacionados(t,s):
					if not (self.model.operations[op](t[0],t[1]),self.model.operations[op](s[0],s[1])) in self.d:
						return False
		return True

	def preserva_operaciones(self):
		result = True
		for op in self.model.operations:
			result = result and self.__preserva_operacion(op)
		return result