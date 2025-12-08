import sqlite3
import os

DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "cinema.db")

os.makedirs(DATA_DIR, exist_ok=True)


def get_connection():
    """
    Creează o conexiune la baza de date SQLite.
    activează foreign_keys pentru ștergeri în lanț.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """
    Creează tabelele dacă nu există deja:
      - sali
      - filme
      - rezervari
    """
    conn = get_connection()
    cur = conn.cursor()

    # tabel săli
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

    # tabel filme
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS filme (
            id_film   INTEGER PRIMARY KEY AUTOINCREMENT,
            titlu     TEXT NOT NULL,
            durata    INTEGER NOT NULL,
            sala_id   INTEGER NOT NULL,
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

    # tabel rezervări (un loc / rezervare, ca în codul tău actual)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS rezervari (
            id_rezervare INTEGER PRIMARY KEY AUTOINCREMENT,
            film_id      INTEGER NOT NULL,
            sala_id      INTEGER NOT NULL,
            rand         INTEGER NOT NULL,
            loc          INTEGER NOT NULL,
            FOREIGN KEY (film_id)
                REFERENCES filme(id_film)
                ON DELETE CASCADE,
            FOREIGN KEY (sala_id)
                REFERENCES sali(id_sala)
                ON DELETE CASCADE
        );
        """
    )

    conn.commit()
    conn.close()


# inițializează baza de date la import
init_db()
