from services.rezervari_service import creeaza_rezervare, sterge_rezervare
from services.admin_service import adauga_sala
from services.api_filme_service import adauga_film_din_api


def meniu():
    while True:
        print("\n=== MENIU CINEMA ===")
        print("1. Adaugă sală")
        print("2. Creează rezervare")
        print("3. Anulează rezervare")
        print("4. Adaugă film din API")
        print("0. Ieșire")

        opt = input("Alege opțiunea: ")

        if opt == "1":
            nume = input("Nume sală: ")
            randuri = int(input("Randuri: "))
            locuri = int(input("Locuri pe rând: "))
            sala = adauga_sala(nume, randuri, locuri)
            print(f"Sală adăugată cu ID: {sala['id_sala']}")

        elif opt == "2":
            film = int(input("ID film: "))
            sala = int(input("ID sala: "))
            r = int(input("Rand: "))
            l = int(input("Loc: "))
            rezervare = creeaza_rezervare(film, sala, r, l)
            print("Rezervare creată:", rezervare)

        elif opt == "3":
            rez_id = int(input("ID rezervare de anulat: "))
            sterge_rezervare(rez_id)

        elif opt == "4":
            titlu = input("Titlul filmului: ")
            sala_id = int(input("ID sala: "))
            rezultat = adauga_film_din_api(titlu, sala_id)
            if rezultat:
                print("Film adăugat automat din API cu succes!")
            else:
                print("Nu s-a putut adăuga filmul.")

        elif opt == "0":
            print("La revedere!")
            break

        else:
            print("Opțiune invalidă!")
