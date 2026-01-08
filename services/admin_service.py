from services.db import get_connection


def _time_to_minutes(hhmm: str) -> int:
    parts = (hhmm or "").strip().split(":")
    if len(parts) != 2:
        raise ValueError("Ora trebuie să fie în format HH:MM (ex: 18:30).")

    try:
        h = int(parts[0])
        m = int(parts[1])
    except ValueError:
        raise ValueError("Ora trebuie să fie în format HH:MM (ex: 18:30).")

    if h < 0 or h > 23 or m < 0 or m > 59:
        raise ValueError("Ora nu este validă. (00:00 - 23:59)")

    return h * 60 + m


def _exista_suprapunere_film(sala_id: int, start_time: str, durata: int) -> bool:
    start_new = _time_to_minutes(start_time)
    end_new = start_new + int(durata)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT start_time, durata
        FROM filme
        WHERE sala_id = ?
          AND start_time IS NOT NULL
          AND TRIM(start_time) <> '';
        """,
        (int(sala_id),),
    )
    rows = cur.fetchall()
    conn.close()

    for r in rows:
        old_start_str = (r["start_time"] or "").strip()
        if not old_start_str:
            continue

        try:
            start_old = _time_to_minutes(old_start_str)
        except Exception:
            continue

        end_old = start_old + int(r["durata"])

        # overlap: new_start < old_end AND old_start < new_end
        if start_new < end_old and start_old < end_new:
            return True

    return False


# -------------------- SĂLI -----------------------

def incarca_sali():
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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sali WHERE id_sala = ?;", (int(id_sala),))
    conn.commit()
    conn.close()


# -------------------- FILME -----------------------

def incarca_filme():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id_film, titlu, durata, sala_id, start_time,
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
            "start_time": row["start_time"],
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
    start_time: str | None = None,
    descriere=None,
    rated=None,
    poster=None,
    actori=None,
    genuri=None,
    tags=None,
):
    durata_int = int(durata)
    sala_id_int = int(sala_id)

    start_clean = (start_time or "").strip()
    if start_clean:
        _ = _time_to_minutes(start_clean)

        if _exista_suprapunere_film(sala_id_int, start_clean, durata_int):
            raise ValueError(
                "În sala aleasă există deja un film care rulează în acel interval. "
                "Alege altă oră sau altă sală."
            )
    else:
        start_clean = None

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO filme (
            titlu, durata, sala_id, start_time,
            descriere, rated, poster,
            actori, genuri, tags
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            titlu,
            durata_int,
            sala_id_int,
            start_clean,
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
        "durata": durata_int,
        "sala_id": sala_id_int,
        "start_time": start_clean,
        "descriere": descriere,
        "rated": rated,
        "poster": poster,
        "actori": actori,
        "genuri": genuri,
        "tags": tags,
    }


def sterge_film(id_film):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM filme WHERE id_film = ?;", (int(id_film),))
    conn.commit()
    conn.close()
