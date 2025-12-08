from services.db import get_connection


def incarca_rezervari():
    """Returnează toate rezervările ca listă de dict-uri."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id_rezervare, film_id, sala_id, rand, loc
        FROM rezervari
        ORDER BY id_rezervare;
        """
    )
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id_rezervare": row["id_rezervare"],
            "film_id": row["film_id"],
            "sala_id": row["sala_id"],
            "rand": row["rand"],
            "loc": row["loc"],
        }
        for row in rows
    ]


def creeaza_rezervare(film_id, sala_id, rand, loc):
    """
    Creează o rezervare (un singur loc, ca în implementarea ta actuală).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO rezervari (film_id, sala_id, rand, loc)
        VALUES (?, ?, ?, ?);
        """,
        (int(film_id), int(sala_id), int(rand), int(loc)),
    )
    conn.commit()
    id_rezervare = cur.lastrowid
    conn.close()

    return {
        "id_rezervare": id_rezervare,
        "film_id": int(film_id),
        "sala_id": int(sala_id),
        "rand": int(rand),
        "loc": int(loc),
    }


def sterge_rezervare(id_rezervare):
    """Șterge o rezervare după ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM rezervari WHERE id_rezervare = ?;",
        (int(id_rezervare),),
    )
    conn.commit()
    conn.close()
