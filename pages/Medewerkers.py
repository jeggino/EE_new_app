import streamlit as st
from utils.supabase_client import supabase, supabase_admin
from utils.auth import check_password
from config.employee_options import ERVARINGSNIVEAU, ROLLEN, CATEGORIEËN

# --- Hide sidebar ---
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# --- Auth check ---
if not check_password():
    st.stop()

st.title("Medewerkersbeheer")

# Navigation pills
keuze = st.pills(
    "Acties",
    ["Gebruiker + Medewerker aanmaken", "Overzicht", "Bewerken / Verwijderen"],
    default="Gebruiker + Medewerker aanmaken",
)

# ============================================================
# 1️⃣ GEBRUIKER + MEDEWERKER AANMAKEN
# ============================================================
if keuze == "Gebruiker + Medewerker aanmaken":
    st.subheader("Nieuwe gebruiker + medewerker aanmaken")

    with st.form("create_user_employee_form"):
        st.markdown("### Gebruiker")
        email = st.text_input("Email")

        password = st.text_input("Wachtwoord", type="password")
        password_confirm = st.text_input("Bevestig wachtwoord", type="password")

        st.markdown("### Medewerkergegevens")
        volledige_naam = st.text_input("Volledige naam")
        mobiel_nummer = st.text_input("Mobiel nummer")
        beschikbare_dagen = st.number_input("Beschikbare dagen", min_value=0, max_value=7)

        ervaringsniveau = st.selectbox("Ervaringsniveau", ERVARINGSNIVEAU)
        rol = st.selectbox("Rol", ROLLEN)
        categorie = st.selectbox("Categorie", CATEGORIEËN)

        submit = st.form_submit_button("Aanmaken")

    if submit:
        # --- Check wachtwoorden ---
        if password != password_confirm:
            st.error("De wachtwoorden komen niet overeen.")
            st.stop()

        try:
            # 1. Create Supabase Auth user (Admin API)
            res = supabase_admin.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {
                    "volledige_naam": volledige_naam,
                    "rol": rol,
                    "categorie": categorie
                }
            })

            user_id = res.user.id

            # 2. Create employee record
            supabase.table("new_app_employees").insert({
                "gebruiker_id": user_id,
                "volledige_naam": volledige_naam,
                "email": email,
                "mobiel_nummer": mobiel_nummer,
                "beschikbare_dagen": beschikbare_dagen,
                "ervaringsniveau": ervaringsniveau,
                "rol": rol,
                "categorie": categorie
            }).execute()

            st.success("Gebruiker + medewerker succesvol aangemaakt.")

        except Exception as e:
            st.error(f"Fout bij aanmaken: {e}")


# ============================================================
# 2️⃣ OVERZICHT
# ============================================================
elif keuze == "Overzicht":
    st.subheader("Medewerkers overzicht")

    res = supabase.table("new_app_employees").select("*").execute()
    medewerkers = res.data

    if not medewerkers:
        st.info("Er zijn nog geen medewerkers toegevoegd.")
        st.stop()

    st.dataframe(medewerkers, use_container_width=True, hide_index=True)

# ============================================================
# 3️⃣ BEWERKEN / VERWIJDEREN
# ============================================================
elif keuze == "Bewerken / Verwijderen":
    st.subheader("Medewerker bewerken of verwijderen")

    res = supabase.table("new_app_employees").select("*").execute()
    medewerkers = res.data

    if not medewerkers:
        st.info("Geen medewerkers beschikbaar.")
        st.stop()

    keuze_medewerker = st.selectbox(
        "Kies een medewerker",
        [f"{m['volledige_naam']} ({m['email']})" for m in medewerkers]
    )

    medewerker = next(m for m in medewerkers if f"{m['volledige_naam']} ({m['email']})" == keuze_medewerker)

    with st.form("edit_form"):
        volledige_naam = st.text_input("Volledige naam", medewerker["volledige_naam"])
        mobiel_nummer = st.text_input("Mobiel nummer", medewerker["mobiel_nummer"])
        beschikbare_dagen = st.number_input("Beschikbare dagen", min_value=0, max_value=7, value=medewerker["beschikbare_dagen"])

        ervaringsniveau = st.selectbox("Ervaringsniveau", ERVARINGSNIVEAU, index=ERVARINGSNIVEAU.index(medewerker["ervaringsniveau"]))
        rol = st.selectbox("Rol", ROLLEN, index=ROLLEN.index(medewerker["rol"]))
        categorie = st.selectbox("Categorie", CATEGORIEËN, index=CATEGORIEËN.index(medewerker["categorie"]))

        opslaan = st.form_submit_button("Opslaan")

        if opslaan:
            supabase.table("new_app_employees").update({
                "volledige_naam": volledige_naam,
                "mobiel_nummer": mobiel_nummer,
                "beschikbare_dagen": beschikbare_dagen,
                "ervaringsniveau": ervaringsniveau,
                "rol": rol,
                "categorie": categorie
            }).eq("id", medewerker["id"]).execute()

            st.success("Medewerker bijgewerkt.")
            st.rerun()

    if st.button("Medewerker verwijderen"):
        supabase.table("new_app_employees").delete().eq("id", medewerker["id"]).execute()
        st.success("Medewerker verwijderd.")
        st.rerun()

# ============================================================
# TERUG NAAR HOME
# ============================================================
st.button("⬅️ Terug naar Home", on_click=lambda: st.switch_page("Home.py"))



