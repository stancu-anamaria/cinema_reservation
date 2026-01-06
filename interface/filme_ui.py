# path: interface/filme_ui.py
from __future__ import annotations

import os
import random
import uuid

import streamlit as st

from services.admin_service import adauga_film, incarca_filme, sterge_film
from services.api_filme_service import cauta_film_in_api


def _rerun() -> None:
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()


def film_exista_deja(titlu: str, sala_id: int) -> bool:
    filme = incarca_filme()
    titlu_norm = titlu.strip().lower()
    sala_id = int(sala_id)

    for f in filme:
        if f.get("titlu", "").strip().lower() == titlu_norm and int(f.get("sala_id", 0)) == sala_id:
            return True
    return False


def traduce_genuri(genuri_en: str | None) -> str | None:
    if not genuri_en:
        return None

    mapping = {
        "action": "Acțiune",
        "adventure": "Aventură",
        "drama": "Dramă",
        "sci-fi": "SF",
        "science fiction": "SF",
        "comedy": "Comedie",
        "romance": "Romantic",
        "fantasy": "Fantezie",
        "horror": "Horror",
        "thriller": "Thriller",
        "animation": "Animație",
        "family": "Familie",
        "crime": "Crime",
        "mystery": "Mister",
        "history": "Istoric",
        "war": "Război",
        "biography": "Biografic",
    }

    rezultat: list[str] = []
    for g in genuri_en.split(","):
        g_curat = g.strip()
        key = g_curat.lower()
        rezultat.append(mapping.get(key, g_curat))

    return ", ".join(rezultat)


def traduce_rated(rated_en: str | None) -> str | None:
    if not rated_en or rated_en == "N/A":
        return None

    mapping = {
        "G": "AG – recomandat tuturor vârstelor",
        "PG": "AP-12 – pentru copii, cu acordul părinților",
        "PG-13": "AP-13 – nerecomandat sub 13 ani",
        "R": "N-15 – interzis sub 15 ani neînsoțiți",
        "NC-17": "IM-18 – interzis minorilor sub 18 ani",
    }
    return mapping.get(rated_en, rated_en)


def genereaza_tags_din_genuri(genuri_en: str | None) -> str | None:
    if not genuri_en:
        return None

    text = genuri_en.lower()
    tags: list[str] = []

    if "drama" in text:
        tags.append("Tulburător")
    if "sci-fi" in text or "science fiction" in text:
        tags.append("Imaginativ")
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
    if "thriller" in text:
        tags.append("Tensionat")

    return ", ".join(tags) if tags else None


def pagina_vizualizare_filme() -> None:
    st.header("🎥 Filme disponibile")

    filtre_sala_id = st.session_state.get("filme_filter_sala_id")

    # Filtrul NU apare în pagină, doar control discret în sidebar.
    if filtre_sala_id is not None:
        with st.sidebar.expander("🔎 Filtru", expanded=False):
            st.caption(f"Sală selectată: {filtre_sala_id}")
            if st.button("Resetează filtrul", key="reset_filtru_filme"):
                st.session_state["filme_filter_sala_id"] = None
                _rerun()

    filme = incarca_filme()
    if filtre_sala_id is not None:
        filme = [f for f in filme if int(f.get("sala_id", 0)) == int(filtre_sala_id)]

    if not filme:
        st.info("Nu există filme înregistrate.")
        return

    for f in filme:
        titlu = f.get("titlu", "Fără titlu")
        durata = f.get("durata", "N/A")
        sala_id = f.get("sala_id", "N/A")
        descriere = f.get("descriere", None)
        rated = f.get("rated", None)
        poster = f.get("poster", None)
        actori = f.get("actori", None)
        genuri = f.get("genuri", None)
        tags = f.get("tags", None)

        with st.container(border=True):
            st.markdown(f"### 🎬 {titlu}")
            col1, col2 = st.columns([1, 2])

            with col1:
                if poster:
                    st.image(poster, use_container_width=True)

            with col2:
                st.write(f"⏱ **Durată:** {durata} minute")
                st.write(f"🏢 **Sală:** {sala_id}")
                if rated:
                    st.write(f"🔞 **Clasificare vârstă:** {rated}")
                if actori:
                    st.write(f"**Distribuție:** {actori}")
                if genuri:
                    st.write(f"**Genuri:** {genuri}")
                if tags:
                    st.write(f"**Acest film este:** {tags}")
                if descriere:
                    st.write("**Descriere:**")
                    st.write(descriere)


