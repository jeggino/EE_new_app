import streamlit as st
from utils.auth import check_password
from utils.supabase_client import supabase
from utils.inventarisatie.survey_defaults import SURVEY_DEFAULTS
from utils.inventarisatie.save_inventarisatie import save_inventarisatie
from utils.geometry_tools import draw_geometry_with_existing


from utils.inventarisatie.load_inventarisatie import load_inventarisatie
from utils.inventarisatie.update_inventarisatie import update_inventarisatie
from utils.inventarisatie.delete_inventarisatie import delete_inventarisatie

from utils.inventarisatie.helpers import get_full_name, load_geometry
from utils.inventarisatie.map_viewer import show_geometry_map

from utils.inventarisatie.info_renderer import render_survey_info, render_info_block



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


        # --- Draw geometry ---
        st.markdown("<h2 style='color:#2A8C55;'>Teken het projectgebied</h2>", unsafe_allow_html=True)
        geojson = draw_inventarisatie_geometry(key="new_inv_map")

        # --- Basic project info ---
        st.markdown("<h2 style='color:#2A8C55;'>Projectinformatie</h2>", unsafe_allow_html=True)

        project_naam = st.text_input("Projectnaam")
        project_beschrijving = st.text_area("Beschrijving",placeholder="Plak hier de relevante informatie uit de Quickscan: projectomschrijving, locatie, aanleiding en context.")
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
        st.markdown("<h2 style='color:#2A8C55;'>Survey informatie</h2>", unsafe_allow_html=True)
        
        survey_informatie = {}
        
        for soort, config in SURVEY_DEFAULTS.items():
        
            # MAIN SPECIES HEADER
            st.markdown(
                f"<h3 style='color:#1F4E79; margin-top:25px;'>{soort.capitalize()}</h3>",
                unsafe_allow_html=True
            )
        
            # ---------------------------------------------------------
            # 1. Toggle-based species (mussen/spreeuwen, gierzwaluwen)
            # ---------------------------------------------------------
            if config["type"] == "toggle_group":
                actief = st.toggle(
                    f"Is een survey nodig voor {soort}?",
                    value=config["default"],
                    key=f"{soort}_toggle"
                )
        
                if actief:
                    defaults = config["fields"]
                    fields = {}
        
                    fields["aantal_rondes"] = st.number_input(
                        f"Aantal rondes ({soort})",
                        min_value=0,
                        value=defaults["aantal_rondes"],
                        key=f"{soort}_rondes"
                    )
        
                    fields["aantal_personen"] = st.number_input(
                        f"Aantal personen ({soort})",
                        min_value=0,
                        value=defaults["aantal_personen"],
                        key=f"{soort}_personen"
                    )
        
                    fields["uren_per_survey"] = st.number_input(
                        f"Uren per survey ({soort})",
                        min_value=0,
                        value=defaults["uren_per_survey"],
                        key=f"{soort}_uren"
                    )
        
                    survey_informatie[soort] = fields
        
                else:
                    survey_informatie[soort] = None
        
            # ---------------------------------------------------------
            # 2. Multi-phase species WITH toggle (vleermuizen)
            # ---------------------------------------------------------
            elif config["type"] == "multi_phase_toggle":
                actief = st.toggle(
                    f"Is een survey nodig voor {soort}?",
                    value=config["default"],
                    key=f"{soort}_toggle"
                )
        
                if actief:
                    phases = {}
        
                    for fase, defaults in config["phases"].items():
        
                        # PHASE HEADER
                        st.markdown(
                            f"<h4 style='color:#6A1B9A; margin-left:20px;'>{fase.capitalize()}</h4>",
                            unsafe_allow_html=True
                        )
        
                        phases[fase] = {
                            "aantal_rondes": st.number_input(
                                f"Aantal rondes ({fase})",
                                min_value=0,
                                value=defaults["aantal_rondes"],
                                key=f"{soort}_{fase}_rondes"
                            ),
                            "aantal_personen": st.number_input(
                                f"Aantal personen ({fase})",
                                min_value=0,
                                value=defaults["aantal_personen"],
                                key=f"{soort}_{fase}_personen"
                            ),
                            "uren_per_survey": st.number_input(
                                f"Uren per survey ({fase})",
                                min_value=0,
                                value=defaults["uren_per_survey"],
                                key=f"{soort}_{fase}_uren"
                            )
                        }
        
                    survey_informatie[soort] = phases
        
                else:
                    survey_informatie[soort] = None



        # --- Client info (JSON) ---
        st.markdown("<h2 style='color:#2A8C55;'>Klant informatie</h2>", unsafe_allow_html=True)
        
        klant_informatie = {}
        
        # Ask if a contact person is needed
        heeft_contactpersoon = st.toggle(
            "Is er een contactpersoon?",
            value=False,
            key="heeft_contactpersoon"
        )
        
        if heeft_contactpersoon:
            st.markdown("<h4 style='color:#1F4E79;'>Contactpersoon</h4>", unsafe_allow_html=True)
        
            naam = st.text_input(
                "Naam contactpersoon",
                placeholder="Voor- en achternaam"
            )
        
            email = st.text_input(
                "E-mailadres contactpersoon",
                placeholder="naam@organisatie.nl"
            )
        
            telefoon = st.text_input(
                "Telefoonnummer contactpersoon",
                placeholder="06-12345678"
            )
        
            klant_informatie["contactpersoon"] = {
                "naam": naam if naam else "---",
                "email": email if email else "---",
                "telefoon": telefoon if telefoon else "---"
            }
        
        else:
            # No contact person → store unknown values
            klant_informatie["contactpersoon"] = None


        # --- Save button ---
        if st.button("Inventarisatie opslaan"):

            if not geojson:
                st.error("Teken eerst een geometrie.")
                st.stop()

            if not project_naam:
                st.error("Voer een projectnaam in.")
                st.stop()

            result = save_inventarisatie(
                project_naam,
                project_beschrijving,
                actief,
                gebruikers,
                survey_informatie,
                klant_informatie,
                geojson
            )
        
            if result["success"]:
                st.success(f"Project opgeslagen!")
            else:
                st.error(f"Fout bij opslaan: {result['error']}")

    # ============================================================
    # 2. INVENTARISATIE BEWERKEN
    # ============================================================
    elif menu == "Inventarisatie bewerken":
    
    
        st.header("Inventarisatie bewerken")
    
        # -----------------------------
        # 1. Year filter
        # -----------------------------
        years_resp = supabase.table("new_app_inventarisatie") \
            .select("id, project_naam, aangemaakt_op") \
            .execute()
    
        all_projects = years_resp.data
        
        if not all_projects:
            st.info("Geen inventarisaties gevonden.")
            st.stop()
    
        # Extract years
        years = sorted({p["aangemaakt_op"][:4] for p in all_projects})
    
        selected_year = st.selectbox("Selecteer jaar:", years)
    
        # Filter projects by year
        filtered = [p for p in all_projects if p["aangemaakt_op"].startswith(selected_year)]
    
        selected_project = st.selectbox(
            "Selecteer project:",
            filtered,
            format_func=lambda p: p["project_naam"]
        )
    
        project_id = selected_project["id"]
    
        # -----------------------------
        # 2. Load project
        # -----------------------------
        project, err = load_inventarisatie(project_id)
    
        if err:
            st.error(err)
            st.stop()
    
        meta = project["metadata"]
        geometry = project["geometry"]
    
        # -----------------------------
        # 3. Geometry editor
        # -----------------------------
        st.subheader("Geometrie")
    
        new_geojson = draw_geometry_with_existing(
            existing_geojson=geometry,
            key=f"edit_inv_map_{project_id}"
        )

        # -----------------------------
        # 4. Metadata fields
        # -----------------------------
        st.subheader("Projectinformatie")
    
        project_naam = st.text_input("Projectnaam", value=meta["project_naam"])
        project_beschrijving = st.text_area("Beschrijving", value=meta["project_beschrijving"])
        actief = st.toggle("Project actief?", value=meta["actief"])
    
        # -----------------------------
        # 5. Gebruikers
        # -----------------------------
        employees = supabase.table("new_app_employees").select("email, volledige_naam").execute().data
    
        employee_labels = {e["email"]: f"{e['volledige_naam']} ({e['email']})" for e in employees}
    
        gebruikers = st.multiselect(
            "Gebruikers",
            options=list(employee_labels.keys()),
            default=meta["gebruikers"],
            format_func=lambda email: employee_labels[email]
        )
    
        # -----------------------------
        # 6. Survey informatie (same UI as creation)
        # -----------------------------
        st.subheader("Survey informatie")
    
        survey_informatie = {}
        for soort, config in SURVEY_DEFAULTS.items():
    
            st.markdown(f"### {soort.capitalize()}")
    
            existing = meta["survey_informatie"].get(soort)
    
            if config["type"] == "toggle_group":
                actief_survey = st.toggle(
                    f"Survey nodig voor {soort}?",
                    value=(existing is not None)
                )
    
                if actief_survey:
                    fields = {}
                    defaults = config["fields"]
    
                    fields["aantal_rondes"] = st.number_input(
                        f"Aantal rondes ({soort})",
                        min_value=0,
                        value=existing["aantal_rondes"] if existing else defaults["aantal_rondes"]
                    )
    
                    fields["aantal_personen"] = st.number_input(
                        f"Aantal personen ({soort})",
                        min_value=0,
                        value=existing["aantal_personen"] if existing else defaults["aantal_personen"]
                    )
    
                    fields["uren_per_survey"] = st.number_input(
                        f"Uren per survey ({soort})",
                        min_value=0,
                        value=existing["uren_per_survey"] if existing else defaults["uren_per_survey"]
                    )
    
                    survey_informatie[soort] = fields
                else:
                    survey_informatie[soort] = None
    
            elif config["type"] == "multi_phase_toggle":
                actief_survey = st.toggle(
                    f"Survey nodig voor {soort}?",
                    value=(existing is not None)
                )
    
                if actief_survey:
                    phases = {}
                    for fase, defaults in config["phases"].items():
                        st.markdown(f"#### {fase.capitalize()}")
    
                        ex = existing.get(fase) if existing else None
    
                        phases[fase] = {
                            "aantal_rondes": st.number_input(
                                f"Aantal rondes ({fase})",
                                min_value=0,
                                value=ex["aantal_rondes"] if ex else defaults["aantal_rondes"]
                            ),
                            "aantal_personen": st.number_input(
                                f"Aantal personen ({fase})",
                                min_value=0,
                                value=ex["aantal_personen"] if ex else defaults["aantal_personen"]
                            ),
                            "uren_per_survey": st.number_input(
                                f"Uren per survey ({fase})",
                                min_value=0,
                                value=ex["uren_per_survey"] if ex else defaults["uren_per_survey"]
                            )
                        }
    
                    survey_informatie[soort] = phases
                else:
                    survey_informatie[soort] = None
    
        # -----------------------------
        # 7. Klant informatie
        # -----------------------------
        st.subheader("Klant informatie")
    
        existing_contact = meta["klant_informatie"]["contactpersoon"]
    
        heeft_contactpersoon = st.toggle(
            "Is er een contactpersoon?",
            value=(existing_contact["naam"] != "unknown")
        )
    
        klant_informatie = {}
    
        if heeft_contactpersoon:
            naam = st.text_input("Naam contactpersoon", value=existing_contact["naam"])
            email = st.text_input("Email contactpersoon", value=existing_contact["email"])
            telefoon = st.text_input("Telefoon contactpersoon", value=existing_contact["telefoon"])
    
            klant_informatie["contactpersoon"] = {
                "naam": naam,
                "email": email,
                "telefoon": telefoon
            }
        else:
            klant_informatie["contactpersoon"] = None
    
        # -----------------------------
        # 8. Save button
        # -----------------------------
        if st.button("Inventarisatie opslaan"):
            with st.spinner("..."):
        
                update_data = {
                    "project_naam": project_naam,
                    "project_beschrijving": project_beschrijving,
                    "actief": actief,
                    "gebruikers": gebruikers,
                    "survey_informatie": survey_informatie,
                    "klant_informatie": klant_informatie
                }
        
                success, error = update_inventarisatie(project_id, update_data, new_geojson)
        
                if success:
                    st.success("Inventarisatie bijgewerkt.")
        
                else:
                    st.error(f"Fout bij opslaan: {error}")


    


        # -----------------------------
        # Delete project
        # -----------------------------
        if "delete_confirm" not in st.session_state:
            st.session_state.delete_confirm = False
        
        # User clicks delete → show confirmation buttons immediately
        if st.button("Verwijder inventarisatie"):
            st.session_state.delete_confirm = True
        
        # Show confirmation buttons
        if st.session_state.delete_confirm:
        
            st.warning("Weet je zeker dat je dit project wilt verwijderen? Klik op **'Ja, verwijderen'** om te bevestigen.")
        
            col1, col2 = st.columns(2)
        
            if col1.button("Ja, verwijderen"):
                with st.spinner("Project wordt verwijderd..."):
                    success, err = delete_inventarisatie(project_id)
        
                if success:
                    st.success("Project verwijderd.")
                    st.session_state.delete_confirm = False
                    st.rerun()
                else:
                    st.error(f"Fout bij verwijderen: {err}")
        
            if col2.button("Nee, annuleren"):
                st.session_state.delete_confirm = False
                st.info("Verwijderen geannuleerd.")
                st.rerun()





    # ============================================================
    # 3. INVENTARISATIE BEKIJKEN
    # ============================================================
    elif menu == "Inventarisatie bekijken":
    
    
        st.header("Inventarisatie bekijken")
    
        # Load all projects
        resp = supabase.table("new_app_inventarisatie") \
            .select("id, project_naam, actief, aangemaakt_op") \
            .order("project_naam", desc=False) \
            .execute()
    
        projecten = resp.data
    
        if not projecten:
            st.info("Geen inventarisaties beschikbaar.")
            st.stop()
    
        # -----------------------------
        # Filters
        # -----------------------------
        st.subheader("Filters")
    
        # 1. Actief / Niet actief
        status_filter = st.radio(
            "Status:",
            ["Actief", "Niet actief"],
            horizontal=True
        )
        status_bool = True if status_filter == "Actief" else False
    
        projecten = [p for p in projecten if p["actief"] == status_bool]
    
        # 2. Year filter
        jaren = sorted({p["aangemaakt_op"][:4] for p in projecten})
        gekozen_jaar = st.selectbox("Jaar:", jaren)
    
        projecten = [p for p in projecten if p["aangemaakt_op"][:4] == gekozen_jaar]
    
        # 3. Project name (alphabetical)
        projecten = sorted(projecten, key=lambda x: x["project_naam"])
    
        keuze = st.selectbox(
            "Project:",
            options=projecten,
            format_func=lambda x: f"{x['project_naam']} ({x['aangemaakt_op'][:10]})"
        )

        # If nothing selected or project missing → stop
        if not keuze or "id" not in keuze:
            st.warning("Er is geen project beschikbaar om te bekijken.")
            st.stop()
        
    
        project_id = keuze["id"]
    
        # Load full project
        project = supabase.table("new_app_inventarisatie") \
            .select("*") \
            .eq("id", project_id) \
            .single() \
            .execute().data
    
        # Load geometry
        geometry = load_geometry(project_id)
    
        # -----------------------------
        # Layout
        # -----------------------------
        st.subheader("Geometrie")
        show_geometry_map(geometry, key=f"map_{project_id}")
    
        st.subheader("Projectinformatie")
    
    
        st.write(f"**Beschrijving:** {project['project_beschrijving']}")
    
        st.markdown("### Team")
        full_names = [get_full_name(email) for email in project["gebruikers"]]
        for name in full_names:
            st.write(f"- {name}")
    
        render_survey_info("Survey informatie", project["survey_informatie"])
        render_info_block("Klant informatie", project["klant_informatie"])



