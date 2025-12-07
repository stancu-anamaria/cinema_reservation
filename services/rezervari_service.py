import json
import os

DATA_DIR = "data"
DATAFILE = os.path.join(DATA_DIR, "rezervari.json")

# asigură-te că folderul data există
os.makedirs(DATA_DIR, exist_ok=True)


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


def sterge_rezervari_pentru_film(film_id):
    """Șterge toate rezervările asociate unui film."""
    rezervari = incarca_rezervari()
    rezervari = [r for r in rezervari if r["film_id"] != film_id]
    salveaza_rezervari(rezervari)


def sterge_rezervari_pentru_sala(sala_id):
    """Șterge toate rezervările asociate unei săli."""
    rezervari = incarca_rezervari()
    rezervari = [r for r in rezervari if r["sala_id"] != sala_id]
    salveaza_rezervari(rezervari)


def sterge_rezervari_pentru_filme_din_sala(lista_id_filme):
    """Șterge toate rezervările pentru o listă de filme (de ex. când ștergi o sală)."""
    rezervari = incarca_rezervari()
    rezervari = [r for r in rezervari if r["film_id"] not in lista_id_filme]
    salveaza_rezervari(rezervari)
