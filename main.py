class Sala:
    def __init__(self, id_sala, nume, randuri, locuri_pe_rand):
        self.id_sala = id_sala
        self.nume = nume
        self.randuri = randuri
        self.locuri_pe_rand = locuri_pe_rand
        self.locuri = self.genereaza_locuri()

    def genereaza_locuri(self):
        return [[0 for _ in range(self.locuri_pe_rand)] for _ in range(self.randuri)]

    def afiseaza_locuri(self):
        print(f"\nLocuri pentru {self.nume}:")
        for i, rand in enumerate(self.locuri):
            rand_str = "".join(["[X]" if loc == 1 else "[ ]" for loc in rand])
            print(f"Rând {i}: {rand_str}")


class Film:
    def __init__(self, id_film, titlu, durata, sala):
        self.id_film = id_film
        self.titlu = titlu
        self.durata = durata
        self.sala = sala


def rezerva_loc(film, rand, loc):
    sala = film.sala

    if rand < 0 or rand >= sala.randuri or loc < 0 or loc >= sala.locuri_pe_rand:
        print("Rand sau loc invalid.")
        return

    if sala.locuri[rand][loc] == 1:
        print("Loc deja rezervat!")
    else:
        sala.locuri[rand][loc] = 1
        print("Rezervare efectuată cu succes!")


def main():
    sala1 = Sala(id_sala=1, nume="Sala 1", randuri=5, locuri_pe_rand=8)
    film1 = Film(id_film=1, titlu="Film Demo", durata=120, sala=sala1)

    while True:
        print("\n=== MENIU CINEMA ===")
        print("1. Afișează locurile")
        print("2. Fă o rezervare")
        print("0. Ieșire")

        opt = input("Alege opțiunea: ")

        if opt == "1":
            film1.sala.afiseaza_locuri()
        elif opt == "2":
            try:
                r = int(input("Rând: "))
                c = int(input("Loc: "))
                rezerva_loc(film1, r, c)
            except ValueError:
                print("Introduceți doar numere.")
        elif opt == "0":
            print("La revedere!")
            break
        else:
            print("Opțiune invalidă.")


if __name__ == "__main__":
    main()
