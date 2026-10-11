import streamlit as st
from utils.supabase_client import supabase
from utils.auth import check_password
from config.employee_options import ERVARINGSNIVEAU, ROLLEN, CATEGORIEËN

st.set_page_config(page_title="Medewerkers", layout="wide")

# ---------------- AUTH CHECK ----------------
if not check_password():
    st.stop()

st.title("Medewerkersbeheer")

# Navigation
keuze = st.pills(
    "Acties",
    ["Aanmaken", "Overzicht", "Bewerken / Verwijderen"],
    default="Aanmaken",
)

# ============================================================
# 1️⃣ AANMAKEN — Koppel medewerker aan bestaande Supabase user
# ============================================================
if keuze == "Aanmaken":
    st.subheader("Nieuwe medewerker koppelen aan bestaande gebruiker")

    # Fetch existing Supabase Auth users
    users = supabase.rpc("get_all_users").execute().data or []

    if not users:
        st.warning("Er zijn nog geen gebruikers in Supabase Auth.")
        st.stop()

    # Select user
    email_to_id = {u["email"]: u["id"] for u in users}
    gekozen_user = st.selectbox("Kies een bestaande gebruiker", list(email_to_id.keys()))

    st.markdown("### Medewerkergegevens")

    with st.form("create_employee_form"):
        volledige_naam = st.text_input("Volledige naam")
        mobiel_nummer = st.text_input("Mobiel nummer")
        beschikbare_dagen = st.number_input("Beschikbare dagen", min_value=0, max_value=7)

        ervaringsniveau = st.selectbox("Ervaringsniveau", ERVARINGSNIVEAU)
        rol = st.selectbox("Rol", ROLLEN)
        categorie = st.selectbox("Categorie", CATEGORIEËN)

        submit = st.form_submit_button("Medewerker aanmaken")

        if submit:
            try:
                supabase.table("new_app_employees").insert({
                    "gebruiker_id": email_to_id[gekozen_user],
                    "volledige_naam": volledige_naam,
                    "email": gekozen_user,
                    "mobiel_nummer": mobiel_nummer,
                    "beschikbare_dagen": beschikbare_dagen,
                    "ervaringsniveau": ervaringsniveau,
                    "rol": rol,
                    "categorie": categorie
                }).execute()

                st.success("Medewerker succesvol aangemaakt en gekoppeld aan gebruiker.")

            except Exception as e:
                st.error(f"Fout bij aanmaken: {e}")

# ============================================================
# 2️⃣ OVERZICHT — Simpele lijst
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
# 3️⃣ BEWERKEN / VERWIJDEREN — Simpel beheer
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


