import streamlit as st
from utils.supabase_client import supabase
from utils.auth import check_password
from config.employee_options import ERVARINGSNIVEAU, ROLLEN, CATEGORIEËN

def medewerker_aanmaken():
    st.title("Nieuwe medewerker aanmaken")

    # ---------------- AUTH CHECK ----------------
    if not check_password():
        st.stop()

    # ---------------- FORM ----------------
    with st.form("create_employee_form"):
        volledige_naam = st.text_input("Volledige naam")
        email = st.text_input("Email")
        wachtwoord = st.text_input("Wachtwoord", type="password")
        mobiel_nummer = st.text_input("Mobiel nummer")
        beschikbare_dagen = st.number_input("Beschikbare dagen", min_value=0, max_value=7)

        ervaringsniveau = st.selectbox("Ervaringsniveau", ERVARINGSNIVEAU)
        rol = st.selectbox("Rol", ROLLEN)
        categorie = st.selectbox("Categorie", CATEGORIEËN)

        submit = st.form_submit_button("Aanmaken")

        if submit:
            try:
                # 1. Create Supabase Auth user
                res = supabase.auth.sign_up({
                    "email": email,
                    "password": wachtwoord,
                    "options": {
                        "data": {
                            "volledige_naam": volledige_naam,
                            "rol": rol,
                            "categorie": categorie
                        }
                    }
                })

                gebruiker_id = res.user.id

                # 2. Insert employee record
                supabase.table("new_app_employees").insert({
                    "gebruiker_id": gebruiker_id,
                    "volledige_naam": volledige_naam,
                    "email": email,
                    "mobiel_nummer": mobiel_nummer,
                    "beschikbare_dagen": beschikbare_dagen,
                    "ervaringsniveau": ervaringsniveau,
                    "rol": rol,
                    "categorie": categorie
                }).execute()

                st.success("Medewerker en account succesvol aangemaakt.")

            except Exception as e:
                st.error(f"Fout bij aanmaken: {e}")

    if st.button("⬅️ Terug naar menu"):
        st.switch_page("Home.py")

medewerker_aanmaken()