def pagina_adauga_film_manual() -> None:
    st.header("➕ Adaugă film manual")

    from services.admin_service import incarca_sali

    sali = incarca_sali()
    if not sali:
        st.info("Nu există săli. Înainte de a adăuga filme, adaugă cel puțin o sală.")
        return

    titlu = st.text_input("Titlul filmului (în română)")
    durata = st.number_input("Durata (minute)", min_value=1, step=1)

    opt_sala = st.selectbox("Alege sala", options=sali, format_func=lambda s: f"{s['nume']}")
    sala_id = opt_sala["id_sala"]

    descriere = st.text_area("Descriere (în română, opțional)")
    rated = st.text_input("Clasificare vârstă (opțional)")
    actori = st.text_input("Distribuție (opțional)")
    genuri = st.text_input("Genuri (opțional)")
    tags = st.text_input("Acest film este... (opțional)")

    poster_file = st.file_uploader("Poster film (opțional)", type=["png", "jpg", "jpeg"])

    if st.button("Adaugă film"):
        if not titlu.strip():
            st.warning("Te rog să introduci titlul filmului.")
            return
        if film_exista_deja(titlu, int(sala_id)):
            st.warning("Acest film există deja în această sală.")
            return

        poster_path = None
        if poster_file is not None:
            posters_dir = os.path.join("data", "postere")
            os.makedirs(posters_dir, exist_ok=True)
            ext = os.path.splitext(poster_file.name)[1]
            filename = f"poster_{uuid.uuid4().hex}{ext}"
            full_path = os.path.join(posters_dir, filename)
            with open(full_path, "wb") as f_out:
                f_out.write(poster_file.getbuffer())
            poster_path = full_path

        film = adauga_film(
            titlu=titlu.strip(),
            durata=int(durata),
            sala_id=int(sala_id),
            descriere=descriere.strip() if descriere.strip() else None,
            rated=rated.strip() if rated.strip() else None,
            poster=poster_path,
            actori=actori.strip() if actori.strip() else None,
            genuri=genuri.strip() if genuri.strip() else None,
            tags=tags.strip() if tags.strip() else None,
        )
        st.success(f"Film adăugat: **{film['titlu']}**")


