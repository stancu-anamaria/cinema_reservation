from __future__ import annotations

from repositories.rezervari_repository import RezervariRepository


PRETURI_BILETE = {
    "Adult": 35.0,
    "Copil": 20.0,
    "Student": 25.0,
    "Pensionar": 22.0,
}


class RezervariService:
    def __init__(self, repo: RezervariRepository | None = None):
        self.repo = repo or RezervariRepository()

    def incarca_preturi_bilete(self):
        return dict(PRETURI_BILETE)

    def locuri_ocupate(self, film_id: int, sala_id: int) -> set[tuple[int, int]]:
        return self.repo.locuri_ocupate(film_id, sala_id)

    def incarca_rezervari_admin(self) -> list[dict]:
        return self.repo.incarca_rezervari_admin()

    def creeaza_rezervare_multi(
        self,
        film_id: int,
        sala_id: int,
        locuri_selectate: list[tuple[int, int]],
        tip_bilet_per_loc: dict[tuple[int, int], str],
        username: str,
        nume_client: str,
        telefon: str,
    ) -> int:
        if not username or not username.strip():
            raise ValueError("Trebuie să fii autentificat ca să faci o rezervare.")
        if username.strip().lower() == "vizitator":
            raise ValueError("Pentru rezervare, autentifică-te cu un cont (nu ca vizitator).")

        if not (nume_client or "").strip():
            raise ValueError("Te rog să introduci numele pentru rezervare.")
        if not (telefon or "").strip():
            raise ValueError("Te rog să introduci numărul de telefon.")
        if not locuri_selectate:
            raise ValueError("Nu ai selectat niciun loc.")

        sala = self.repo.incarca_sala(int(sala_id))
        if not sala:
            raise ValueError("Sala nu există.")

        randuri = int(sala["randuri"])
        locuri_pe_rand = int(sala["locuri_pe_rand"])
        preturi = self.incarca_preturi_bilete()

        # validare + tip
        for (r, l) in locuri_selectate:
            if int(r) < 1 or int(r) > randuri:
                raise ValueError(f"Rând invalid: {r}")
            if int(l) < 1 or int(l) > locuri_pe_rand:
                raise ValueError(f"Loc invalid: {l}")
            tip = tip_bilet_per_loc.get((r, l))
            if not tip or tip not in preturi:
                raise ValueError("Tip bilet invalid / lipsă pentru unul dintre locuri.")

        ocupate = self.locuri_ocupate(int(film_id), int(sala_id))
        for coord in locuri_selectate:
            if coord in ocupate:
                raise ValueError(f"Locul R{coord[0]} L{coord[1]} este deja ocupat.")

        rez_id = self.repo.creeaza_header(
            film_id=int(film_id),
            sala_id=int(sala_id),
            username=username.strip(),
            nume_client=nume_client.strip(),
            telefon=telefon.strip(),
        )

        for (r, l) in locuri_selectate:
            tip = tip_bilet_per_loc[(r, l)]
            pret = float(preturi[tip])
            self.repo.adauga_loc(rez_id, int(film_id), int(sala_id), int(r), int(l), tip, pret)

        return rez_id

    def sterge_rezervare(self, id_rezervare: int) -> None:
        self.repo.sterge_rezervare(id_rezervare)


# --------- wrappers (pentru UI existent) ---------
_rez = RezervariService()

def incarca_preturi_bilete():
    return _rez.incarca_preturi_bilete()

def locuri_ocupate(film_id: int, sala_id: int):
    return _rez.locuri_ocupate(film_id, sala_id)

def creeaza_rezervare_multi(**kwargs):
    return _rez.creeaza_rezervare_multi(**kwargs)

def sterge_rezervare(id_rezervare: int):
    _rez.sterge_rezervare(id_rezervare)

def incarca_rezervari(username: str | None, is_admin: bool):
    # tu vrei doar admin => păstrăm doar admin
    if not is_admin:
        return []
    return _rez.incarca_rezervari_admin()
