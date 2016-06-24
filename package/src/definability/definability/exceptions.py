class Counterexample(Exception):

    def __init__(self, morphism):
        self.morphism = morphism

    def __str__(self):
        return repr(self.morphism)
