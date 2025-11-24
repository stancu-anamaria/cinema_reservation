import json
import os

DATA_DIR = "data"
FILME_FILE = os.path.join(DATA_DIR, "filme.json")
SALI_FILE = os.path.join(DATA_DIR, "sali.json")


# -------------------- SALI -----------------------

def incarca_sali():
    try:
        with open(SALI_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def salveaza_sali(lista):
    with open(SALI_FILE, "w") as f:
        json.dump(lista, f, indent=4)


def genereaza_id_sala():
    sali = incarca_sali()
    if not sali:
        return 1
    return sali[-1]["id_sala"] + 1


def adauga_sala(id_sala, nume, randuri, locuri_pe_rand):
    sali = incarca_sali()
    sala = {
        "id_sala": id_sala,
        "nume": nume,
        "randuri": randuri,
        "locuri_pe_rand": locuri_pe_rand
    }
    sali.append(sala)
    salveaza_sali(sali)
    return sala


# -------------------- FILME -----------------------

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
    return filme[-1]["id_film"] + 1


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
