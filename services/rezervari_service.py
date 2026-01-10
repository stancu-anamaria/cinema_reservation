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


def locuri_ocupate(film_id: int, sala_id: int) -> set[tuple[int, int]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT rl.rand, rl.loc
        FROM rezervari_locuri rl
        WHERE rl.film_id = ? AND rl.sala_id = ?;
        """,
        (int(film_id), int(sala_id)),
    )
    rows = cur.fetchall()
    conn.close()
    return {(int(r["rand"]), int(r["loc"])) for r in rows}


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

    preturi = incarca_preturi_bilete()

    # validare tipuri bilete
    for coord in locuri_selectate:
        tip = tip_bilet_per_loc.get(coord)
        if not tip:
            raise ValueError("Lipsește tipul de bilet pentru unul dintre locuri.")
        if tip not in preturi:
            raise ValueError(f"Tip bilet invalid: {tip}")

    # verificare ocupate
    ocupate = locuri_ocupate(int(film_id), int(sala_id))
    for coord in locuri_selectate:
        if coord in ocupate:
            raise ValueError(f"Locul R{coord[0]} L{coord[1]} este deja ocupat.")

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO rezervari (film_id, sala_id, username, nume_client, telefon, ridicate)
            VALUES (?, ?, ?, ?, ?, 0);
            """,
            (int(film_id), int(sala_id), str(username), nume_client.strip(), telefon.strip()),
        )
        id_rez = int(cur.lastrowid)

        for (rand, loc) in locuri_selectate:
            tip = tip_bilet_per_loc[(rand, loc)]
            pret = float(preturi[tip])

            cur.execute(
                """
                INSERT INTO rezervari_locuri
                    (rezervare_id, film_id, sala_id, rand, loc, tip_bilet, pret)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (id_rez, int(film_id), int(sala_id), int(rand), int(loc), tip, pret),
            )

        conn.commit()
        return id_rez

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
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def incarca_rezervari(
    username: str | None,
    is_admin: bool,
    film_id: int | None = None,
    start_time: str | None = None,
) -> list[dict]:
    """
    Returnează rezervări + detalii film/sală/locuri.
    Optional filtre:
      - film_id
      - start_time (ora de start din filme)
    """
    conn = get_connection()
    cur = conn.cursor()

    where = []
    params = []

    if not is_admin:
        where.append("r.username = ?")
        params.append(username)

    if film_id is not None:
        where.append("r.film_id = ?")
        params.append(int(film_id))

    if start_time is not None and str(start_time).strip():
        where.append("COALESCE(f.start_time,'') = ?")
        params.append(str(start_time).strip())

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    cur.execute(
        f"""
        SELECT
            r.id_rezervare, r.film_id, r.sala_id, r.username, r.created_at,
            r.nume_client, r.telefon, r.ridicate,

            f.titlu AS film_titlu, f.start_time AS film_start_time, f.durata AS film_durata,
            s.nume AS sala_nume

        FROM rezervari r
        JOIN filme f ON f.id_film = r.film_id
        JOIN sali s ON s.id_sala = r.sala_id
        {where_sql}
        ORDER BY r.id_rezervare DESC;
        """,
        tuple(params),
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
        locuri_rows = cur.fetchall()

        locuri = [
            {
                "rand": int(l["rand"]),
                "loc": int(l["loc"]),
                "tip_bilet": l["tip_bilet"],
                "pret": float(l["pret"]),
            }
            for l in locuri_rows
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
                "ridicate": bool(int(r["ridicate"] or 0)),

                "film_titlu": r["film_titlu"],
                "film_start_time": r["film_start_time"],
                "film_durata": int(r["film_durata"] or 0),
                "sala_nume": r["sala_nume"],

                "locuri": locuri,
                "total": float(total),
            }
        )

    conn.close()
    return rezultat


def seteaza_bilete_ridicate(id_rezervare: int, ridicate: bool) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE rezervari
        SET ridicate = ?
        WHERE id_rezervare = ?;
        """,
        (1 if ridicate else 0, int(id_rezervare)),
    )
    conn.commit()
    conn.close()
