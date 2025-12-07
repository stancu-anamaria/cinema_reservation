import json
import os

DATA_DIR = "data"
FILME_FILE = os.path.join(DATA_DIR, "filme.json")
SALI_FILE = os.path.join(DATA_DIR, "sali.json")

os.makedirs(DATA_DIR, exist_ok=True)


# -------------------- SĂLI -----------------------

def incarca_sali():
    """Încărcă lista de săli din fișierul JSON."""
    try:
        with open(SALI_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def salveaza_sali(lista):
    """Salvează lista de săli în fișierul JSON."""
    with open(SALI_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)


def genereaza_id_sala():
    """Generează un ID nou de sală (incremental)."""
    sali = incarca_sali()
    if not sali:
        return 1
    return int(sali[-1]["id_sala"]) + 1


def adauga_sala(nume, randuri, locuri_pe_rand):
    """Adaugă o sală nouă în sistem."""
    sali = incarca_sali()
    sala = {
        "id_sala": genereaza_id_sala(),
        "nume": nume,
        "randuri": int(randuri),
        "locuri_pe_rand": int(locuri_pe_rand)
    }
    sali.append(sala)
    salveaza_sali(sali)
    return sala


def sterge_sala(id_sala):
    """
    Șterge o sală + toate filmele din sala respectivă + rezervările asociate.

    - Scoate sala din sali.json
    - Scoate toate filmele cu sala_id = id_sala din filme.json
    - Scoate toate rezervările care au sala_id sau film_id din acele filme
    """
    from services.rezervari_service import incarca_rezervari, salveaza_rezervari

    id_sala = int(id_sala)

    # 1. Scoatem sala
    sali = incarca_sali()
    sali_noi = [s for s in sali if int(s["id_sala"]) != id_sala]
    salveaza_sali(sali_noi)

    # 2. Scoatem filmele din sala respectivă
    filme = incarca_filme()
    filme_noi = []
    filme_ids_sterse = []
    for f in filme:
        if int(f["sala_id"]) == id_sala:
            filme_ids_sterse.append(int(f["id_film"]))
        else:
            filme_noi.append(f)
    salveaza_filme(filme_noi)

    # 3. Scoatem rezervările legate de sala + filmele șterse
    rezervari = incarca_rezervari()
    rezervari_noi = []
    for r in rezervari:
        if int(r["sala_id"]) == id_sala:
            continue
        if int(r["film_id"]) in filme_ids_sterse:
            continue
        rezervari_noi.append(r)
    salveaza_rezervari(rezervari_noi)


# -------------------- FILME -----------------------

def incarca_filme():
    """Încărcă lista de filme din fișierul JSON."""
    try:
        with open(FILME_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def salveaza_filme(lista):
    """Salvează lista de filme în fișierul JSON."""
    with open(FILME_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)


def genereaza_id_film():
    """Generează un ID nou de film (incremental)."""
    filme = incarca_filme()
    if not filme:
        return 1
    return int(filme[-1]["id_film"]) + 1


def adauga_film(
    titlu,
    durata,
    sala_id,
    descriere=None,
    rated=None,
    poster=None,
    actori=None,
    genuri=None,
    tags=None,
):
    """
    Adaugă film nou (din API sau manual).

    câmpuri:
      - titlu: titlul filmului (în română, pentru clienți)
      - durata: minute
      - sala_id: ID-ul sălii în care rulează
      - descriere: descriere în română
      - rated: clasificare vârstă (în română)
      - poster: URL sau path local către poză
      - actori: distribuție (string)
      - genuri: genuri (string, în română)
      - tags: etichete de tip „Tulburător, Creativ”
    """
    filme = incarca_filme()
    new_id = genereaza_id_film()

    film = {
        "id_film": new_id,
        "titlu": titlu,
        "durata": int(durata),
        "sala_id": int(sala_id),
        "descriere": descriere,
        "rated": rated,
        "poster": poster,
        "actori": actori,
        "genuri": genuri,
        "tags": tags,
    }
    filme.append(film)
    salveaza_filme(filme)
    return film


def sterge_film(id_film):
    """
    Șterge un film după id_film + toate rezervările lui.
    """
    from services.rezervari_service import incarca_rezervari, salveaza_rezervari

    id_film = int(id_film)

    # 1. scoatem filmul din filme.json
    filme = incarca_filme()
    filme_noi = [f for f in filme if int(f["id_film"]) != id_film]
    salveaza_filme(filme_noi)

    # 2. scoatem rezervările asociate din rezervari.json
    rezervari = incarca_rezervari()
    rezervari_noi = [r for r in rezervari if int(r["film_id"]) != id_film]
    salveaza_rezervari(rezervari_noi)
