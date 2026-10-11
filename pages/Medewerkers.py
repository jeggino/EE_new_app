import streamlit as st
from utils.supabase_client import supabase


# Sidebar verbergen
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)


# ------------------ DATABASE FUNCTIES ------------------

def fetch_medewerkers():
    res = supabase.table("new_app_employees").select("*").order("aangemaakt_op", desc=True).execute()
    return res.data if res.data else []


def voeg_medewerker_toe(volledige_naam, email, mobiel_nummer, beschikbare_dagen, ervaringsniveau, rol, categorie):
    supabase.table("new_app_employees").insert({
        "volledige_naam": volledige_naam,
        "email": email,
        "mobiel_nummer": mobiel_nummer,
        "beschikbare_dagen": beschikbare_dagen,
        "ervaringsniveau": ervaringsniveau,
        "rol": rol,
        "categorie": categorie,
    }).execute()


def update_medewerker(medewerker_id, volledige_naam, email, mobiel_nummer, beschikbare_dagen, ervaringsniveau, rol, categorie):
    supabase.table("new_app_employees").update({
        "volledige_naam": volledige_naam,
        "email": email,
        "mobiel_nummer": mobiel_nummer,
        "beschikbare_dagen": beschikbare_dagen,
        "ervaringsniveau": ervaringsniveau,
        "rol": rol,
        "categorie": categorie,
    }).eq("id", medewerker_id).execute()


def verwijder_medewerker(medewerker_id):
    supabase.table("new_app_employees").delete().eq("id", medewerker_id).execute()


# ------------------ DASHBOARD ------------------

def medewerker_dashboard():
    st.title("Medewerker Dashboard")

    keuze = st.pills(
        "Acties",
        ["Overzicht", "Toevoegen", "Bewerken / Verwijderen"],
        default="Overzicht",
    )

    medewerkers = fetch_medewerkers()

    # ----------- OVERZICHT -----------
    if keuze == "Overzicht":
        st.subheader("Alle medewerkers")

        if not medewerkers:
            st.info("Er zijn nog geen medewerkers toegevoegd.")
            return

        st.dataframe(medewerkers, use_container_width=True, hide_index=True)

    # ----------- TOEVOEGEN -----------
    elif keuze == "Toevoegen":
        st.subheader("Nieuwe medewerker toevoegen")

        with st.form("toevoegen_form"):
            volledige_naam = st.text_input("Volledige naam")
            email = st.text_input("Email")
            mobiel_nummer = st.text_input("Mobiel nummer")
            beschikbare_dagen = st.number_input("Beschikbare dagen", min_value=0, max_value=7, value=5)
            ervaringsniveau = st.selectbox("Ervaringsniveau", ["junior", "intermediate", "senior", "expert"])
            rol = st.selectbox("Rol", ["gast", "gebruiker", "beheerder"])
            categorie = st.selectbox("Categorie", ["junior", "intermediate", "senior", "expert"])

            opslaan = st.form_submit_button("Opslaan")

            if opslaan:
                try:
                    voeg_medewerker_toe(
                        volledige_naam,
                        email,
                        mobiel_nummer,
                        beschikbare_dagen,
                        ervaringsniveau,
                        rol,
                        categorie,
                    )
                    st.success("Medewerker succesvol toegevoegd.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Fout bij toevoegen: {e}")

    # ----------- BEWERKEN / VERWIJDEREN -----------
    elif keuze == "Bewerken / Verwijderen":
        st.subheader("Medewerkers bewerken of verwijderen")

        if not medewerkers:
            st.info("Er zijn nog geen medewerkers om te bewerken.")
            return

        medewerker_map = {f"{m['volledige_naam']} ({m['email']})": m for m in medewerkers}
        keuze_label = st.selectbox("Kies een medewerker", list(medewerker_map.keys()))
        medewerker = medewerker_map[keuze_label]

        col1, col2 = st.columns(2)

        # ----- BEWERKEN -----
        with col1:
            st.markdown("### Gegevens bewerken")
            with st.form("bewerken_form"):
                volledige_naam = st.text_input("Volledige naam", value=medewerker["volledige_naam"])
                email = st.text_input("Email", value=medewerker["email"])
                mobiel_nummer = st.text_input("Mobiel nummer", value=medewerker.get("mobiel_nummer", ""))
                beschikbare_dagen = st.number_input(
                    "Beschikbare dagen",
                    min_value=0,
                    max_value=7,
                    value=medewerker.get("beschikbare_dagen", 5),
                )
                ervaringsniveau = st.selectbox(
                    "Ervaringsniveau",
                    ["junior", "intermediate", "senior", "expert"],
                    index=["junior", "intermediate", "senior", "expert"].index(medewerker.get("ervaringsniveau", "junior")),
                )
                rol = st.selectbox(
                    "Rol",
                    ["gast", "gebruiker", "beheerder"],
                    index=["gast", "gebruiker", "beheerder"].index(medewerker.get("rol", "gebruiker")),
                )
                categorie = st.selectbox(
                    "Categorie",
                    ["junior", "intermediate", "senior", "expert"],
                    index=["junior", "intermediate", "senior", "expert"].index(medewerker.get("categorie", "junior")),
                )

                opslaan = st.form_submit_button("Wijzigingen opslaan")

                if opslaan:
                    try:
                        update_medewerker(
                            medewerker["id"],
                            volledige_naam,
                            email,
                            mobiel_nummer,
                            beschikbare_dagen,
                            ervaringsniveau,
                            rol,
                            categorie,
                        )
                        st.success("Medewerker bijgewerkt.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Fout bij bijwerken: {e}")

        # ----- VERWIJDEREN -----
        with col2:
            st.markdown("### Verwijderen")
            st.warning("Let op: verwijderen is definitief.")
            if st.button("Medewerker verwijderen", type="primary"):
                try:
                    verwijder_medewerker(medewerker["id"])
                    st.success("Medewerker verwijderd.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Fout bij verwijderen: {e}")


if st.button("⬅️ Terug naar menu"):
    st.switch_page("Home.py")

medewerker_dashboard()
