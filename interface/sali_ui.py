# path: interface/sali_ui.py
from __future__ import annotations

import streamlit as st
from services.admin_service import incarca_sali, adauga_sala, sterge_sala


def _rerun() -> None:
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()


def _sala_capacity(sala: dict) -> int:
    return int(sala.get("randuri", 0)) * int(sala.get("locuri_pe_rand", 0))


def _format_sala_label(sala: dict) -> str:
    cap = _sala_capacity(sala)
    return f"{sala['nume']} — {cap} locuri"


def pagina_vizualizare_sali() -> None:
    st.header("🏢 Săli disponibile")

    sali = incarca_sali()
    if not sali:
        st.info("Nu există săli înregistrate încă.")
        return

    c1, c2 = st.columns([2, 1])
    with c1:
        query = st.text_input("🔎 Caută după nume / ID", placeholder="ex: 1, IMAX, Sala 2")
    with c2:
        sort_by = st.selectbox(
            "Sortare",
            options=[
                "ID (crescător)",
                "ID (descrescător)",
                "Nume (A-Z)",
                "Nume (Z-A)",
                "Capacitate (descrescător)",
                "Capacitate (crescător)",
            ],
        )

    q = (query or "").strip().lower()
    if q:
        sali = [
            s for s in sali
            if q in str(s.get("id_sala", "")).lower() or q in str(s.get("nume", "")).lower()
        ]

    if not sali:
        st.warning("Nu am găsit nicio sală pentru filtrul tău.")
        return

    if sort_by == "ID (crescător)":
        sali.sort(key=lambda s: int(s["id_sala"]))
    elif sort_by == "ID (descrescător)":
        sali.sort(key=lambda s: int(s["id_sala"]), reverse=True)
    elif sort_by == "Nume (A-Z)":
        sali.sort(key=lambda s: str(s["nume"]).lower())
    elif sort_by == "Nume (Z-A)":
        sali.sort(key=lambda s: str(s["nume"]).lower(), reverse=True)
    elif sort_by == "Capacitate (descrescător)":
        sali.sort(key=_sala_capacity, reverse=True)
    elif sort_by == "Capacitate (crescător)":
        sali.sort(key=_sala_capacity)

    total_locuri = sum(_sala_capacity(s) for s in sali)
    k1, k2, k3 = st.columns(3)
    k1.metric("Săli", len(sali))
    k2.metric("Locuri totale", total_locuri)
    k3.metric("Capacitate medie", int(total_locuri / max(len(sali), 1)))

    st.markdown("---")

    for s in sali:
        cap = _sala_capacity(s)

        with st.container(border=True):
            left, right = st.columns([3, 2], vertical_alignment="center")

            with left:
                st.markdown(f"### {s['nume']}")
                st.caption(f"Capacitate: {cap} locuri")

                if st.button("🎬 Vezi filmele din această sală", key=f"goto_filme_{s['id_sala']}"):
                    # filtrăm filmele
                    st.session_state["filme_filter_sala_id"] = int(s["id_sala"])

                    # NU modificăm menu_choice direct aici (altfel crăpă dacă radio e deja creat)
                    st.session_state["navigate_to"] = "Vizualizare filme"
                    _rerun()

            with right:
                m1, m2, m3 = st.columns(3)
                m1.metric("Rânduri", int(s["randuri"]))
                m2.metric("Locuri/rând", int(s["locuri_pe_rand"]))
                m3.metric("Total", cap)


def pagina_adauga_sala(is_admin: bool) -> None:
    st.header("➕ Adaugă sală")

    if not is_admin:
        st.error("Doar administratorul poate adăuga săli.")
        return

    with st.form("form_adauga_sala", clear_on_submit=True):
        nume = st.text_input("Nume sală", placeholder="ex: Sala 1 / IMAX")
        cols = st.columns(2)
        with cols[0]:
            randuri = st.number_input("Număr de rânduri", min_value=1, step=1, value=10)
        with cols[1]:
            locuri = st.number_input("Locuri pe rând", min_value=1, step=1, value=12)
        submitted = st.form_submit_button("Salvează sala")

    if not submitted:
        st.info("Completează câmpurile și apasă **Salvează sala**.")
        return

    nume_clean = (nume or "").strip()
    if not nume_clean:
        st.warning("Te rog să introduci numele sălii.")
        return

    sala = adauga_sala(nume=nume_clean, randuri=int(randuri), locuri_pe_rand=int(locuri))
    st.success(f"Sală adăugată: **{sala['nume']}**")
    _rerun()


def pagina_sterge_sala(is_admin: bool) -> None:
    st.header("🗑 Șterge sală")

    if not is_admin:
        st.error("Doar administratorul poate șterge săli.")
        return

    sali = incarca_sali()
    if not sali:
        st.info("Nu există săli înregistrate.")
        return

    sali.sort(key=lambda s: int(s["id_sala"]))
    opt_sala = st.selectbox("Alege sala", options=sali, format_func=_format_sala_label)

    st.warning("Atenție: la ștergere se vor șterge și filmele + rezervările asociate (CASCADE).")

    confirm = st.checkbox("Confirm că vreau să șterg definitiv această sală.")
    if st.button("Șterge definitiv", type="primary", disabled=not confirm):
        sterge_sala(opt_sala["id_sala"])
        st.success(f"Sala **{opt_sala['nume']}** a fost ștearsă.")
        _rerun()
