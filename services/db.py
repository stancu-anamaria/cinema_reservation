import sqlite3
import os

DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "cinema.db")

os.makedirs(DATA_DIR, exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _exista_tabela(cur, nume_tabela: str) -> bool:
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
        (nume_tabela,),
    )
    return cur.fetchone() is not None


def _exista_index(cur, nume_index: str) -> bool:
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name=?;",
        (nume_index,),
    )
    return cur.fetchone() is not None


def _coloane_tabela(cur, nume_tabela: str) -> set[str]:
    cur.execute(f"PRAGMA table_info({nume_tabela});")
    return {row["name"] for row in cur.fetchall()}


def _drop_table_if_exists(cur, nume_tabela: str):
    cur.execute(f"DROP TABLE IF EXISTS {nume_tabela};")


def _asigura_coloane_rezervari(cur):
    """
    Dacă baza există deja, CREATE TABLE IF NOT EXISTS nu adaugă coloane noi.
    Așa că folosim ALTER TABLE ADD COLUMN când lipsește ceva.
    """
    if not _exista_tabela(cur, "rezervari"):
        return

    cols = _coloane_tabela(cur, "rezervari")

    if "nume_client" not in cols:
        cur.execute("ALTER TABLE rezervari ADD COLUMN nume_client TEXT;")
    if "telefon" not in cols:
        cur.execute("ALTER TABLE rezervari ADD COLUMN telefon TEXT;")
    if "created_at" not in cols:
        cur.execute("ALTER TABLE rezervari ADD COLUMN created_at TEXT DEFAULT (datetime('now'));")
    if "username" not in cols:
        # rar, dar ca safety
        cur.execute("ALTER TABLE rezervari ADD COLUMN username TEXT NOT NULL DEFAULT 'unknown';")


def _creeaza_schema(cur):
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

    # filme
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

    # rezervari (header) - schema nouă
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


def _este_schema_veche_rezervari(cur) -> bool:
    """
    Schema veche: rezervari are coloane rand/loc direct în rezervari.
    """
    if not _exista_tabela(cur, "rezervari"):
        return False
    cols = _coloane_tabela(cur, "rezervari")
    return ("rand" in cols) and ("loc" in cols)


def _migrare_soft_din_schema_veche(cur):
    """
    Migrare SAFE (fără drop/rename):
    - dacă există rand/loc în rezervari, copiem acele locuri în rezervari_locuri
    - nu ștergem nimic, nu redenumim nimic
    - folosim INSERT OR IGNORE ca să fie idempotent
    """
    # dacă nu e schema veche, nimic de făcut
    if not _este_schema_veche_rezervari(cur):
        return

    # ne asigurăm că există tabelul nou de detalii
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
            pret          REAL NOT NULL
        );
        """
    )

    # asigurăm unique index (dacă lipsește)
    if not _exista_index(cur, "uq_loc_film_sala"):
        cur.execute(
            """
            CREATE UNIQUE INDEX uq_loc_film_sala
            ON rezervari_locuri (film_id, sala_id, rand, loc);
            """
        )

    # copiem
    cur.execute(
        """
        SELECT id_rezervare, film_id, sala_id, rand, loc
        FROM rezervari
        WHERE rand IS NOT NULL AND loc IS NOT NULL
        ORDER BY id_rezervare;
        """
    )
    vechi = cur.fetchall()

    for r in vechi:
        id_rez = int(r["id_rezervare"])
        film_id = int(r["film_id"])
        sala_id = int(r["sala_id"])
        rand = int(r["rand"])
        loc = int(r["loc"])

        cur.execute(
            """
            INSERT OR IGNORE INTO rezervari_locuri
                (rezervare_id, film_id, sala_id, rand, loc, tip_bilet, pret)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (id_rez, film_id, sala_id, rand, loc, "Adult", 35.0),
        )


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # în migrare lucrăm fără FK ca să fie stabil
    conn.execute("PRAGMA foreign_keys = OFF;")
    conn.commit()

    # 1) creăm schema (tables + index)
    _creeaza_schema(cur)
    conn.commit()

    # 2) dacă baza era veche, facem migrare soft (copiere în rezervari_locuri)
    _migrare_soft_din_schema_veche(cur)
    conn.commit()

    # 3) dacă rezervari exista deja, dar îi lipsesc coloane noi, le adăugăm
    _asigura_coloane_rezervari(cur)
    conn.commit()

    # activăm FK la final
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.close()


init_db()
