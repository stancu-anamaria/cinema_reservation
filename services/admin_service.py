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


def adauga_film(id_film, titlu, durata, sala_id):
    filme = incarca_filme()
    film = {
        "id_film": id_film,
        "titlu": titlu,
        "durata": durata,
        "sala_id": sala_id
    }
    filme.append(film)
    salveaza_filme(filme)


def incarca_sali():
    try:
        with open(SALI_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def salveaza_sali(lista):
    with open(SALI_FILE, "w") as f:
        json.dump(lista, f, indent=4)


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
