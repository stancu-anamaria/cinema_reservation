# path: interface/rezervari_ui.py
from __future__ import annotations

import streamlit as st

from services.admin_service import incarca_filme, incarca_sali
from services.rezervari_service import (
    incarca_rezervari,
    sterge_rezervare,
    locuri_ocupate,
    creeaza_rezervare_multi,
    incarca_preturi_bilete,
)


# ----------------- HELPERS UI -----------------

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
    sm = _time_to_minutes(start_time)
    if sm is None:
        return str(start_time)
    em = sm + int(durata_min)
    return f"{_minutes_to_time(sm)} – {_minutes_to_time(em)}"


def _gaseste_sala(sali: list[dict], sala_id: int) -> dict | None:
    for s in sali:
        if int(s["id_sala"]) == int(sala_id):
            return s
    return None


def _init_state() -> None:
    st.session_state.setdefault("locuri_selectate", set())
    st.session_state.setdefault("tip_bilet_per_loc", {})
    st.session_state.setdefault("tip_bilet_default", "Adult")
    st.session_state.setdefault("numar_locuri_dorite", 1)


def _taie_selectia_la_n(n: int) -> bool:
    selectate = sorted(list(st.session_state["locuri_selectate"]))
    if len(selectate) <= n:
        return False

    de_scos = selectate[n:]
    for coord in de_scos:
        st.session_state["locuri_selectate"].discard(coord)
        st.session_state["tip_bilet_per_loc"].pop(coord, None)

    return True


def _toggle_loc(rand: int, loc: int, max_locuri: int) -> None:
    coord = (int(rand), int(loc))
    selectate: set[tuple[int, int]] = st.session_state["locuri_selectate"]

    # deselect
    if coord in selectate:
        selectate.remove(coord)
        st.session_state["tip_bilet_per_loc"].pop(coord, None)
        st.rerun()

    # limit
    if len(selectate) >= int(max_locuri):
        st.warning(f"Ai ales deja {max_locuri} locuri. Deselectează unul ca să alegi altul.")
        return

    # select
    selectate.add(coord)
    st.session_state["tip_bilet_per_loc"][coord] = st.session_state["tip_bilet_default"]
    st.rerun()


def _deseneaza_harta_locuri(sala: dict, ocupate: set[tuple[int, int]], max_locuri: int) -> None:
    st.subheader("🗺️ Alege-ți locurile")
    st.caption("Legendă: 🟩 liber | 🟥 ocupat | ⭐ selectat | (spațiu) culoar")

    randuri = int(sala["randuri"])
    locuri_pe_rand = int(sala["locuri_pe_rand"])
    selectate: set[tuple[int, int]] = st.session_state["locuri_selectate"]

    st.write("🎞️ **ECRAN**")
    st.divider()

    index_culoar_dupa = locuri_pe_rand // 2
    numar_coloane = locuri_pe_rand + 1

    for r in range(1, randuri + 1):
        col_label, col_seats = st.columns([1, 12])

        with col_label:
            st.write(f"**R{r}**")

        with col_seats:
            cols = st.columns(numar_coloane)

            for l in range(1, locuri_pe_rand + 1):
                idx_col = l - 1
                if l > index_culoar_dupa:
                    idx_col += 1

                e_ocupat = (r, l) in ocupate
                e_selectat = (r, l) in selectate

                simbol = "⭐" if e_selectat else ("🟥" if e_ocupat else "🟩")

                if e_ocupat:
                    cols[idx_col].button(simbol, key=f"seat_{r}_{l}", disabled=True)
                else:
                    if cols[idx_col].button(simbol, key=f"seat_{r}_{l}"):
                        _toggle_loc(r, l, int(max_locuri))

            cols[index_culoar_dupa].write("")


def _calculeaza_total(preturi: dict[str, float]) -> float:
    total = 0.0
    for coord in st.session_state["locuri_selectate"]:
        tip = st.session_state["tip_bilet_per_loc"].get(coord, "Adult")
        total += float(preturi.get(tip, 0.0))
    return float(total)


# ----------------- PAGES -----------------

