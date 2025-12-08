from services.db import get_connection


# -------------------- SĂLI -----------------------


def incarca_sali():
    """Returnează o listă de săli sub formă de dict-uri."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id_sala, nume, randuri, locuri_pe_rand FROM sali ORDER BY id_sala;")
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id_sala": row["id_sala"],
            "nume": row["nume"],
            "randuri": row["randuri"],
            "locuri_pe_rand": row["locuri_pe_rand"],
        }
        for row in rows
    ]


def adauga_sala(nume, randuri, locuri_pe_rand):
    """Adaugă o sală nouă și o întoarce ca dict."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO sali (nume, randuri, locuri_pe_rand)
        VALUES (?, ?, ?);
        """,
        (nume, int(randuri), int(locuri_pe_rand)),
    )
    conn.commit()
    sala_id = cur.lastrowid
    conn.close()

    return {
        "id_sala": sala_id,
        "nume": nume,
        "randuri": int(randuri),
        "locuri_pe_rand": int(locuri_pe_rand),
    }


def sterge_sala(id_sala):
    """
    Șterge o sală. Datorită foreign_keys ON DELETE CASCADE:
      - se șterg automat și filmele din sală
      - se șterg automat și rezervările din acele filme/sală
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sali WHERE id_sala = ?;", (int(id_sala),))
    conn.commit()
    conn.close()


# -------------------- FILME -----------------------


def incarca_filme():
    """Returnează lista de filme ca dict-uri."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id_film, titlu, durata, sala_id,
               descriere, rated, poster, actori, genuri, tags
        FROM filme
        ORDER BY id_film;
        """
    )
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id_film": row["id_film"],
            "titlu": row["titlu"],
            "durata": row["durata"],
            "sala_id": row["sala_id"],
            "descriere": row["descriere"],
            "rated": row["rated"],
            "poster": row["poster"],
            "actori": row["actori"],
            "genuri": row["genuri"],
            "tags": row["tags"],
        }
        for row in rows
    ]


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
    Adaugă film nou (manual sau bazat pe API) și-l întoarce ca dict.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO filme (
            titlu, durata, sala_id,
            descriere, rated, poster,
            actori, genuri, tags
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            titlu,
            int(durata),
            int(sala_id),
            descriere,
            rated,
            poster,
            actori,
            genuri,
            tags,
        ),
    )
    conn.commit()
    id_film = cur.lastrowid
    conn.close()

    return {
        "id_film": id_film,
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


def sterge_film(id_film):
    """
    Șterge un film. Datorită ON DELETE CASCADE:
      - se șterg automat rezervările legate de acest film.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM filme WHERE id_film = ?;", (int(id_film),))
    conn.commit()
    conn.close()
