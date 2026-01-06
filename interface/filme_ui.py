import streamlit as st
import os
import uuid
import random

from services.admin_service import (
    incarca_filme,
    adauga_film,
    sterge_film,
    incarca_sali,
)
from services.api_filme_service import cauta_film_in_api


# ------------ funcții ajutătoare (filme, traduceri) ------------


def film_exista_deja(titlu: str, sala_id: int) -> bool:
    filme = incarca_filme()
    titlu_norm = titlu.strip().lower()
    sala_id = int(sala_id)

    for f in filme:
        if (
            f.get("titlu", "").strip().lower() == titlu_norm
            and int(f.get("sala_id", 0)) == sala_id
        ):
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

    rezultat = []
    for g in genuri_en.split(","):
        g_curat = g.strip()
        key = g_curat.lower()
        tradus = mapping.get(key)
        rezultat.append(tradus if tradus else g_curat)

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

    explicatie = mapping.get(rated_en)
    if explicatie:
        return explicatie
    return rated_en


def genereaza_tags_din_genuri(genuri_en: str | None) -> str | None:
    if not genuri_en:
        return None

    text = genuri_en.lower()
    tags = []

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

    if not tags:
        return None
    return ", ".join(tags)


# ----------------- PAGINI -----------------


def pagina_vizualizare_filme(is_admin: bool = False):
    """
    Listează filmele într-un layout frumos:
      - clientul vede doar info utile
      - adminul vede ID-urile în caption, discret
    """
    st.header("🎥 Filme disponibile")

    filme = incarca_filme()
    sali = {s["id_sala"]: s for s in incarca_sali()}

    if not filme:
        st.info("Nu există filme înregistrate încă.")
        return

    for f in filme:
        titlu = f.get("titlu", "Fără titlu")
        durata = f.get("durata")
        sala_id = f.get("sala_id")

        sala = sali.get(sala_id)
        if sala:
            sala_nume = sala["nume"]
        else:
            sala_nume = f"Sală {sala_id}" if sala_id is not None else "Nespecificat"

        descriere = f.get("descriere")
        rated = f.get("rated")
        poster = f.get("poster")
        actori = f.get("actori")
        genuri = f.get("genuri")
        tags = f.get("tags")

        with st.container():
            # titlu mare
            st.markdown(f"## 🎬 {titlu}")

            col_poster, col_info = st.columns([1, 2])

            # poster
            with col_poster:
                if poster:
                    st.image(poster, use_container_width=True)

            # informații film
            with col_info:
                info_st, info_dr = st.columns(2)

                with info_st:
                    if durata:
                        st.write(f"⏱ **Durată:** {durata} minute")
                    st.write(f"🏢 **Sală:** {sala_nume}")

                with info_dr:
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

                # info tehnică doar pentru admin
                if is_admin:
                    st.caption(
                        f"(ID intern film: {f.get('id_film')} | ID intern sală: {sala_id})"
                    )

        st.markdown("---")


def pagina_adauga_film_manual():
    st.header("➕ Adaugă film manual")

    sali = incarca_sali()
    if not sali:
        st.info("Nu există săli. Înainte de a adăuga filme, adaugă cel puțin o sală.")
        return

    titlu = st.text_input("Titlul filmului (în română)")
    durata = st.number_input("Durata (minute)", min_value=1, step=1)

    opt_sala = st.selectbox(
        "Alege sala",
        options=sali,
        format_func=lambda s: f"[{s['id_sala']}] {s['nume']}",
    )
    sala_id = opt_sala["id_sala"]

    descriere = st.text_area("Descriere (în română, opțional)")
    rated = st.text_input("Clasificare vârstă (ex: AG, 12+, 16+, 18+) (opțional)")

    actori = st.text_input("Distribuție (nume actori principali) (opțional)")
    genuri = st.text_input("Genuri (ex: Acțiune, Aventură, SF) (opțional)")
    tags = st.text_input("Acest film este... (ex: Tulburător, Creativ) (opțional)")

    poster_file = st.file_uploader(
        "Poster film (încarcă o imagine de pe calculator – opțional)",
        type=["png", "jpg", "jpeg"],
    )

    if st.button("Adaugă film"):
        if not titlu.strip():
            st.warning("Te rog să introduci titlul filmului.")
        elif film_exista_deja(titlu, int(sala_id)):
            st.warning("Acest film există deja în această sală.")
        else:
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
            st.success(
                f"Film adăugat cu succes! "
                f"ID: {film['id_film']} | Titlu: {film['titlu']} | "
                f"Durată: {film['durata']} min | Sală: {film['sala_id']}"
            )


