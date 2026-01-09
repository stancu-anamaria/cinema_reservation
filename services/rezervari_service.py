# path: services/rezervari_service.py
from __future__ import annotations

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


def curata_orfani_rezervari_locuri() -> int:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM rezervari_locuri
        WHERE rezervare_id NOT IN (SELECT id_rezervare FROM rezervari);
        """
    )
    sters = cur.rowcount

    conn.commit()
    conn.close()
    return int(sters)


def locuri_ocupate(film_id: int, sala_id: int) -> set[tuple[int, int]]:
    """
    IMPORTANT: doar locurile care aparțin unor rezervări existente (JOIN cu rezervari).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT rl.rand, rl.loc
        FROM rezervari_locuri rl
        JOIN rezervari r ON r.id_rezervare = rl.rezervare_id
        WHERE rl.film_id = ? AND rl.sala_id = ?;
        """,
        (int(film_id), int(sala_id)),
    )
    rows = cur.fetchall()
    conn.close()

    return {(int(r["rand"]), int(r["loc"])) for r in rows}


def incarca_rezervari(username: str | None, is_admin: bool) -> list[dict]:
    """
    Returnează rezervări + locuri + total + (film title, sala nume, start_time, durata)
    """
    conn = get_connection()
    cur = conn.cursor()

    if is_admin:
        cur.execute(
            """
            SELECT r.id_rezervare, r.film_id, r.sala_id, r.username, r.created_at, r.nume_client, r.telefon,
                   f.titlu AS film_titlu, f.start_time AS film_start_time, f.durata AS film_durata,
                   s.nume AS sala_nume
            FROM rezervari r
            LEFT JOIN filme f ON f.id_film = r.film_id
            LEFT JOIN sali  s ON s.id_sala = r.sala_id
            ORDER BY r.id_rezervare DESC;
            """
        )
        rezervari_rows = cur.fetchall()
    else:
        cur.execute(
            """
            SELECT r.id_rezervare, r.film_id, r.sala_id, r.username, r.created_at, r.nume_client, r.telefon,
                   f.titlu AS film_titlu, f.start_time AS film_start_time, f.durata AS film_durata,
                   s.nume AS sala_nume
            FROM rezervari r
            LEFT JOIN filme f ON f.id_film = r.film_id
            LEFT JOIN sali  s ON s.id_sala = r.sala_id
            WHERE r.username = ?
            ORDER BY r.id_rezervare DESC;
            """,
            (username,),
        )
        rezervari_rows = cur.fetchall()

    rezultat: list[dict] = []
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
                "nume_client": r["nume_client"],
                "telefon": r["telefon"],
                "locuri": locuri,
                "total": float(total),
                # extra pentru UI (fără id-uri)
                "film_titlu": r["film_titlu"],
                "film_start_time": r["film_start_time"],
                "film_durata": r["film_durata"],
                "sala_nume": r["sala_nume"],
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
    nume_client: str,
    telefon: str,
) -> int:
    if not username or not str(username).strip():
        raise ValueError("Trebuie să fii autentificat ca să faci o rezervare.")

    if not (nume_client or "").strip():
        raise ValueError("Te rog să introduci numele pentru rezervare.")
    if not (telefon or "").strip():
        raise ValueError("Te rog să introduci numărul de telefon.")
    if not locuri_selectate:
        raise ValueError("Nu ai selectat niciun loc.")

    sala = _incarca_sala(int(sala_id))
    if not sala:
        raise ValueError("Sala nu există.")

    randuri = int(sala["randuri"])
    locuri_pe_rand = int(sala["locuri_pe_rand"])
    preturi = incarca_preturi_bilete()

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
        cur.execute(
            """
            INSERT INTO rezervari (film_id, sala_id, username, nume_client, telefon)
            VALUES (?, ?, ?, ?, ?);
            """,
            (int(film_id), int(sala_id), str(username), nume_client.strip(), telefon.strip()),
        )
        id_rezervare = int(cur.lastrowid)

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
        return id_rezervare

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def sterge_rezervare(id_rezervare: int) -> None:
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM rezervari_locuri WHERE rezervare_id = ?;", (int(id_rezervare),))
        cur.execute("DELETE FROM rezervari WHERE id_rezervare = ?;", (int(id_rezervare),))

        cur.execute(
            """
            DELETE FROM rezervari_locuri
            WHERE rezervare_id NOT IN (SELECT id_rezervare FROM rezervari);
            """
        )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
