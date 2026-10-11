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
                "categorie": categorie,
                "wachtwoord":password
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

        # Nieuw: wachtwoord wijzigen
        nieuw_wachtwoord = st.text_input("Nieuw wachtwoord (optioneel)", type="password")
        nieuw_wachtwoord_confirm = st.text_input("Bevestig nieuw wachtwoord", type="password")

        opslaan = st.form_submit_button("Opslaan")

        if opslaan:

            # --- Check wachtwoorden ---
            if nieuw_wachtwoord or nieuw_wachtwoord_confirm:
                if nieuw_wachtwoord != nieuw_wachtwoord_confirm:
                    st.error("De nieuwe wachtwoorden komen niet overeen.")
                    st.stop()

            update_data = {
                "volledige_naam": volledige_naam,
                "mobiel_nummer": mobiel_nummer,
                "beschikbare_dagen": beschikbare_dagen,
                "ervaringsniveau": ervaringsniveau,
                "rol": rol,
                "categorie": categorie
            }

            # --- Update wachtwoord in eigen tabel + Auth ---
            if nieuw_wachtwoord:
                update_data["wachtwoord"] = nieuw_wachtwoord

                # Update in Supabase Auth
                try:
                    supabase_admin.auth.admin.update_user(
                        medewerker["gebruiker_id"],
                        {"password": nieuw_wachtwoord}
                    )
                except Exception as e:
                    st.error(f"Kon wachtwoord niet updaten in Auth: {e}")
                    st.stop()

            # Update medewerker record
            supabase.table("new_app_employees").update(update_data).eq("id", medewerker["id"]).execute()

            st.success("Medewerker succesvol bijgewerkt.")
            st.rerun()

    # --- Verwijderen ---
    if st.button("Medewerker + gebruiker verwijderen"):
        try:
            # 1. Verwijder Supabase Auth gebruiker
            supabase_admin.auth.admin.delete_user(medewerker["gebruiker_id"])

            # 2. Verwijder medewerker uit eigen tabel
            supabase.table("new_app_employees").delete().eq("id", medewerker["id"]).execute()

            st.success("Gebruiker + medewerker volledig verwijderd.")
            st.rerun()

        except Exception as e:
            st.error(f"Fout bij verwijderen: {e}")



# ============================================================
# TERUG NAAR HOME
# ============================================================
st.button("⬅️ Terug naar Home", on_click=lambda: st.switch_page("Home.py"))



