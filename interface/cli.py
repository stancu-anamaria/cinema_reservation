import streamlit as st

from services.rezervari_service import (
    creeaza_rezervare_multi,
    sterge_rezervare,
    incarca_rezervari,
)
from services.admin_service import (
    adauga_sala,
    adauga_film,
    incarca_filme,
    incarca_sali,
)
from services.api_filme_service import adauga_film_din_api


# ----------------- CONFIG PAGINĂ -----------------

st.set_page_config(
    page_title="Cinema Reservation",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Sistem de Rezervare Cinema")
st.write("Bun venit! Alege o acțiune din meniul din stânga.")


# ----------------- MENIU LATERAL -----------------

meniu = st.sidebar.selectbox(
    "Navigare",
    [
        "Vizualizare filme",
        "Adaugă film manual",
        "Adaugă film din API",
        "Adaugă sală",
        "Creează rezervare",
        "Anulează rezervare",
        "Vizualizare rezervări",
    ]
)


# ----------------- VIZUALIZARE FILME -----------------

if meniu == "Vizualizare filme":
    st.header("📽 Filme disponibile")

    filme = incarca_filme()

    if not filme:
        st.info("Nu există filme înregistrate încă.")
    else:
        for f in filme:
            st.subheader(f.get("titlu", "Fără titlu"))
            st.write(f"ID film: {f.get('id_film', 'N/A')}")
            st.write(f"Durata: {f.get('durata', 0)} minute")
            st.write(f"Sală ID: {f.get('sala_id', 'N/A')}")
            st.write("---")


# ----------------- ADAUGĂ FILM MANUAL -----------------

elif meniu == "Adaugă film manual":
    st.header("➕ Adaugă film manual")

    titlu = st.text_input("Titlul filmului")
    durata = st.number_input("Durata (minute)", min_value=1, step=1)
    sala_id = st.number_input("ID Sală", min_value=1, step=1)

    if st.button("Adaugă film"):
        if not titlu.strip():
            st.warning("Te rog să introduci titlul filmului.")
        else:
            film = adauga_film(
                titlu=titlu.strip(),
                durata=int(durata),
                sala_id=int(sala_id),
            )
            st.success(
                f"Film adăugat cu succes! "
                f"ID: {film['id_film']} | Titlu: {film['titlu']} | "
                f"Durată: {film['durata']} min | Sală: {film['sala_id']}"
            )


# ----------------- ADAUGĂ FILM DIN API -----------------

elif meniu == "Adaugă film din API":
    st.header("🎥 Adaugă film automat din OMDb API")

    titlu = st.text_input("Titlul filmului (exact sau aproximativ)")
    sala_id = st.number_input("ID Sală", min_value=1, step=1)

    if st.button("Caută și adaugă film"):
        if not titlu.strip():
            st.warning("Te rog să introduci titlul filmului.")
        else:
            film = adauga_film_din_api(titlu.strip(), int(sala_id))
            if film:
                st.success(
                    f"Film adăugat automat: {film['titlu']} "
                    f"({film['durata']} min), sală ID {film['sala_id']} "
                    f"(ID film: {film['id_film']})"
                )
            else:
                st.error("Nu s-a găsit filmul în API sau a apărut o eroare.")


# ----------------- ADAUGĂ SALĂ -----------------

elif meniu == "Adaugă sală":
    st.header("🏢 Adaugă sală")

    nume = st.text_input("Nume sală")
    randuri = st.number_input("Număr de rânduri", min_value=1, step=1)
    locuri = st.number_input("Locuri pe rând", min_value=1, step=1)

    if st.button("Adaugă sală"):
        if not nume.strip():
            st.warning("Te rog să introduci numele sălii.")
        else:
            sala = adauga_sala(
                nume=nume.strip(),
                randuri=int(randuri),
                locuri_pe_rand=int(locuri),
            )
            st.success(f"Sală adăugată cu ID: {sala['id_sala']}")


# ----------------- CREEAZĂ REZERVARE -----------------

elif meniu == "Creează rezervare":
    st.header("🎟 Creează rezervare")

    filme = incarca_filme()
    sali = incarca_sali()

    if not filme or not sali:
        st.info("Trebuie să existe cel puțin un film și o sală pentru a crea o rezervare.")
    else:
        opt_film = st.selectbox(
            "Alege filmul",
            options=filme,
            format_func=lambda f: f"[{f['id_film']}] {f['titlu']}"
        )

        opt_sala = st.selectbox(
            "Alege sala",
            options=sali,
            format_func=lambda s: f"[{s['id_sala']}] {s['nume']}"
        )

        rand = st.number_input("Rând", min_value=1, step=1)
        loc = st.number_input("Loc", min_value=1, step=1)

        if st.button("Creează rezervare"):
            rezervare = creeaza_rezervare_multi(
                film_id=opt_film["id_film"],
                sala_id=opt_sala["id_sala"],
                rand=int(rand),
                loc=int(loc),
            )
            st.success(
                f"Rezervare creată! "
                f"ID: {rezervare['id_rezervare']} | "
                f"Film: {opt_film['titlu']} | "
                f"Sală: {opt_sala['nume']} | "
                f"Rând: {rezervare['rand']} | "
                f"Loc: {rezervare['loc']}"
            )


# ----------------- ANULEAZĂ REZERVARE -----------------

elif meniu == "Anulează rezervare":
    st.header("❌ Anulează rezervare")

    rezervari = incarca_rezervari()
    if not rezervari:
        st.info("Nu există rezervări înregistrate.")
    else:
        opt_rez = st.selectbox(
            "Alege rezervarea",
            options=rezervari,
            format_func=lambda r: f"ID {r['id_rezervare']} - Film {r['film_id']} | Sală {r['sala_id']} | Rând {r['rand']} Loc {r['loc']}"
        )

        if st.button("Anulează rezervare"):
            sterge_rezervare(opt_rez["id_rezervare"])
            st.success(f"Rezervarea cu ID {opt_rez['id_rezervare']} a fost anulată.")


# ----------------- VIZUALIZARE REZERVĂRI -----------------

elif meniu == "Vizualizare rezervări":
    st.header("📋 Rezervări existente")

    rezervari = incarca_rezervari()
    if not rezervari:
        st.info("Nu există rezervări înregistrate.")
    else:
        for r in rezervari:
            st.write(
                f"ID rezervare: {r['id_rezervare']} | "
                f"Film ID: {r['film_id']} | "
                f"Sală ID: {r['sala_id']} | "
                f"Rând: {r['rand']} | Loc: {r['loc']}"
            )
            st.write("---")
