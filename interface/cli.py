from services.rezervari_service import creeaza_rezervare, sterge_rezervare
from services.admin_service import adauga_film, adauga_sala


def meniu():
    while True:
        print("\n=== MENIU CINEMA ===")
        print("1. Adaugă film")
        print("2. Adaugă sală")
        print("3. Creează rezervare")
        print("4. Anulează rezervare")
        print("0. Ieșire")

        opt = input("Alege opțiunea: ")

        if opt == "1":
            titlu = input("Titlu film: ")
            durata = int(input("Durata: "))
            sala_id = int(input("ID sala: "))
            adauga_film(1, titlu, durata, sala_id)

        elif opt == "2":
            nume = input("Nume sală: ")
            randuri = int(input("Randuri: "))
            locuri = int(input("Locuri pe rând: "))
            adauga_sala(1, nume, randuri, locuri)

        elif opt == "3":
            film = int(input("ID film: "))
            sala = int(input("ID sala: "))
            r = int(input("Rand: "))
            l = int(input("Loc: "))
            print(creeaza_rezervare(film, sala, r, l))

        elif opt == "4":
            rez_id = int(input("ID rezervare: "))
            sterge_rezervare(rez_id)

        elif opt == "0":
            break
        else:
            print("Opțiune invalidă!")
