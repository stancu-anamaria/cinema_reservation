class Rezervare:
    def __init__(self, id_rezervare, film_id, sala_id, rand, loc):
        self.id_rezervare = id_rezervare
        self.film_id = film_id
        self.sala_id = sala_id
        self.rand = rand
        self.loc = loc

    def __repr__(self):
        return f"<Rezervare {self.id_rezervare}: Film {self.film_id}, Sala {self.sala_id} -> R{self.rand} L{self.loc}>"
