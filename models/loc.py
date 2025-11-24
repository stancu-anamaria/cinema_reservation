class Loc:
    def __init__(self, rand, numar, rezervat=False):
        self.rand = rand
        self.numar = numar
        self.rezervat = rezervat

    def __repr__(self):
        return f"<Loc R{self.rand} L{self.numar} {'REZERVAT' if self.rezervat else 'LIBER'}>"
