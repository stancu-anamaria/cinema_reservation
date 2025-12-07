import streamlit as st
from services.admin_service import (
    incarca_sali,
    adauga_sala,
    sterge_sala,
)


def pagina_vizualizare_sali():
    st.header("🏢 Săli disponibile")

    sali = incarca_sali()

    if not sali:
        st.info("Nu există săli înregistrate încă.")
        return

    for s in sali:
        st.subheader(f"{s['nume']} (ID {s['id_sala']})")
        st.write(f"Rânduri: **{s['randuri']}**")
        st.write(f"Locuri pe rând: **{s['locuri_pe_rand']}**")
        st.write("---")


def pagina_adauga_sala(is_admin: bool):
    st.header("🏢 Adaugă sală")

    if not is_admin:
        st.error("Doar administratorul poate adăuga săli.")
        return

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


def pagina_sterge_sala(is_admin: bool):
    st.header("🗑 Șterge sală")

    if not is_admin:
        st.error("Doar administratorul poate șterge săli.")
        return

    sali = incarca_sali()
    if not sali:
        st.info("Nu există săli înregistrate.")
        return

    opt_sala = st.selectbox(
        "Alege sala de șters",
        options=sali,
        format_func=lambda s: f"[{s['id_sala']}] {s['nume']}"
    )

    st.warning(
        "Atenție! La ștergerea unei săli se vor șterge și filmele și "
        "rezervările asociate acesteia."
    )

    if st.button("Șterge sală definitiv"):
        sterge_sala(opt_sala["id_sala"])
        st.success(
            f"Sala '{opt_sala['nume']}' (ID {opt_sala['id_sala']}) a fost ștearsă."
        )
