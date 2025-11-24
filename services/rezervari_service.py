import json
from models.rezervare import Rezervare

DATAFILE = "data/rezervari.json"


def incarca_rezervari():
    try:
        with open(DATAFILE, "r") as f:
            return json.load(f)
    except:
        return []


def salveaza_rezervari(lista):
    with open(DATAFILE, "w") as f:
        json.dump(lista, f, indent=4)


def creeaza_rezervare(film_id, sala_id, rand, loc):
    rezervari = incarca_rezervari()

    new_id = len(rezervari) + 1
    rezervare = {
        "id_rezervare": new_id,
        "film_id": film_id,
        "sala_id": sala_id,
        "rand": rand,
        "loc": loc
    }
    rezervari.append(rezervare)
    salveaza_rezervari(rezervari)
    return rezervare


def sterge_rezervare(id_rezervare):
    rezervari = incarca_rezervari()
    rezervari = [r for r in rezervari if r["id_rezervare"] != id_rezervare]
    salveaza_rezervari(rezervari)