def pagina_sugestii_filme(is_admin: bool) -> None:
    st.header("💡 Sugestii filme (pentru administrator)")

    if not is_admin:
        st.error("Doar administratorul poate folosi sugestiile de filme.")
        return

    from services.admin_service import incarca_sali

    sali = incarca_sali()
    if not sali:
        st.info("Nu există săli. Adaugă o sală înainte de a salva filme sugerate.")
        return

    opt_sala = st.selectbox("Sală", options=sali, format_func=lambda s: f"{s['nume']}")
    sala_id = opt_sala["id_sala"]

    if "seed_sugestii" not in st.session_state:
        st.session_state["seed_sugestii"] = 0

    if st.button("🔁 Reîncarcă sugestiile"):
        st.session_state["seed_sugestii"] += 1

    random.seed(st.session_state["seed_sugestii"])

    toate_titlurile = [
        "Inception",
        "The Dark Knight",
        "Interstellar",
        "Avatar",
        "Titanic",
        "The Matrix",
        "Gladiator",
        "The Lord of the Rings: The Fellowship of the Ring",
        "Pulp Fiction",
        "Forrest Gump",
        "The Shawshank Redemption",
        "The Godfather",
        "Fight Club",
    ]

    titluri_sugestii = random.sample(toate_titlurile, k=min(5, len(toate_titlurile)))

    sugestii_data: list[dict] = []
    for titlu in titluri_sugestii:
        data = cauta_film_in_api(titlu)
        if data:
            sugestii_data.append(data)

    if not sugestii_data:
        st.error("Nu s-au putut încărca sugestiile din baza de date.")
        return

    for idx, data in enumerate(sugestii_data):
        titlu_en = data.get("Title", "Fără titlu")
        an = data.get("Year", "N/A")
        durata_str = data.get("Runtime", "N/A")
        rated_en = data.get("Rated", "N/A")
        descriere_en = data.get("Plot", "Nu există descriere disponibilă.")
        poster = data.get("Poster", None)
        if poster == "N/A":
            poster = None

        actori_en = data.get("Actors", "")
        genuri_en = data.get("Genre", "")

        rated_ro_default = traduce_rated(rated_en) or ""
        genuri_ro_default = traduce_genuri(genuri_en) or ""
        tags_default = genereaza_tags_din_genuri(genuri_en) or ""

        with st.container(border=True):
            st.markdown(f"### 🎬 {titlu_en} ({an})")

            col1, col2 = st.columns([1, 2])
            with col1:
                if poster:
                    st.image(poster, use_container_width=True)
            with col2:
                st.caption("Informații originale")
                st.write(f"Durată: {durata_str}")
                st.write(f"Clasificare: {rated_en}")
                if actori_en:
                    st.write(f"Distribuție: {actori_en}")
                if genuri_en:
                    st.write(f"Genuri: {genuri_en}")
                st.write(descriere_en)

            titlu_ro = st.text_input("Titlu pentru clienți", value=titlu_en, key=f"titlu_ro_{idx}")

            durata_min = 0
            if durata_str.split():
                try:
                    durata_min = int(durata_str.split()[0])
                except ValueError:
                    durata_min = 0

            rated_ro = st.text_input("Clasificare vârstă", value=rated_ro_default, key=f"rated_ro_{idx}")
            genuri_ro = st.text_input("Genuri (RO)", value=genuri_ro_default, key=f"genuri_ro_{idx}")
            actori_ro = st.text_input("Distribuție", value=actori_en, key=f"actori_ro_{idx}")
            tags_ro = st.text_input("Acest film este...", value=tags_default, key=f"tags_ro_{idx}")
            descriere_ro = st.text_area("Descriere (RO)", key=f"descriere_ro_{idx}")

            if st.button("Salvează filmul", key=f"salveaza_film_{idx}"):
                if not titlu_ro.strip():
                    st.warning("Te rog să introduci titlul filmului.")
                    continue
                if film_exista_deja(titlu_ro, int(sala_id)):
                    st.warning("Acest film există deja în această sală.")
                    continue

                film = adauga_film(
                    titlu=titlu_ro.strip(),
                    durata=int(durata_min) if durata_min > 0 else 0,
                    sala_id=int(sala_id),
                    descriere=descriere_ro.strip() if descriere_ro.strip() else None,
                    rated=rated_ro.strip() if rated_ro.strip() else None,
                    poster=poster,
                    actori=actori_ro.strip() if actori_ro.strip() else None,
                    genuri=genuri_ro.strip() if genuri_ro.strip() else None,
                    tags=tags_ro.strip() if tags_ro.strip() else None,
                )
                st.success(f"Film salvat: **{film['titlu']}**")


def pagina_sterge_film(is_admin: bool) -> None:
    st.header("🗑 Șterge film")

    if not is_admin:
        st.error("Doar administratorul poate șterge filme.")
        return

    filme = incarca_filme()
    if not filme:
        st.info("Nu există filme înregistrate.")
        return

    opt_film = st.selectbox("Alege filmul", options=filme, format_func=lambda f: f"{f['titlu']}")
    st.warning("Atenție: la ștergere se șterg și rezervările asociate.")

    confirm = st.checkbox("Confirm ștergerea acestui film.")
    if st.button("Șterge film definitiv", type="primary", disabled=not confirm):
        sterge_film(opt_film["id_film"])
        st.success(f"Filmul '{opt_film['titlu']}' a fost șters.")
        _rerun()
