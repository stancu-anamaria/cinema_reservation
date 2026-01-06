import streamlit as st

from services.admin_service import incarca_filme, incarca_sali
from services.rezervari_service import (
    incarca_rezervari,
    sterge_rezervare,
    locuri_ocupate,
    creeaza_rezervare_multi,
    incarca_preturi_bilete,
)


def _gaseste_sala(sali: list[dict], sala_id: int) -> dict | None:
    for s in sali:
        if int(s["id_sala"]) == int(sala_id):
            return s
    return None


def _init_state():
    if "locuri_selectate" not in st.session_state:
        st.session_state["locuri_selectate"] = set()
    if "tip_bilet_per_loc" not in st.session_state:
        st.session_state["tip_bilet_per_loc"] = {}
    if "tip_bilet_default" not in st.session_state:
        st.session_state["tip_bilet_default"] = "Adult"
    if "numar_locuri_dorite" not in st.session_state:
        st.session_state["numar_locuri_dorite"] = 1


def _taie_selectia_la_n(n: int) -> bool:
    """
    Dacă user scade numărul de bilete, reducem selecția automat.
    Returnează True dacă a modificat selecția (ca să dăm rerun).
    """
    selectate = sorted(list(st.session_state["locuri_selectate"]))
    if len(selectate) <= n:
        return False

    de_scos = selectate[n:]
    for coord in de_scos:
        st.session_state["locuri_selectate"].discard(coord)
        if coord in st.session_state["tip_bilet_per_loc"]:
            del st.session_state["tip_bilet_per_loc"][coord]

    return True


def _toggle_loc_si_rerun(rand: int, loc: int, max_locuri: int):
    """
    Toggle loc + rerun imediat => UI nu mai rămâne "în urmă" (fix bug).
    """
    coord = (int(rand), int(loc))
    selectate = st.session_state["locuri_selectate"]

    if coord in selectate:
        selectate.remove(coord)
        if coord in st.session_state["tip_bilet_per_loc"]:
            del st.session_state["tip_bilet_per_loc"][coord]
        st.rerun()

    if len(selectate) >= int(max_locuri):
        st.warning(f"Ai ales deja {max_locuri} locuri. Deselectează unul ca să alegi altul.")
        return

    selectate.add(coord)
    st.session_state["tip_bilet_per_loc"][coord] = st.session_state["tip_bilet_default"]
    st.rerun()


def _deseneaza_harta_locuri_cu_culoar_gol(sala: dict, ocupate: set[tuple[int, int]], max_locuri: int):
    st.markdown("### 🗺️ Alege-ți locurile")
    st.caption("Legendă: 🟩 liber | 🟥 ocupat | ⭐ selectat | (spațiu) culoar")

    randuri = int(sala["randuri"])
    locuri_pe_rand = int(sala["locuri_pe_rand"])
    selectate = st.session_state["locuri_selectate"]

    st.markdown("#### 🎞️ ECRAN")
    st.markdown("---")

    index_culoar_dupa = locuri_pe_rand // 2
    numar_coloane = locuri_pe_rand + 1

    for r in range(1, randuri + 1):
        col_label, col_seats = st.columns([1, 12])

        with col_label:
            st.markdown(f"**R{r}**")

        with col_seats:
            cols = st.columns(numar_coloane)

            for l in range(1, locuri_pe_rand + 1):
                if l > index_culoar_dupa:
                    idx_col = l
                else:
                    idx_col = l - 1

                e_ocupat = (r, l) in ocupate
                e_selectat = (r, l) in selectate

                simbol = "⭐" if e_selectat else ("🟥" if e_ocupat else "🟩")

                if e_ocupat:
                    cols[idx_col].button(simbol, key=f"seat_{r}_{l}", disabled=True)
                else:
                    if cols[idx_col].button(simbol, key=f"seat_{r}_{l}"):
                        _toggle_loc_si_rerun(r, l, int(max_locuri))

            # culoar gol
            idx_culoar = index_culoar_dupa
            cols[idx_culoar].markdown("<div style='height:38px;'></div>", unsafe_allow_html=True)


def _calculeaza_total(preturi: dict[str, float]) -> float:
    total = 0.0
    for coord in st.session_state["locuri_selectate"]:
        tip = st.session_state["tip_bilet_per_loc"].get(coord, "Adult")
        total += float(preturi.get(tip, 0.0))
    return float(total)


