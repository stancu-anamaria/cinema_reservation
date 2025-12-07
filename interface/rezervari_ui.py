import streamlit as st
from services.rezervari_service import (
    creeaza_rezervare,
    sterge_rezervare,
    incarca_rezervari,
)
from services.admin_service import (
    incarca_filme,
    incarca_sali,
)


def pagina_creeaza_rezervare():
    """Pagină pentru crearea unei rezervări (un singur loc / rezervare)."""
    st.header("🎟 Creează rezervare")

    filme = incarca_filme()
    sali = incarca_sali()

    if not filme:
        st.info("Nu există filme. Cere administratorului să adauge un film.")
        return
    if not sali:
        st.info("Nu există săli. Cere administratorului să adauge o sală.")
        return

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
        rezervare = creeaza_rezervare(
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


def pagina_anuleaza_rezervare(is_admin: bool):
    """Pagină pentru anularea unei rezervări (doar admin)."""
    st.header("❌ Anulează rezervare")

    if not is_admin:
        st.error("Doar administratorul poate anula rezervări.")
        return

    rezervari = incarca_rezervari()
    if not rezervari:
        st.info("Nu există rezervări înregistrate.")
        return

    opt_rez = st.selectbox(
        "Alege rezervarea",
        options=rezervari,
        format_func=lambda r: (
            f"ID {r['id_rezervare']} - Film {r['film_id']} | "
            f"Sală {r['sala_id']} | Rând {r.get('rand', '?')} Loc {r.get('loc', '?')}"
        )
    )

    if st.button("Anulează rezervare"):
        sterge_rezervare(opt_rez["id_rezervare"])
        st.success(f"Rezervarea cu ID {opt_rez['id_rezervare']} a fost anulată.")


def pagina_vizualizare_rezervari():
    """Pagină pentru vizualizarea tuturor rezervărilor."""
    st.header("📋 Rezervări existente")

    rezervari = incarca_rezervari()
    if not rezervari:
        st.info("Nu există rezervări înregistrate.")
        return

    with st.expander("Vezi lista de rezervări"):
        for r in rezervari:
            # suportă atât formatul vechi (rand/loc),
            # cât și un eventual format nou cu locuri multiple
            if "locuri" in r:
                locuri_str = ", ".join(
                    [f"Rând {l['rand']} Loc {l['loc']}" for l in r["locuri"]]
                )
            else:
                locuri_str = f"Rând {r.get('rand', '?')} Loc {r.get('loc', '?')}"

            st.write(
                f"ID rezervare: {r['id_rezervare']} | "
                f"Film ID: {r['film_id']} | "
                f"Sală ID: {r['sala_id']} | "
                f"{locuri_str}"
            )
            st.write("---")
