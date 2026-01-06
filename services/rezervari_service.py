from services.db import get_connection

PRETURI_BILETE = {
    "Adult": 35.0,
    "Copil": 20.0,
    "Student": 25.0,
    "Pensionar": 22.0,
}


def incarca_preturi_bilete():
    return dict(PRETURI_BILETE)


def _incarca_sala(sala_id: int) -> dict | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id_sala, nume, randuri, locuri_pe_rand
        FROM sali
        WHERE id_sala = ?;
        """,
        (int(sala_id),),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id_sala": int(row["id_sala"]),
        "nume": row["nume"],
        "randuri": int(row["randuri"]),
        "locuri_pe_rand": int(row["locuri_pe_rand"]),
    }


def locuri_ocupate(film_id: int, sala_id: int) -> set[tuple[int, int]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT rand, loc
        FROM rezervari_locuri
        WHERE film_id = ? AND sala_id = ?;
        """,
        (int(film_id), int(sala_id)),
    )
    rows = cur.fetchall()
    conn.close()

    return {(int(r["rand"]), int(r["loc"])) for r in rows}


def incarca_rezervari(username: str | None, is_admin: bool) -> list[dict]:
    """
    - admin vede toate rezervările
    - user vede doar rezervările lui
    """
    conn = get_connection()
    cur = conn.cursor()

    if is_admin:
        cur.execute(
            """
            SELECT id_rezervare, film_id, sala_id, username, created_at
            FROM rezervari
            ORDER BY id_rezervare DESC;
            """
        )
        rezervari_rows = cur.fetchall()
    else:
        cur.execute(
            """
            SELECT id_rezervare, film_id, sala_id, username, created_at
            FROM rezervari
            WHERE username = ?
            ORDER BY id_rezervare DESC;
            """,
            (username,),
        )
        rezervari_rows = cur.fetchall()

    rezultat = []
    for r in rezervari_rows:
        cur.execute(
            """
            SELECT rand, loc, tip_bilet, pret
            FROM rezervari_locuri
            WHERE rezervare_id = ?
            ORDER BY rand, loc;
            """,
            (int(r["id_rezervare"]),),
        )

        locuri = [
            {
                "rand": int(l["rand"]),
                "loc": int(l["loc"]),
                "tip_bilet": l["tip_bilet"],
                "pret": float(l["pret"]),
            }
            for l in cur.fetchall()
        ]

        total = sum(l["pret"] for l in locuri)

        rezultat.append(
            {
                "id_rezervare": int(r["id_rezervare"]),
                "film_id": int(r["film_id"]),
                "sala_id": int(r["sala_id"]),
                "username": r["username"],
                "created_at": r["created_at"],
                "locuri": locuri,
                "total": float(total),
            }
        )

    conn.close()
    return rezultat


def creeaza_rezervare_multi(
    film_id: int,
    sala_id: int,
    locuri_selectate: list[tuple[int, int]],
    tip_bilet_per_loc: dict[tuple[int, int], str],
    username: str,
):
    if not username or not str(username).strip():
        raise ValueError("Trebuie să fii autentificat ca să faci o rezervare.")

    if not locuri_selectate:
        raise ValueError("Nu ai selectat niciun loc.")

    sala = _incarca_sala(int(sala_id))
    if not sala:
        raise ValueError("Sala nu există.")

    randuri = int(sala["randuri"])
    locuri_pe_rand = int(sala["locuri_pe_rand"])
    preturi = incarca_preturi_bilete()

    # validare coordonate + tip bilet
    for (rand, loc) in locuri_selectate:
        if int(rand) < 1 or int(rand) > randuri:
            raise ValueError(f"Rând invalid: {rand}")
        if int(loc) < 1 or int(loc) > locuri_pe_rand:
            raise ValueError(f"Loc invalid: {loc}")

        tip = tip_bilet_per_loc.get((rand, loc))
        if not tip:
            raise ValueError("Lipsește tipul de bilet pentru unul dintre locuri.")
        if tip not in preturi:
            raise ValueError(f"Tip bilet invalid: {tip}")

    ocupate = locuri_ocupate(int(film_id), int(sala_id))
    for coord in locuri_selectate:
        if coord in ocupate:
            raise ValueError(f"Locul R{coord[0]} L{coord[1]} este deja ocupat.")

    conn = get_connection()
    cur = conn.cursor()

    try:
        # header
        cur.execute(
            """
            INSERT INTO rezervari (film_id, sala_id, username)
            VALUES (?, ?, ?);
            """,
            (int(film_id), int(sala_id), str(username)),
        )
        conn.commit()
        id_rezervare = int(cur.lastrowid)

        # detalii
        for (rand, loc) in locuri_selectate:
            tip = tip_bilet_per_loc[(rand, loc)]
            pret = float(preturi[tip])

            cur.execute(
                """
                INSERT INTO rezervari_locuri
                    (rezervare_id, film_id, sala_id, rand, loc, tip_bilet, pret)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (id_rezervare, int(film_id), int(sala_id), int(rand), int(loc), tip, pret),
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return id_rezervare


def sterge_rezervare(id_rezervare: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM rezervari WHERE id_rezervare = ?;", (int(id_rezervare),))
    conn.commit()
    conn.close()