def pagina_creeaza_rezervare():
    _init_state()
    st.header("🎟 Rezervare bilete")

    # doar logat
    if not st.session_state.get("logged_in", False):
        st.warning("Trebuie să te autentifici ca să poți face o rezervare.")
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

    opt_film = st.selectbox(
        "🎬 Alege filmul",
        options=filme,
        format_func=lambda f: f"[{f['id_film']}] {f['titlu']}",
    )

    film_id = int(opt_film["id_film"])
    sala_id = int(opt_film["sala_id"])
    sala = _gaseste_sala(sali, sala_id)

    if not sala:
        st.error("Filmul are o sală asociată invalidă. Verifică datele din DB.")
        return

    ocupate = locuri_ocupate(film_id, sala_id)

    total_locuri = int(sala["randuri"]) * int(sala["locuri_pe_rand"])
    libere = total_locuri - len(ocupate)

    st.info(
        f"🏢 Sala: **{sala['nume']}** | "
        f"Dimensiune: {sala['randuri']}×{sala['locuri_pe_rand']} | "
        f"Locuri libere: **{libere}** / {total_locuri}"
    )

    # număr bilete (cu key stabil)
    numar_bilete = st.number_input(
        "🎫 Câte locuri vrei să rezervi?",
        min_value=1,
        max_value=max(1, libere),
        step=1,
        value=int(st.session_state["numar_locuri_dorite"]),
        key="numar_locuri_dorite",
    )

    # dacă user a scăzut, tăiem selecția și dăm rerun
    if _taie_selectia_la_n(int(numar_bilete)):
        st.rerun()

    st.session_state["tip_bilet_default"] = st.selectbox(
        "👥 Tip bilet (default pentru locurile noi selectate)",
        options=list(preturi.keys()),
        index=list(preturi.keys()).index(st.session_state["tip_bilet_default"])
        if st.session_state["tip_bilet_default"] in preturi
        else 0,
        key="tip_bilet_default_select",
    )

    st.markdown("---")

    _deseneaza_harta_locuri_cu_culoar_gol(sala, ocupate, int(numar_bilete))

    st.markdown("---")
    st.subheader("✅ Selecția ta")

    locuri_selectate = sorted(list(st.session_state["locuri_selectate"]))
    st.write(f"Ai selectat **{len(locuri_selectate)} / {int(numar_bilete)}** locuri.")

    if st.button("🧹 Golește selecția"):
        st.session_state["locuri_selectate"] = set()
        st.session_state["tip_bilet_per_loc"] = {}
        st.rerun()

    if not locuri_selectate:
        st.info("Selectează locurile din hartă (🟩).")
        return

    st.markdown("### 🎟 Tip bilet pe fiecare loc")
    for (r, l) in locuri_selectate:
        key_tip = f"tip_{r}_{l}"
        tip_curent = st.session_state["tip_bilet_per_loc"].get((r, l), st.session_state["tip_bilet_default"])

        tip_nou = st.selectbox(
            f"R{r} L{l}",
            options=list(preturi.keys()),
            index=list(preturi.keys()).index(tip_curent) if tip_curent in preturi else 0,
            key=key_tip,
        )
        st.session_state["tip_bilet_per_loc"][(r, l)] = tip_nou

    total = _calculeaza_total(preturi)
    st.markdown("### 💰 Total")
    st.success(f"{total:.2f} RON")

    st.markdown("### 💳 Plată")
    st.info("Plata se face **doar la casierie** (în aplicație nu există plată cu cardul).")

    st.markdown("---")

    username = st.session_state.get("username")

    if len(locuri_selectate) != int(numar_bilete):
        st.warning("Selectează exact numărul de locuri dorit (sau schimbă numărul de bilete).")
        return

    if st.button("✅ Confirmă rezervarea"):
        try:
            id_rez = creeaza_rezervare_multi(
                film_id=film_id,
                sala_id=sala_id,
                locuri_selectate=locuri_selectate,
                tip_bilet_per_loc=dict(st.session_state["tip_bilet_per_loc"]),
                username=str(username),
            )

            st.success(f"Rezervarea a fost creată cu succes! (ID: {id_rez}) ✅")
            st.info("Recomandare: vino cu **cel puțin 30 de minute mai devreme** ca să ridici și să plătești biletele la casierie.")

            st.session_state["locuri_selectate"] = set()
            st.session_state["tip_bilet_per_loc"] = {}
            st.rerun()

        except ValueError as e:
            st.error(str(e))


def pagina_anuleaza_rezervare(is_admin: bool):
    st.header("❌ Anulează rezervare")

    if not is_admin:
        st.error("Doar administratorul poate anula rezervări.")
        return

    rezervari = incarca_rezervari(username=None, is_admin=True)
    if not rezervari:
        st.info("Nu există rezervări înregistrate.")
        return

    opt = st.selectbox(
        "Alege rezervarea",
        options=rezervari,
        format_func=lambda r: f"ID {r['id_rezervare']} | user {r['username']} | total {r['total']:.2f} RON",
    )

    if st.button("Anulează rezervarea selectată"):
        sterge_rezervare(opt["id_rezervare"])
        st.success("Rezervarea a fost anulată.")
        st.rerun()


def pagina_vizualizare_rezervari(is_admin: bool):
    st.header("📋 Biletele mele")

    if not st.session_state.get("logged_in", False):
        st.warning("Autentifică-te ca să îți vezi biletele.")
        return

    username = st.session_state.get("username")
    rezervari = incarca_rezervari(username=username, is_admin=is_admin)

    if not rezervari:
        st.info("Nu ai rezervări încă.")
        return

    for r in rezervari:
        locuri = r.get("locuri", [])
        locuri_str = ", ".join([f"R{l['rand']} L{l['loc']} ({l['tip_bilet']})" for l in locuri])

        st.markdown(f"### 🎫 Rezervare #{r['id_rezervare']}")
        st.write(f"Film ID: **{r['film_id']}** | Sală ID: **{r['sala_id']}**")
        st.write(f"Locuri: {locuri_str}")
        st.write(f"Total: **{r['total']:.2f} RON**")
        st.caption(f"Utilizator: {r['username']} | Data: {r.get('created_at', '-')}")
        st.info("Vino cu **cel puțin 30 de minute mai devreme** ca să ridici și să plătești biletele la casierie.")
        st.markdown("---")
