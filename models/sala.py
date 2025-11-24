class Sala:
    def __init__(self, id_sala, nume, randuri, locuri_pe_rand):
        self.id_sala = id_sala
        self.nume = nume
        self.randuri = randuri
        self.locuri_pe_rand = locuri_pe_rand
        self.locuri = self.genereaza_locuri()

    def genereaza_locuri(self):
        return [[0 for _ in range(self.locuri_pe_rand)]
                for _ in range(self.randuri)]

    def __repr__(self):
        return f"<Sala {self.id_sala}: {self.nume}>"
