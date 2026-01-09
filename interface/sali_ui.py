# path: interface/sali_ui.py
from __future__ import annotations

import streamlit as st

from services.admin_service import incarca_sali, adauga_sala, sterge_sala, incarca_filme


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


# ----------------- HELPERS ORĂ -----------------

def _time_to_minutes(hhmm: str) -> int | None:
    t = (hhmm or "").strip()
    if not t:
        return None

    parts = t.split(":")
    if len(parts) != 2:
        return None

    try:
        h = int(parts[0])
        m = int(parts[1])
    except ValueError:
        return None

    if h < 0 or h > 23 or m < 0 or m > 59:
        return None

    return h * 60 + m


def _minutes_to_time(total_min: int) -> str:
    total_min = int(total_min) % (24 * 60)
    h = total_min // 60
    m = total_min % 60
    return f"{h:02d}:{m:02d}"


def _format_interval(start_time: str | None, durata_min: int | None) -> str:
    if not start_time or durata_min is None:
        return "—"

    start_m = _time_to_minutes(start_time)
    if start_m is None:
        return str(start_time)

    end_m = start_m + int(durata_min)
    return f"{_minutes_to_time(start_m)} – {_minutes_to_time(end_m)}"


def _filme_in_sala(sala_id: int) -> list[dict]:
    filme = incarca_filme() or []
    filme = [f for f in filme if int(f.get("sala_id", 0)) == int(sala_id)]

    def sort_key(f: dict):
        stt = _time_to_minutes(str(f.get("start_time") or "")) or 10**9
        return (stt, int(f.get("id_film", 0)))

    filme.sort(key=sort_key)
    return filme


def _txt_or_dash(x: str | None) -> str:
    t = (x or "").strip()
    return t if t else "—"


# ----------------- PAGES -----------------

def pagina_vizualizare_sali() -> None:
    st.header("🏢 Săli disponibile")
    st.session_state.setdefault("sala_expand_id", None)

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
            if q in str(s.get("id_sala", "")).lower()
            or q in str(s.get("nume", "")).lower()
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
        sala_id = int(s["id_sala"])
        sala_nume = str(s["nume"])

        with st.container(border=True):
            top = st.columns([3, 1, 1, 1], vertical_alignment="center")
            with top[0]:
                st.markdown(f"### {sala_nume}")
                st.caption(f"Capacitate: {cap} locuri")

            top[1].metric("Rânduri", int(s["randuri"]))
            top[2].metric("Locuri/rând", int(s["locuri_pe_rand"]))
            top[3].metric("Total", cap)

            opened = (st.session_state.get("sala_expand_id") == sala_id)
            btn_label = "🎬 Ascunde programul" if opened else "🎬 Vezi programul"
            if st.button(btn_label, key=f"toggle_program_{sala_id}"):
                st.session_state["sala_expand_id"] = None if opened else sala_id
                _rerun()

            if opened:
                filme = _filme_in_sala(sala_id)

                st.markdown("#### 🎞 Program în această sală")

                if not filme:
                    st.info("Momentan nu este programat niciun film în această sală.")
                else:
                    # Header compact
                    h = st.columns([1.0, 3.0, 1.6, 1.2, 2.0, 2.0])
                    h[0].markdown("**Poster**")
                    h[1].markdown("**🎬 Film**")
                    h[2].markdown("**🕒 Interval**")
                    h[3].markdown("**⏱ Durată**")
                    h[4].markdown("**🔞 Clasificare**")
                    h[5].markdown("**✨ Tags**")
                    st.divider()

                    for f in filme:
                        titlu = f.get("titlu", "Fără titlu")
                        durata = int(f.get("durata", 0) or 0)
                        start_time = f.get("start_time", None)
                        interval = _format_interval(start_time, durata)

                        poster = f.get("poster", None)
                        rated = _txt_or_dash(f.get("rated"))
                        tags = _txt_or_dash(f.get("tags"))

                        row = st.columns([1.0, 3.0, 1.6, 1.2, 2.0, 2.0], vertical_alignment="center")

                        # Poster mic
                        with row[0]:
                            if poster:
                                # merge și cu URL (OMDb) și cu path local
                                st.image(poster, use_container_width=True)
                            else:
                                st.write("—")

                        row[1].write(titlu)
                        row[2].write(interval)
                        row[3].write(f"{durata} min" if durata else "—")
                        row[4].write(rated)
                        row[5].write(tags)

                        st.markdown(
                            "<div style='height: 8px'></div>",
                            unsafe_allow_html=True
                        )

                    st.divider()


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
