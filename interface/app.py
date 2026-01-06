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

LOGIN_BG_PATH = Path("assets/login_bg.jpg")  # optional


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


def _inject_global_style(image_path: Path | None = None) -> None:
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
          /* Hide Streamlit default menu/footer */
          #MainMenu {{visibility:hidden;}}
          footer {{visibility:hidden;}}
          header[data-testid="stHeader"] {{background: transparent;}}

          /* App background */
          div[data-testid="stAppViewContainer"] {{
            background:
              radial-gradient(1200px 800px at 20% 10%, rgba(90, 70, 255, 0.28), rgba(0,0,0,0) 55%),
              radial-gradient(900px 600px at 80% 0%, rgba(255, 80, 120, 0.18), rgba(0,0,0,0) 60%),
              linear-gradient(180deg, rgba(10, 12, 20, 0.80), rgba(10, 12, 20, 0.92)),
              {bg_css};
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
          }}

          /* Wider overall content a bit nicer */
          section.main > div {{
            max-width: 1100px;
            padding-top: 1.2rem;
          }}

          /* Login layout: center vertically */
          .cc-login-page {{
            min-height: calc(100vh - 6rem);
            display: flex;
            align-items: center;
            justify-content: center;
          }}

          .cc-login-grid {{
            width: 100%;
            max-width: 980px;
            display: grid;
            grid-template-columns: 1.1fr 0.9fr;
            gap: 22px;
          }}

          /* Left hero */
          .cc-hero {{
            padding: 28px 28px;
            border-radius: 22px;
            border: 1px solid rgba(255,255,255,0.10);
            background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.35);
          }}

          .cc-hero h1 {{
            margin: 0;
            font-size: 44px;
            line-height: 1.05;
            letter-spacing: -0.02em;
            color: rgba(255,255,255,0.95);
          }}

          .cc-hero p {{
            margin: 12px 0 0 0;
            font-size: 16px;
            color: rgba(255,255,255,0.70);
          }}

          .cc-pill {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.12);
            background: rgba(255,255,255,0.06);
            color: rgba(255,255,255,0.85);
            font-size: 13px;
            margin-top: 16px;
          }}

          /* Right login card */
          .cc-card {{
            padding: 22px 20px;
            border-radius: 22px;
            border: 1px solid rgba(255,255,255,0.12);
            background: rgba(15, 17, 26, 0.55);
            backdrop-filter: blur(14px);
            box-shadow: 0 18px 55px rgba(0,0,0,0.38);
          }}

          .cc-card h2 {{
            margin: 0 0 8px 0;
            font-size: 20px;
            color: rgba(255,255,255,0.92);
          }}

          .cc-card small {{
            color: rgba(255,255,255,0.65);
          }}

          /* Make Streamlit inputs nicer */
          div[data-testid="stTextInput"] > div {{
            border-radius: 14px;
          }}

          /* Buttons nicer */
          .stButton > button {{
            border-radius: 14px !important;
            padding: 0.60rem 0.9rem !important;
            border: 1px solid rgba(255,255,255,0.14) !important;
          }}

          /* Primary button */
          div[data-testid="stFormSubmitButton"] button {{
            background: linear-gradient(90deg, rgba(90,70,255,1), rgba(255,80,120,1)) !important;
            color: white !important;
            border: none !important;
            font-weight: 650 !important;
          }}

          /* Sidebar styling */
          section[data-testid="stSidebar"] > div {{
            background: linear-gradient(180deg, rgba(15,17,26,0.92), rgba(15,17,26,0.80));
            border-right: 1px solid rgba(255,255,255,0.08);
          }}

          /* Responsive */
          @media (max-width: 900px) {{
            .cc-login-grid {{
              grid-template-columns: 1fr;
            }}
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
        return

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
    _inject_global_style(LOGIN_BG_PATH)

    st.markdown('<div class="cc-login-page">', unsafe_allow_html=True)
    st.markdown('<div class="cc-login-grid">', unsafe_allow_html=True)

    # HERO (stânga)
    st.markdown(
        """
        <div class="cc-hero">
          <div class="cc-pill">🎬 <b>Cinema Reservation</b> · Rapid · Simplu · Modern</div>
          <h1>Sistem de Rezervare<br/>Cinema</h1>
          <p>
            Alege filmul, selectează locurile preferate și vezi biletele în contul tău.
            Plata se face la casierie.
          </p>
          <div class="cc-pill">⭐ Recomandare: vino cu cel puțin <b>30 min</b> mai devreme</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # CARD (dreapta)
    st.markdown('<div class="cc-card">', unsafe_allow_html=True)
    st.markdown("<h2>🔐 Autentificare</h2><small>Intră cu contul tău sau ca vizitator.</small>", unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Nume utilizator", placeholder="ex: andrei.popescu")
        password = st.text_input("Parolă", type="password", placeholder="parola ta")
        submitted = st.form_submit_button("Autentificare")

    col1, col2 = st.columns(2)
    with col1:
        if submitted:
            login(username, password)
    with col2:
        if st.button("Intră ca vizitator"):
            login_as_guest()

    st.markdown(
        "<div style='margin-top:12px; opacity:0.75; font-size:12px;'>"
        "Admin demo: <b>admin</b> / <b>admin123</b>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)  # cc-card

    st.markdown("</div>", unsafe_allow_html=True)  # cc-login-grid
    st.markdown("</div>", unsafe_allow_html=True)  # cc-login-page


def render_sidebar(is_admin: bool) -> str:
    _apply_pending_navigation()

    st.sidebar.markdown("## 👤 Profil")
    st.sidebar.markdown(f"**Utilizator:** `{st.session_state.username}`")
    st.sidebar.markdown(f"**Rol:** `{st.session_state.role}`")

    if is_admin:
        st.sidebar.success("✅ Administrator")
    else:
        st.sidebar.info("👀 Client")

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
        pagina_vizualizare_filme(is_admin=is_admin)
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
        pagina_vizualizare_rezervari(is_admin=is_admin)


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

    # aplicăm stilul global și după login (sidebar + background consistent)
    _inject_global_style(LOGIN_BG_PATH)

    menu = render_sidebar(is_admin=st.session_state.is_admin)
    route(menu, is_admin=st.session_state.is_admin)


if __name__ == "__main__":
    main()