def pagina_creeaza_rezervare() -> None:
    _init_state()
    st.header("🎟 Rezervare bilete")

    # obligatoriu logat (NU vizitator)
    if not st.session_state.get("logged_in", False):
        st.warning("Trebuie să te autentifici ca să poți face o rezervare.")
        return

    if str(st.session_state.get("username", "")).strip().lower() == "vizitator":
        st.warning("Pentru a face o rezervare, te rog autentifică-te cu un cont (nu ca vizitator).")
        return

    filme = incarca_filme()
    sali = incarca_sali()
    preturi = incarca_preturi_bilete()

    if not filme:
        st.info("Nu există filme. Cere administratorului să adauge un film.")
        return
    if not sali:
        st.info("Nu există săli. Cere administratorului să adauge o sală.")
        return

    # 1) clientul alege "proiecția" (adică film + sală + interval/oră)
    proiectii = []
    for f in filme:
        sala = _gaseste_sala(sali, int(f["sala_id"]))
        sala_nume = sala["nume"] if sala else "Sala"
        start = (f.get("start_time") or "").strip()
        durata = int(f.get("durata", 0) or 0)

        interval = _format_interval(start, durata) if start else "fără oră"
        label = f"🎬 {f.get('titlu','-')}  |  🏢 {sala_nume}  |  🕒 {interval}  |  ⏱ {durata} min"

        proiectii.append(
            {
                "label": label,
                "film_id": int(f["id_film"]),
                "sala_id": int(f["sala_id"]),
                "titlu": f.get("titlu", "-"),
                "sala_nume": sala_nume,
                "start_time": start or None,
                "durata": durata,
            }
        )

    # sort frumos (după titlu, apoi oră)
    def sort_key(p: dict):
        stt = _time_to_minutes(p.get("start_time") or "") or 10**9
        return (str(p.get("titlu", "")).lower(), str(p.get("sala_nume", "")).lower(), stt)

    proiectii.sort(key=sort_key)

    opt_proj = st.selectbox(
        "🎬 Alege proiecția (film + sală + interval)",
        options=proiectii,
        format_func=lambda p: p["label"],
    )

    film_id = int(opt_proj["film_id"])
    sala_id = int(opt_proj["sala_id"])
    sala = _gaseste_sala(sali, sala_id)

    if not sala:
        st.error("Proiecția are o sală asociată invalidă. Verifică datele din DB.")
        return

    ocupate = locuri_ocupate(film_id, sala_id)

    total_locuri = int(sala["randuri"]) * int(sala["locuri_pe_rand"])
    libere = total_locuri - len(ocupate)

    st.info(
        f"🎬 **{opt_proj['titlu']}** | 🏢 **{opt_proj['sala_nume']}** | "
        f"🕒 **{_format_interval(opt_proj.get('start_time'), opt_proj.get('durata')) if opt_proj.get('start_time') else 'fără oră'}**\n\n"
        f"Locuri libere: **{libere}** / {total_locuri}"
    )

    if libere <= 0:
        st.error("Nu mai există locuri disponibile pentru această proiecție.")
        return

    max_bilete = max(1, libere)

    st.session_state["numar_locuri_dorite"] = int(
        min(max(1, int(st.session_state["numar_locuri_dorite"])), max_bilete)
    )

    numar_bilete = st.number_input(
        "🎫 Câte locuri vrei să rezervi?",
        min_value=1,
        max_value=max_bilete,
        step=1,
        key="numar_locuri_dorite",
    )

    if _taie_selectia_la_n(int(numar_bilete)):
        st.rerun()

    tip_default = st.selectbox(
        "👥 Tip bilet (default pentru locurile noi selectate)",
        options=list(preturi.keys()),
        index=list(preturi.keys()).index(st.session_state["tip_bilet_default"])
        if st.session_state["tip_bilet_default"] in preturi
        else 0,
    )
    st.session_state["tip_bilet_default"] = tip_default

    st.divider()
    _deseneaza_harta_locuri(sala, ocupate, int(numar_bilete))

    st.divider()
    st.subheader("✅ Selecția ta")

    locuri_selectate = sorted(list(st.session_state["locuri_selectate"]))
    st.write(f"Ai selectat **{len(locuri_selectate)} / {int(numar_bilete)}** locuri.")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🧹 Golește selecția"):
            st.session_state["locuri_selectate"] = set()
            st.session_state["tip_bilet_per_loc"] = {}
            st.rerun()

    if not locuri_selectate:
        st.info("Selectează locurile din hartă (🟩).")
        return

    st.write("### 🎟 Tip bilet pe fiecare loc")
    for (r, l) in locuri_selectate:
        tip_curent = st.session_state["tip_bilet_per_loc"].get(
            (r, l),
            st.session_state["tip_bilet_default"],
        )

        tip_nou = st.selectbox(
            f"R{r} L{l}",
            options=list(preturi.keys()),
            index=list(preturi.keys()).index(tip_curent) if tip_curent in preturi else 0,
            key=f"tip_{r}_{l}",
        )
        st.session_state["tip_bilet_per_loc"][(r, l)] = tip_nou

    total = _calculeaza_total(preturi)
    st.success(f"💰 Total: **{total:.2f} RON**")
    st.info("💳 Plata se face **doar la casierie**. (Nu există plată cu cardul în aplicație.)")

    st.divider()
    st.subheader("🧾 Date pentru rezervare")

    nume_client = st.text_input("Nume și prenume (pentru identificare la ridicare)")
    telefon = st.text_input("Număr de telefon")

    st.info(
        "📌 La ridicarea biletelor, **persoana care a făcut rezervarea** trebuie să prezinte "
        "**un act de identitate** și **numărul de telefon** folosit."
    )

    if len(locuri_selectate) != int(numar_bilete):
        st.warning("Selectează exact numărul de locuri dorit (sau schimbă numărul de bilete).")
        return

    if st.button("✅ Confirmă rezervarea"):
        try:
            username = str(st.session_state.get("username"))

            id_rez = creeaza_rezervare_multi(
                film_id=film_id,
                sala_id=sala_id,
                locuri_selectate=locuri_selectate,
                tip_bilet_per_loc=dict(st.session_state["tip_bilet_per_loc"]),
                username=username,
                nume_client=nume_client,
                telefon=telefon,
            )

            st.success(f"✅ Rezervarea a fost creată! **ID rezervare: {id_rez}**")
            st.info("⏰ Recomandare: vino cu **cel puțin 30 de minute mai devreme** ca să ridici și să plătești biletele.")

            st.session_state["locuri_selectate"] = set()
            st.session_state["tip_bilet_per_loc"] = {}
            st.rerun()

        except ValueError as e:
            st.error(str(e))


