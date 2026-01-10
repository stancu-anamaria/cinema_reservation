# path: services/db.py
from __future__ import annotations

import os
import sqlite3

DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "cinema.db")

os.makedirs(DATA_DIR, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    # timeout mai mare => reduce "database is locked"
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    # setări recomandate pentru concurență mai bună
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn


def _exista_tabela(cur: sqlite3.Cursor, nume_tabela: str) -> bool:
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
        (nume_tabela,),
    )
    return cur.fetchone() is not None


def _exista_index(cur: sqlite3.Cursor, nume_index: str) -> bool:
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name=?;",
        (nume_index,),
    )
    return cur.fetchone() is not None


def _coloane_tabela(cur: sqlite3.Cursor, nume_tabela: str) -> set[str]:
    cur.execute(f"PRAGMA table_info({nume_tabela});")
    return {row["name"] for row in cur.fetchall()}


def _asigura_coloane_filme(cur: sqlite3.Cursor) -> None:
    """
    Dacă baza există deja, CREATE TABLE IF NOT EXISTS nu adaugă coloane.
    Așa că facem ALTER TABLE ADD COLUMN când lipsește start_time.
    """
    if not _exista_tabela(cur, "filme"):
        return

    cols = _coloane_tabela(cur, "filme")
    if "start_time" not in cols:
        cur.execute("ALTER TABLE filme ADD COLUMN start_time TEXT;")


def _asigura_coloane_rezervari(cur: sqlite3.Cursor) -> None:
    if not _exista_tabela(cur, "rezervari"):
        return

    cols = _coloane_tabela(cur, "rezervari")

    if "username" not in cols:
        cur.execute("ALTER TABLE rezervari ADD COLUMN username TEXT NOT NULL DEFAULT 'unknown';")
    if "created_at" not in cols:
        cur.execute("ALTER TABLE rezervari ADD COLUMN created_at TEXT DEFAULT (datetime('now'));")
    if "nume_client" not in cols:
        cur.execute("ALTER TABLE rezervari ADD COLUMN nume_client TEXT;")
    if "telefon" not in cols:
        cur.execute("ALTER TABLE rezervari ADD COLUMN telefon TEXT;")

    # ✅ NOU: bilete ridicate (0/1)
    if "ridicate" not in cols:
        cur.execute("ALTER TABLE rezervari ADD COLUMN ridicate INTEGER NOT NULL DEFAULT 0;")


def _creeaza_schema(cur: sqlite3.Cursor) -> None:
    # sali
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sali (
            id_sala        INTEGER PRIMARY KEY AUTOINCREMENT,
            nume           TEXT NOT NULL,
            randuri        INTEGER NOT NULL,
            locuri_pe_rand INTEGER NOT NULL
        );
        """
    )

    # filme (cu start_time)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS filme (
            id_film   INTEGER PRIMARY KEY AUTOINCREMENT,
            titlu     TEXT NOT NULL,
            durata    INTEGER NOT NULL,
            sala_id   INTEGER NOT NULL,
            start_time TEXT,

            descriere TEXT,
            rated     TEXT,
            poster    TEXT,
            actori    TEXT,
            genuri    TEXT,
            tags      TEXT,

            FOREIGN KEY (sala_id)
                REFERENCES sali(id_sala)
                ON DELETE CASCADE
        );
        """
    )

    # rezervari (header)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS rezervari (
            id_rezervare INTEGER PRIMARY KEY AUTOINCREMENT,
            film_id      INTEGER NOT NULL,
            sala_id      INTEGER NOT NULL,
            username     TEXT NOT NULL,
            created_at   TEXT DEFAULT (datetime('now')),
            nume_client  TEXT,
            telefon      TEXT,
            ridicate     INTEGER NOT NULL DEFAULT 0,

            FOREIGN KEY (film_id)
                REFERENCES filme(id_film)
                ON DELETE CASCADE,
            FOREIGN KEY (sala_id)
                REFERENCES sali(id_sala)
                ON DELETE CASCADE
        );
        """
    )

    # rezervari_locuri (detalii)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS rezervari_locuri (
            id_linie      INTEGER PRIMARY KEY AUTOINCREMENT,
            rezervare_id  INTEGER NOT NULL,

            film_id       INTEGER NOT NULL,
            sala_id       INTEGER NOT NULL,
            rand          INTEGER NOT NULL,
            loc           INTEGER NOT NULL,

            tip_bilet     TEXT NOT NULL,
            pret          REAL NOT NULL,

            FOREIGN KEY (rezervare_id)
                REFERENCES rezervari(id_rezervare)
                ON DELETE CASCADE,

            FOREIGN KEY (film_id)
                REFERENCES filme(id_film)
                ON DELETE CASCADE,

            FOREIGN KEY (sala_id)
                REFERENCES sali(id_sala)
                ON DELETE CASCADE
        );
        """
    )

    # Unique: un loc nu poate fi rezervat de 2 ori la același film/sală
    if not _exista_index(cur, "uq_loc_film_sala"):
        cur.execute(
            """
            CREATE UNIQUE INDEX uq_loc_film_sala
            ON rezervari_locuri (film_id, sala_id, rand, loc);
            """
        )


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    # 1) schema de bază
    _creeaza_schema(cur)
    conn.commit()

    # 2) migrare soft: adăugăm coloane lipsă
    _asigura_coloane_filme(cur)
    _asigura_coloane_rezervari(cur)
    conn.commit()

    conn.close()


init_db()
