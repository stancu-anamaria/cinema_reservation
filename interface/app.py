import streamlit as st
import json
from services.rezervari_service import creeaza_rezervare, sterge_rezervare, incarca_rezervari
from services.admin_service import (
    adauga_film, adauga_sala,
    incarca_filme, incarca_sali
)


st.set_page_config(page_title="Cinema Reservation", page_icon="🎬", layout="centered")

st.title("🎬 Sistem de Rezervare Cinema")
st.write("Bun venit! Alege o acțiune din meniu.")


# ---------------- MENIU -------------------
meniu = st.sidebar.selectbox(
    "Navigare",
    ["Vizualizare filme", "Adaugă film", "Adaugă sală", "Creează rezervare", "Anulează rezervare"]
)


# ---------------- VIZUALIZARE FILME -------------------
if meniu == "Vizualizare filme":
    st.header("📽 Filme disponibile")
    filme = incarca_filme()

    if not filme:
        st.info("Nu există filme înregistrate.")
    else:
        for f in filme:
            st.subheader(f["titlu"])
            st.write(f"Durata: {f['durata']} minute")
            st.write(f"Sală: {f['sala_id']}")
            st.write("---")


# ---------------- ADAUGĂ FILM -------------------
elif meniu == "Adaugă film":
    st.header("➕ Adaugă film")

    titlu = st.text_input("Titlu")
    durata = st.number_input("Durata", min_value=1)
    sala_id = st.number_input("ID Sala", min_value=1)

    if st.button("Adaugă film"):
        filme = incarca_filme()
        new_id = len(filme) + 1
        adauga_film(new_id, titlu, durata, sala_id)
        st.success("Film adăugat cu succes!")


# ---------------- ADAUGĂ SALĂ -------------------
elif meniu == "Adaugă sală":
    st.header("🏢 Adaugă sală")

    nume = st.text_input("Numele sălii")
    randuri = st.number_input("Număr de rânduri", min_value=1)
    locuri_pe_rand = st.number_input("Locuri pe rând", min_value=1)

    if st.button("Adaugă sală"):
        sali = incarca_sali()
        new_id = len(sali) + 1
        adauga_sala(new_id, nume, randuri, locuri_pe_rand)
        st.success("Sală adăugată!")


# ---------------- CREEAZĂ REZERVARE -------------------
elif meniu == "Creează rezervare":
    st.header("🎟 Creează rezervare")

    film_id = st.number_input("ID Film", min_value=1)
    sala_id = st.number_input("ID Sala", min_value=1)
    rand = st.number_input("Rând", min_value=1)
    loc = st.number_input("Loc", min_value=1)

    if st.button("Rezervă"):
        rezervare = creeaza_rezervare(film_id, sala_id, rand, loc)
        st.success(f"Rezervarea a fost creată! ID: {rezervare['id_rezervare']}")


# ---------------- ANULEAZĂ REZERVARE -------------------
elif meniu == "Anulează rezervare":
    st.header("❌ Anulează rezervare")

    rezervari = incarca_rezervari()
    if not rezervari:
        st.info("Nu există rezervări.")
    else:
        id_list = [r["id_rezervare"] for r in rezervari]
        rez_id = st.selectbox("Selectează ID rezervare", id_list)

        if st.button("Anulează"):
            sterge_rezervare(rez_id)
            st.success("Rezervare anulată.")
