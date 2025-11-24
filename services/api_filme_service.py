import requests
from services.admin_service import adauga_film

API_KEY = "CHEIA_TA_AICI"  # pune cheia ta reală OMDb aici
BASE_URL = "https://www.omdbapi.com/"


def cauta_film_in_api(titlu: str):
    """Caută film în API după titlu și întoarce datele."""
    params = {
        "apikey": API_KEY,
        "t": titlu
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        print("Eroare API:", response.status_code)
        return None

    data = response.json()

    if data.get("Response") == "False":
        print("Film negăsit:", data.get("Error"))
        return None

    return data


def adauga_film_din_api(titlu: str, sala_id: int):
    """Caută film în API + îl adaugă automat în sistem fără input manual."""
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

    film = adauga_film(titlu_film, durata, sala_id)
    print(f"Film adăugat automat din API: {film}")
    return film
