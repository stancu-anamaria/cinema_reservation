from __future__ import annotations

import requests
from services.admin_service import adauga_film


API_KEY = "68a685a0"
BASE_URL = "https://www.omdbapi.com/"


def cauta_film_in_api(titlu: str):
    params = {"apikey": API_KEY, "t": titlu}
    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        return None

    data = response.json()
    if data.get("Response") == "False":
        return None

    return data


def genereaza_etichete_din_genuri(genres_str: str | None) -> str | None:
    if not genres_str:
        return None

    text = genres_str.lower()
    tags = []

    if "drama" in text:
        tags.append("Tulburător")
    if "sci-fi" in text or "sci fi" in text or "science fiction" in text:
        tags.append("Creativ")
    if "action" in text:
        tags.append("Alert")
    if "adventure" in text:
        tags.append("Plin de aventură")
    if "comedy" in text:
        tags.append("Amuzant")
    if "romance" in text:
        tags.append("Romantic")
    if "horror" in text:
        tags.append("Înspăimântător")

    return ", ".join(tags) if tags else None


def adauga_film_din_api(titlu: str, sala_id: int):
    data = cauta_film_in_api(titlu)
    if not data:
        return None

    titlu_film = data.get("Title", titlu)

    durata_str = data.get("Runtime", "0 min")
    durata = 0
    if durata_str.split():
        try:
            durata = int(durata_str.split()[0])
        except ValueError:
            durata = 0

    descriere = data.get("Plot", None)
    rated = data.get("Rated", None)

    poster = data.get("Poster", None)
    if poster == "N/A":
        poster = None

    actori = data.get("Actors", None)
    genuri = data.get("Genre", None)
    tags = genereaza_etichete_din_genuri(genuri)

    return adauga_film(
        titlu=titlu_film,
        durata=durata,
        sala_id=int(sala_id),
        descriere=descriere,
        rated=rated,
        poster=poster,
        actori=actori,
        genuri=genuri,
        tags=tags,
    )
