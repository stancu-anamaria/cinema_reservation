from __future__ import annotations

from services.db import get_connection


class RezervariRepository:
    def incarca_sala(self, sala_id: int) -> dict | None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id_sala, nume, randuri, locuri_pe_rand FROM sali WHERE id_sala=?;",
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

    def locuri_ocupate(self, film_id: int, sala_id: int) -> set[tuple[int, int]]:
        """
        JOIN cu rezervari => nu mai rămân “roșii” locuri din cauza orphan rows.
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

    def incarca_rezervari_admin(self) -> list[dict]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id_rezervare, film_id, sala_id, username, created_at, nume_client, telefon
            FROM rezervari
            ORDER BY id_rezervare DESC;
            """
        )
        rez = cur.fetchall()

        rezultat = []
        for r in rez:
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
                {"rand": int(l["rand"]), "loc": int(l["loc"]), "tip_bilet": l["tip_bilet"], "pret": float(l["pret"])}
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
                }
            )

        conn.close()
        return rezultat

    def creeaza_header(self, film_id: int, sala_id: int, username: str, nume_client: str, telefon: str) -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO rezervari (film_id, sala_id, username, nume_client, telefon)
            VALUES (?, ?, ?, ?, ?);
            """,
            (int(film_id), int(sala_id), username, nume_client, telefon),
        )
        conn.commit()
        rez_id = int(cur.lastrowid)
        conn.close()
        return rez_id

    def adauga_loc(self, rezervare_id: int, film_id: int, sala_id: int, rand: int, loc: int, tip: str, pret: float) -> None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO rezervari_locuri (rezervare_id, film_id, sala_id, rand, loc, tip_bilet, pret)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (int(rezervare_id), int(film_id), int(sala_id), int(rand), int(loc), tip, float(pret)),
        )
        conn.commit()
        conn.close()

    def sterge_rezervare(self, id_rezervare: int) -> None:
        """
        Ștergere explicită => locurile se eliberează sigur.
        """
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM rezervari_locuri WHERE rezervare_id=?;", (int(id_rezervare),))
        cur.execute("DELETE FROM rezervari WHERE id_rezervare=?;", (int(id_rezervare),))
        cur.execute("DELETE FROM rezervari_locuri WHERE rezervare_id NOT IN (SELECT id_rezervare FROM rezervari);")
        conn.commit()
        conn.close()