def pagina_sugestii_filme(is_admin: bool):
    st.header("💡 Sugestii filme (pentru administrator)")

    if not is_admin:
        st.error("Doar administratorul poate folosi sugestiile de filme.")
        return

    sali = incarca_sali()
    if not sali:
        st.info("Nu există săli. Adaugă o sală înainte de a salva filme sugerate.")
        return

    opt_sala = st.selectbox(
        "Sală în care vor fi adăugate filmele sugerate",
        options=sali,
        format_func=lambda s: f"[{s['id_sala']}] {s['nume']}",
    )
    sala_id = opt_sala["id_sala"]

    st.markdown(
        "Mai jos ai câteva filme sugerate dintr-o bază de date online (în engleză). "
        "Tu vezi informațiile originale, iar dedesubt completezi/verify versiunea "
        "care va fi salvată pentru clienți. "
        "Genurile și clasificarea de vârstă sunt propuse în română, "
        "dar le poți modifica."
    )

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

    k = min(5, len(toate_titlurile))
    titluri_sugestii = random.sample(toate_titlurile, k=k)

    sugestii_data = []
    for titlu in titluri_sugestii:
        data = cauta_film_in_api(titlu)
        if data:
            sugestii_data.append(data)

    if not sugestii_data:
        st.error("Nu s-au putut încărca sugestiile din baza de date.")
        return

    st.markdown("---")
    st.subheader("Filme sugerate")

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

        with st.container():
            st.markdown(f"### 🎬 {titlu_en} ({an})")
            col1, col2 = st.columns([1, 2])

            with col1:
                if poster:
                    st.image(poster, use_container_width=True)

            with col2:
                st.markdown("**Informații originale:**")
                st.write(f"- Durată: {durata_str}")
                st.write(f"- Clasificare: {rated_en}")
                if actori_en:
                    st.write(f"- Distribuție: {actori_en}")
                if genuri_en:
                    st.write(f"- Genuri: {genuri_en}")
                st.write("**Descriere:**")
                st.write(descriere_en)

            st.markdown("**Date salvate pentru clienți:**")

            titlu_ro = st.text_input(
                "Titlu afișat clienților",
                value=titlu_en,
                key=f"titlu_ro_{idx}",
            )

            durata_min = 0
            if durata_str.split():
                try:
                    durata_min = int(durata_str.split()[0])
                except ValueError:
                    durata_min = 0

            rated_ro = st.text_input(
                "Clasificare vârstă",
                value=rated_ro_default,
                key=f"rated_ro_{idx}",
            )

            genuri_ro = st.text_input(
                "Genuri (în română)",
                value=genuri_ro_default,
                key=f"genuri_ro_{idx}",
            )

            actori_ro = st.text_input(
                "Distribuție",
                value=actori_en,
                key=f"actori_ro_{idx}",
            )

            tags_ro = st.text_input(
                "Acest film este...",
                value=tags_default,
                key=f"tags_ro_{idx}",
            )

            descriere_ro = st.text_area(
                "Descriere pentru clienți",
                key=f"descriere_ro_{idx}",
            )

            if st.button(
                "Salvează filmul pentru clienți",
                key=f"salveaza_film_{idx}",
            ):
                if not titlu_ro.strip():
                    st.warning("Te rog să introduci titlul filmului.")
                elif film_exista_deja(titlu_ro, int(sala_id)):
                    st.warning("Acest film există deja în această sală.")
                else:
                    film = adauga_film(
                        titlu=titlu_ro.strip(),
                        durata=int(durata_min) if durata_min > 0 else 0,
                        sala_id=int(sala_id),
                        descriere=descriere_ro.strip()
                        if descriere_ro.strip()
                        else None,
                        rated=rated_ro.strip() if rated_ro.strip() else None,
                        poster=poster,
                        actori=actori_ro.strip() if actori_ro.strip() else None,
                        genuri=genuri_ro.strip() if genuri_ro.strip() else None,
                        tags=tags_ro.strip() if tags_ro.strip() else None,
                    )
                    st.success(
                        f"Film salvat pentru clienți: {film['titlu']} "
                        f"(ID film: {film['id_film']}, sală ID {film['sala_id']})"
                    )

        st.markdown("---")


def pagina_sterge_film(is_admin: bool):
    st.header("🗑 Șterge film")

    if not is_admin:
        st.error("Doar administratorul poate șterge filme.")
        return

    filme = incarca_filme()
    if not filme:
        st.info("Nu există filme înregistrate.")
        return

    opt_film = st.selectbox(
        "Alege filmul de șters",
        options=filme,
        format_func=lambda f: f"[{f['id_film']}] {f['titlu']}",
    )

    st.warning(
        "Atenție! La ștergerea unui film se vor șterge și rezervările asociate."
    )

    if st.button("Șterge film definitiv"):
        sterge_film(opt_film["id_film"])
        st.success(
            f"Filmul '{opt_film['titlu']}' (ID {opt_film['id_film']}) "
            f"a fost șters, împreună cu rezervările asociate."
        )
