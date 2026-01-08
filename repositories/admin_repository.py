from __future__ import annotations

from services.db import get_connection


class AdminRepository:
    # -------- SALI --------
    def incarca_sali(self) -> list[dict]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_sala, nume, randuri, locuri_pe_rand FROM sali ORDER BY id_sala;")
        rows = cur.fetchall()
        conn.close()
        return [
            {
                "id_sala": int(r["id_sala"]),
                "nume": r["nume"],
                "randuri": int(r["randuri"]),
                "locuri_pe_rand": int(r["locuri_pe_rand"]),
            }
            for r in rows
        ]

    def adauga_sala(self, nume: str, randuri: int, locuri_pe_rand: int) -> dict:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO sali (nume, randuri, locuri_pe_rand) VALUES (?, ?, ?);",
            (nume, int(randuri), int(locuri_pe_rand)),
        )
        conn.commit()
        sala_id = int(cur.lastrowid)
        conn.close()
        return {
            "id_sala": sala_id,
            "nume": nume,
            "randuri": int(randuri),
            "locuri_pe_rand": int(locuri_pe_rand),
        }

    def sterge_sala(self, id_sala: int) -> None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM sali WHERE id_sala = ?;", (int(id_sala),))
        conn.commit()
        conn.close()

    # -------- FILME --------
    def incarca_filme(self) -> list[dict]:
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
                "id_film": int(r["id_film"]),
                "titlu": r["titlu"],
                "durata": int(r["durata"]),
                "sala_id": int(r["sala_id"]),
                "descriere": r["descriere"],
                "rated": r["rated"],
                "poster": r["poster"],
                "actori": r["actori"],
                "genuri": r["genuri"],
                "tags": r["tags"],
            }
            for r in rows
        ]

    def adauga_film(
        self,
        titlu: str,
        durata: int,
        sala_id: int,
        descriere=None,
        rated=None,
        poster=None,
        actori=None,
        genuri=None,
        tags=None,
    ) -> dict:
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
            (titlu, int(durata), int(sala_id), descriere, rated, poster, actori, genuri, tags),
        )
        conn.commit()
        film_id = int(cur.lastrowid)
        conn.close()

        return {
            "id_film": film_id,
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

    def sterge_film(self, id_film: int) -> None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM filme WHERE id_film = ?;", (int(id_film),))
        conn.commit()
        conn.close()
