import streamlit as st

from interface.filme_ui import (
    pagina_vizualizare_filme,
    pagina_adauga_film_manual,
    pagina_sugestii_filme,
    pagina_sterge_film,
)
from interface.sali_ui import (
    pagina_vizualizare_sali,
    pagina_adauga_sala,
    pagina_sterge_sala,
)
from interface.rezervari_ui import (
    pagina_creeaza_rezervare,
    pagina_anuleaza_rezervare,
    pagina_vizualizare_rezervari,
)


# ----------------- CONFIG PAGINĂ -----------------

st.set_page_config(
    page_title="Sistem de Rezervare Cinema",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Sistem de Rezervare Cinema")
st.write("Bun venit! Alege o acțiune din meniul din stânga.")


# ----------------- INITIALIZARE SESSION STATE -----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = "Client"
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False


# ----------------- AUTENTIFICARE -----------------

def login(username: str, password: str):
    if username == "admin" and password == "admin123":
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = "Administrator"
        st.session_state.is_admin = True
        st.success("Te-ai autentificat ca administrator.")
    elif username and password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = "Client"
        st.session_state.is_admin = False
        st.info("Te-ai autentificat ca și client (drepturi limitate).")


def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = "Client"
    st.session_state.is_admin = False
    st.experimental_rerun()


# ----------------- SIDEBAR: PROFIL / LOGIN -----------------

st.sidebar.markdown("## 👤 Profil")

if st.session_state.logged_in:
    st.sidebar.markdown(f"**Utilizator:** `{st.session_state.username}`")
    st.sidebar.markdown(f"**Rol:** `{st.session_state.role}`")

    if st.session_state.is_admin:
        st.sidebar.success("✅ Ai toate drepturile (administrator).")
    else:
        st.sidebar.info("👀 Ești client – poți vizualiza și face rezervări.")

    if st.sidebar.button("Delogare 🚪"):
        logout()
else:
    st.sidebar.markdown("### Autentificare")
    input_user = st.sidebar.text_input("Nume utilizator")
    input_pass = st.sidebar.text_input("Parolă", type="password")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Autentificare"):
            login(input_user.strip(), input_pass.strip())
    with col2:
        if st.button("Intră ca vizitator"):
            st.session_state.logged_in = True
            st.session_state.username = "vizitator"
            st.session_state.role = "Client"
            st.session_state.is_admin = False
            st.info("Ai intrat ca vizitator (client).")

role = st.session_state.role
is_admin = st.session_state.is_admin


# ----------------- MENIU LATERAL -----------------

if is_admin:
    optiuni_meniu = [
        "Vizualizare filme",
        "Adaugă film manual",
        "Sugestii filme",
        "Șterge film",
        "Vizualizare săli",
        "Adaugă sală",
        "Șterge sală",
        "Creează rezervare",
        "Anulează rezervare",
        "Vizualizare rezervări",
    ]
else:
    optiuni_meniu = [
        "Vizualizare filme",
        "Creează rezervare",
        "Vizualizare rezervări",
    ]

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Meniu")
meniu = st.sidebar.radio("Alege opțiunea:", optiuni_meniu)


# ----------------- INFO ROL SUS -----------------

st.info(
    f"Ești autentificat ca: **{role}**"
    f"{' (utilizator: ' + st.session_state.username + ')' if st.session_state.username else ''}"
)


# ----------------- RUTARE CĂTRE PAGINI -----------------

if meniu == "Vizualizare filme":
    pagina_vizualizare_filme()

elif meniu == "Adaugă film manual":
    pagina_adauga_film_manual(is_admin=is_admin)

elif meniu == "Sugestii filme":
    pagina_sugestii_filme(is_admin=is_admin)

elif meniu == "Șterge film":
    pagina_sterge_film(is_admin=is_admin)

elif meniu == "Vizualizare săli":
    pagina_vizualizare_sali()

elif meniu == "Adaugă sală":
    pagina_adauga_sala(is_admin=is_admin)

elif meniu == "Șterge sală":
    pagina_sterge_sala(is_admin=is_admin)

elif meniu == "Creează rezervare":
    pagina_creeaza_rezervare()

elif meniu == "Anulează rezervare":
    pagina_anuleaza_rezervare(is_admin=is_admin)

elif meniu == "Vizualizare rezervări":
    pagina_vizualizare_rezervari(is_admin=is_admin)
