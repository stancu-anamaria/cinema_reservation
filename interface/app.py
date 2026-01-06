from __future__ import annotations

import base64
from pathlib import Path

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

LOGIN_BG_PATH = Path("assets/login_bg.jpg")  # pune aici o imagine (jpg/png)


def _rerun() -> None:
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()


def _init_state() -> None:
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("username", None)
    st.session_state.setdefault("role", "Client")
    st.session_state.setdefault("is_admin", False)

    st.session_state.setdefault("menu_choice", None)
    st.session_state.setdefault("navigate_to", None)

    st.session_state.setdefault("filme_filter_sala_id", None)


def _apply_pending_navigation() -> None:
    target = st.session_state.get("navigate_to")
    if target:
        st.session_state["menu_choice"] = target
        st.session_state["navigate_to"] = None


def _inject_login_background(image_path: Path | None = None) -> None:
    """
    Sets a nice login background. If image_path exists, uses it as base64 data URL.
    Fallback: gradient only.
    """
    bg_css = ""
    if image_path and image_path.exists():
        raw = image_path.read_bytes()
        b64 = base64.b64encode(raw).decode("utf-8")
        suffix = image_path.suffix.lower().replace(".", "")
        mime = "jpeg" if suffix in ("jpg", "jpeg") else suffix
        bg_css = f'url("data:image/{mime};base64,{b64}")'
    else:
        bg_css = "none"

    st.markdown(
        f"""
        <style>
          /* Main app background */
          div[data-testid="stAppViewContainer"] {{
            background:
              linear-gradient(180deg, rgba(8,10,14,0.92), rgba(8,10,14,0.92)),
              {bg_css};
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
          }}

          /* Make header transparent for nicer look */
          header[data-testid="stHeader"] {{
            background: transparent;
          }}

          /* Slightly center + max width for login card */
          .cc-login-wrap {{
            max-width: 920px;
            margin: 0 auto;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def login(username: str, password: str) -> None:
    user = (username or "").strip()
    pwd = (password or "").strip()

    if user == "admin" and pwd == "admin123":
        st.session_state.logged_in = True
        st.session_state.username = user
        st.session_state.role = "Administrator"
        st.session_state.is_admin = True
        st.session_state.menu_choice = None
        st.session_state.navigate_to = None
        st.success("Te-ai autentificat ca administrator.")
        _rerun()

    if user and pwd:
        st.session_state.logged_in = True
        st.session_state.username = user
        st.session_state.role = "Client"
        st.session_state.is_admin = False
        st.session_state.menu_choice = None
        st.session_state.navigate_to = None
        st.info("Te-ai autentificat ca și client (drepturi limitate).")
        _rerun()


def login_as_guest() -> None:
    st.session_state.logged_in = True
    st.session_state.username = "vizitator"
    st.session_state.role = "Client"
    st.session_state.is_admin = False
    st.session_state.menu_choice = None
    st.session_state.navigate_to = None
    st.info("Ai intrat ca vizitator (client).")
    _rerun()


def logout() -> None:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = "Client"
    st.session_state.is_admin = False
    st.session_state.menu_choice = None
    st.session_state.navigate_to = None
    st.session_state.filme_filter_sala_id = None
    _rerun()


def render_login_screen() -> None:
    _inject_login_background(LOGIN_BG_PATH)

    st.markdown('<div class="cc-login-wrap">', unsafe_allow_html=True)
    st.title("🎬 Sistem de Rezervare Cinema")
    st.write("Autentifică-te ca să accesezi meniul aplicației.")

    with st.container(border=True):
        st.subheader("🔐 Autentificare")

        with st.form("login_form"):
            username = st.text_input("Nume utilizator", placeholder="Numele tău")
            password = st.text_input("Parolă", type="password", placeholder="Parola ta")
            submitted = st.form_submit_button("Autentificare")

        cols = st.columns(2)
        with cols[0]:
            if submitted:
                login(username, password)
        with cols[1]:
            if st.button("Intră ca vizitator"):
                login_as_guest()

    st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar(is_admin: bool) -> str:
    _apply_pending_navigation()

    st.sidebar.markdown("## 👤 Profil")
    st.sidebar.markdown(f"**Utilizator:** `{st.session_state.username}`")
    st.sidebar.markdown(f"**Rol:** `{st.session_state.role}`")

    if is_admin:
        st.sidebar.success("✅ Administrator")
    if st.sidebar.button("Delogare 🚪"):
        logout()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Meniu")

    if is_admin:
        optiuni = [
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
        optiuni = [
            "Vizualizare filme",
            "Vizualizare săli",
            "Creează rezervare",
            "Vizualizare rezervări",
        ]

    default = st.session_state.menu_choice or optiuni[0]
    if default not in optiuni:
        default = optiuni[0]

    menu = st.sidebar.radio(
        "Alege opțiunea:",
        optiuni,
        index=optiuni.index(default),
        key="menu_choice",
    )
    return menu


def route(menu: str, is_admin: bool) -> None:
    st.info(
        f"Ești autentificat ca: **{st.session_state.role}**"
        f"{' (utilizator: ' + st.session_state.username + ')' if st.session_state.username else ''}"
    )

    if menu == "Vizualizare filme":
        pagina_vizualizare_filme()
    elif menu == "Adaugă film manual":
        pagina_adauga_film_manual()
    elif menu == "Sugestii filme":
        pagina_sugestii_filme(is_admin=is_admin)
    elif menu == "Șterge film":
        pagina_sterge_film(is_admin=is_admin)
    elif menu == "Vizualizare săli":
        pagina_vizualizare_sali()
    elif menu == "Adaugă sală":
        pagina_adauga_sala(is_admin=is_admin)
    elif menu == "Șterge sală":
        pagina_sterge_sala(is_admin=is_admin)
    elif menu == "Creează rezervare":
        pagina_creeaza_rezervare()
    elif menu == "Anulează rezervare":
        pagina_anuleaza_rezervare(is_admin=is_admin)
    elif menu == "Vizualizare rezervări":
        pagina_vizualizare_rezervari()


def main() -> None:
    st.set_page_config(
        page_title="Sistem de Rezervare Cinema",
        page_icon="🎬",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    _init_state()

    if not st.session_state.logged_in:
        render_login_screen()
        return

    menu = render_sidebar(is_admin=st.session_state.is_admin)
    route(menu, is_admin=st.session_state.is_admin)


if __name__ == "__main__":
    main()
