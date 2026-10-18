import streamlit as st
from utils.auth import check_password
from utils.supabase_client import supabase


# Geometry tools (we will create these next)
from utils.inventarisatie.geometry_tools_inventarisatie import (
    draw_inventarisatie_geometry,
    draw_inventarisatie_geometry_with_existing
)

# Hide sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)


# -----------------------------
# AUTHENTICATION
# -----------------------------
if check_password():

    col1, col2 = st.columns([2, 1])
    if col2.button("⬅️ Terug naar menu"):
        st.switch_page("Home.py")

    # -----------------------------
    # MAIN MENU
    # -----------------------------
    menu = st.pills(
        "Kies een onderdeel",
        default="Nieuwe Inventarisatie",
        selection_mode="single",
        options={
            "Nieuwe Inventarisatie": ":material/add_circle:",
            "Inventarisatie bewerken": ":material/edit:",
            "Inventarisatie bekijken": ":material/visibility:"
        }
    )

    # ============================================================
    # 1. NIEUWE INVENTARISATIE
    # ============================================================
    if menu == "Nieuwe Inventarisatie":

        st.header("Nieuwe Inventarisatie")

        # --- Draw geometry ---
        st.subheader("Teken het projectgebied")
        geojson = draw_inventarisatie_geometry(key="new_inv_map")

        # --- Basic project info ---
        st.subheader("Projectinformatie")

        project_naam = st.text_input("Projectnaam")
        project_beschrijving = st.text_area("Beschrijving")
        actief = st.toggle("Project actief?", value=True)

        # --- Users from new_app_employees ---
        resp = supabase.table("new_app_employees").select("id, volledige_naam, email").execute()
        employees = resp.data
        
        if not employees:
            st.warning("Geen medewerkers gevonden in 'new_app_employees'.")
            employee_labels = {}
        else:
            employee_labels = {
                emp["email"]: f"{emp['volledige_naam']} ({emp['email']})"
                for emp in employees
            }
        
        gebruikers = st.multiselect(
            "Gebruikers die toegang hebben tot dit project",
            options=list(employee_labels.keys()),
            format_func=lambda email: employee_labels[email],
            placeholder="Selecteer één of meerdere gebruikers"
        )



        # --- Survey info (JSON) ---
        st.subheader("Survey informatie")
        survey_informatie = st.text_area(
            "Survey informatie (JSON)",
            placeholder='{"type": "flora", "periode": "zomer"}'
        )

        # --- Client info (JSON) ---
        st.subheader("Klant informatie")
        klant_informatie = st.text_area(
            "Klant informatie (JSON)",
            placeholder='{"naam": "Gemeente X", "contact": "info@gemeente.nl"}'
        )

        # --- Save button ---
        if st.button("Inventarisatie opslaan"):

            if not geojson:
                st.error("Teken eerst een geometrie.")
                st.stop()

            if not project_naam:
                st.error("Voer een projectnaam in.")
                st.stop()

            st.success("Inventarisatie wordt opgeslagen…")

            # Placeholder — will be replaced by real function
            st.info("⚠️ save_inventarisatie() moet nog worden geïmplementeerd.")

    # ============================================================
    # 2. INVENTARISATIE BEWERKEN
    # ============================================================
    elif menu == "Inventarisatie bewerken":

        st.header("Inventarisatie bewerken")

        # Load list of projects
        resp = supabase.table("new_app_inventarisatie") \
            .select("id, project_naam, aangemaakt_op") \
            .order("aangemaakt_op", desc=True) \
            .execute()

        projecten = resp.data

        if not projecten:
            st.info("Geen inventarisaties gevonden.")
            st.stop()

        keuze = st.selectbox(
            "Kies een project:",
            options=projecten,
            format_func=lambda x: f"{x['project_naam']} ({x['aangemaakt_op'][:10]})"
        )

        project_id = keuze["id"]

        # Load full project
        project = supabase.table("new_app_inventarisatie") \
            .select("*") \
            .eq("id", project_id) \
            .single() \
            .execute().data

        # --- Load geometry from bucket ---
        geometry_path = f"inventarisatie/geometries/{project_id}.geojson"
        geometry_bytes = supabase.storage.from_("new_app").download(geometry_path)

        import json
        current_geojson = json.loads(geometry_bytes.decode("utf-8"))

        st.subheader("Geometrie bewerken")
        nieuwe_geojson = draw_inventarisatie_geometry_with_existing(
            current_geojson,
            key="edit_inv_map"
        )

        # --- Edit fields ---
        st.subheader("Projectinformatie")

        project_naam = st.text_input("Projectnaam", value=project["project_naam"])
        project_beschrijving = st.text_area("Beschrijving", value=project["project_beschrijving"])
        actief = st.toggle("Project actief?", value=project["actief"])

        gebruikers = st.text_input(
            "Gebruikers (komma gescheiden)",
            value=", ".join(project["gebruikers"]) if project["gebruikers"] else ""
        )

        survey_informatie = st.text_area(
            "Survey informatie (JSON)",
            value=json.dumps(project["survey_informatie"], indent=2)
        )

        klant_informatie = st.text_area(
            "Klant informatie (JSON)",
            value=json.dumps(project["klant_informatie"], indent=2)
        )

        # --- Save changes ---
        if st.button("Wijzigingen opslaan"):
            st.info("⚠️ update_inventarisatie() moet nog worden geïmplementeerd.")

        # --- Delete project ---
        if st.button("Verwijder project"):
            st.warning("⚠️ delete_inventarisatie() moet nog worden geïmplementeerd.")

    # ============================================================
    # 3. INVENTARISATIE BEKIJKEN
    # ============================================================
    elif menu == "Inventarisatie bekijken":

        st.header("Inventarisatie bekijken")

        resp = supabase.table("new_app_inventarisatie") \
            .select("id, project_naam, aangemaakt_op") \
            .order("aangemaakt_op", desc=True) \
            .execute()

        projecten = resp.data

        if not projecten:
            st.info("Geen inventarisaties beschikbaar.")
            st.stop()

        keuze = st.selectbox(
            "Kies een project:",
            options=projecten,
            format_func=lambda x: f"{x['project_naam']} ({x['aangemaakt_op'][:10]})"
        )

        project_id = keuze["id"]

        project = supabase.table("new_app_inventarisatie") \
            .select("*") \
            .eq("id", project_id) \
            .single() \
            .execute().data

        st.subheader("Projectinformatie")
        st.write(f"**Naam:** {project['project_naam']}")
        st.write(f"**Beschrijving:** {project['project_beschrijving']}")
        st.write(f"**Actief:** {'Ja' if project['actief'] else 'Nee'}")
        st.write(f"**Gebruikers:** {', '.join(project['gebruikers'])}")

        st.subheader("Survey informatie")
        st.json(project["survey_informatie"])

        st.subheader("Klant informatie")
        st.json(project["klant_informatie"])

        # Geometry preview
        st.subheader("Geometrie")
        st.info("⚠️ Kaartweergave moet nog worden geïmplementeerd.")

