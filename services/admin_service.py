import json

FILME_FILE = "data/filme.json"
SALI_FILE = "data/sali.json"


def incarca_filme():
    try:
        with open(FILME_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def salveaza_filme(lista):
    with open(FILME_FILE, "w") as f:
        json.dump(lista, f, indent=4)


def genereaza_id_film():
    filme = incarca_filme()
    if not filme:
        return 1
    return max(f["id_film"] for f in filme) + 1


def adauga_film(titlu, durata, sala_id):
    filme = incarca_filme()
    new_id = genereaza_id_film()
    film = {
        "id_film": new_id,
        "titlu": titlu,
        "durata": durata,
        "sala_id": sala_id
    }
    filme.append(film)
    salveaza_filme(filme)
    return film
