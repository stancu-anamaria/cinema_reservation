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


def _coloane_tabela(cur, nume_tabela: str) -> set[str]:
    cur.execute(f"PRAGMA table_info({nume_tabela});")
    return {row["name"] for row in cur.fetchall()}


def _drop_table_if_exists(cur, nume_tabela: str):
    cur.execute(f"DROP TABLE IF EXISTS {nume_tabela};")


def _creeaza_schema_noua(cur):
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

    # rezervari (header)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS rezervari (
            id_rezervare INTEGER PRIMARY KEY AUTOINCREMENT,
            film_id      INTEGER NOT NULL,
            sala_id      INTEGER NOT NULL,
            username     TEXT NOT NULL,
            created_at   TEXT DEFAULT (datetime('now')),
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
                ON DELETE CASCADE,

            UNIQUE (film_id, sala_id, rand, loc)
        );
        """
    )


def _este_schema_veche_rezervari(cur) -> bool:
    """
    Schema veche: rezervari are coloane rand/loc.
    """
    if not _exista_tabela(cur, "rezervari"):
        return False
    cols = _coloane_tabela(cur, "rezervari")
    return ("rand" in cols) and ("loc" in cols)


def _curata_leftovers_migrare(cur):
    """
    Dacă a crăpat o migrare înainte, pot rămâne tabele *_new.
    Le ștergem ca să nu ne încurce.
    """
    _drop_table_if_exists(cur, "rezervari_new")
    _drop_table_if_exists(cur, "rezervari_locuri_new")


def _migrare_din_schema_veche(cur):
    """
    Migrează:
      rezervari vechi -> rezervari (header) + rezervari_locuri (detalii)

    IMPORTANT:
    - dacă rezervari_locuri există deja (din încercări anterioare), NU mai migrăm iar,
      ca să evităm duplicate/conflicte.
    """
    # dacă deja există tabelul nou cu detalii, considerăm că migrarea a fost făcută/începută
    if _exista_tabela(cur, "rezervari_locuri"):
        # dacă totuși rezervari e încă vechi, cea mai safe e să OPRIM și să cerem reset.
        # Dar putem fi pragmatic: doar nu mai facem rename-uri care crapă.
        return

    # curățăm leftovers
    _curata_leftovers_migrare(cur)

    # tabele noi temporare
    cur.execute(
        """
        CREATE TABLE rezervari_new (
            id_rezervare INTEGER PRIMARY KEY AUTOINCREMENT,
            film_id      INTEGER NOT NULL,
            sala_id      INTEGER NOT NULL,
            username     TEXT NOT NULL,
            created_at   TEXT DEFAULT (datetime('now'))
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE rezervari_locuri_new (
            id_linie      INTEGER PRIMARY KEY AUTOINCREMENT,
            rezervare_id  INTEGER NOT NULL,

            film_id       INTEGER NOT NULL,
            sala_id       INTEGER NOT NULL,
            rand          INTEGER NOT NULL,
            loc           INTEGER NOT NULL,

            tip_bilet     TEXT NOT NULL,
            pret          REAL NOT NULL,

            UNIQUE (film_id, sala_id, rand, loc)
        );
        """
    )

    # citim rezervări vechi
    cur.execute(
        """
        SELECT id_rezervare, film_id, sala_id, rand, loc
        FROM rezervari
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

        # header (păstrăm id)
        cur.execute(
            """
            INSERT INTO rezervari_new (id_rezervare, film_id, sala_id, username, created_at)
            VALUES (?, ?, ?, ?, datetime('now'));
            """,
            (id_rez, film_id, sala_id, "migrat"),
        )

        # detaliu (1 loc)
        cur.execute(
            """
            INSERT OR IGNORE INTO rezervari_locuri_new
                (rezervare_id, film_id, sala_id, rand, loc, tip_bilet, pret)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (id_rez, film_id, sala_id, rand, loc, "Adult", 35.0),
        )

    # DROP vechi, rename noi
    cur.execute("DROP TABLE rezervari;")
    cur.execute("ALTER TABLE rezervari_new RENAME TO rezervari;")
    cur.execute("ALTER TABLE rezervari_locuri_new RENAME TO rezervari_locuri;")


def init_db():
    # folosim conexiune separată (fără foreign keys) ca să fie migrarea safe
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # dezactivează FK temporar
    conn.execute("PRAGMA foreign_keys = OFF;")
    conn.commit()

    # asigură sali/filme măcar
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
            tags      TEXT
        );
        """
    )
    conn.commit()

    # migrare doar dacă rezervari e vechi și NU există deja rezervari_locuri
    if _este_schema_veche_rezervari(cur) and not _exista_tabela(cur, "rezervari_locuri"):
        _migrare_din_schema_veche(cur)
        conn.commit()

    # creează schema nouă (safe)
    _creeaza_schema_noua(cur)
    conn.commit()

    # curățăm leftovers dacă au rămas
    _curata_leftovers_migrare(cur)
    conn.commit()

    # reactivează FK
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.close()


init_db()