def pagina_anuleaza_rezervare(is_admin: bool) -> None:
    st.header("❌ Anulează rezervare")

    if not is_admin:
        st.error("Doar administratorul poate anula rezervări.")
        return

    rezervari = incarca_rezervari(username=None, is_admin=True)
    if not rezervari:
        st.info("Nu există rezervări înregistrate.")
        return

    def label(r: dict) -> str:
        film = r.get("film_titlu") or "Film"
        sala = r.get("sala_nume") or "Sala"
        interval = _format_interval(r.get("film_start_time"), r.get("film_durata"))
        nume = r.get("nume_client") or "-"
        total = float(r.get("total", 0.0))
        telefon = r.get("telefon") or "-"
        return f"👤 {nume} ({telefon})  |  🎬 {film}  |  🏢 {sala}  |  🕒 {interval}  |  💰 {total:.2f} RON"

    opt = st.selectbox("Alege rezervarea", options=rezervari, format_func=label)

    st.warning("La anulare, locurile se eliberează imediat.")
    if st.button("🗑 Anulează rezervarea selectată"):
        sterge_rezervare(opt["id_rezervare"])
        st.success("Rezervarea a fost anulată. Locurile sunt acum libere.")
        st.rerun()


def pagina_vizualizare_rezervari(is_admin: bool) -> None:
    st.header("📋 Rezervări (admin)")

    if not is_admin:
        st.error("Doar administratorul poate vizualiza rezervările.")
        return

    rezervari = incarca_rezervari(username=None, is_admin=True)
    if not rezervari:
        st.info("Nu există rezervări.")
        return

    for r in rezervari:
        film = r.get("film_titlu") or "Film"
        sala = r.get("sala_nume") or "Sala"
        interval = _format_interval(r.get("film_start_time"), r.get("film_durata"))

        locuri = r.get("locuri", [])
        locuri_str = ", ".join([f"R{l['rand']} L{l['loc']} ({l['tip_bilet']})" for l in locuri])

        titlu_exp = f"🎫 {film} | 🏢 {sala} | 🕒 {interval} | Total {r['total']:.2f} RON"

        with st.expander(titlu_exp):
            st.write(f"Client: **{r.get('nume_client','-')}** | Telefon: **{r.get('telefon','-')}**")
            st.write(f"User: `{r.get('username','-')}` | Data: {r.get('created_at','-')}")
            st.write(f"Locuri: {locuri_str if locuri_str else '-'}")
            st.info("Plata se face la casierie. Recomandare: cu 30 min înainte.")
