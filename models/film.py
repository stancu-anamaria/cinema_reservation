class Film:
    def __init__(self, id_film, titlu, durata, sala_id):
        self.id_film = id_film
        self.titlu = titlu
        self.durata = durata
        self.sala_id = sala_id

    def __repr__(self):
        return f"<Film {self.id_film}: {self.titlu}>"
