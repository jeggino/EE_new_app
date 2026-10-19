import streamlit as st
from utils.auth import check_password
from utils.supabase_client import supabase
from utils.inventarisatie.survey_defaults import SURVEY_DEFAULTS
from utils.inventarisatie.save_inventarisatie import save_inventarisatie

from utils.inventarisatie.load_inventarisatie import load_inventarisatie
from utils.inventarisatie.update_inventarisatie import update_inventarisatie
from utils.inventarisatie.delete_inventarisatie import delete_inventarisatie

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
                "naam": naam if naam else "unknown",
                "email": email if email else "unknown",
                "telefoon": telefoon if telefoon else "unknown"
            }
        
        else:
            # No contact person → store unknown values
            klant_informatie["contactpersoon"] = {
                "naam": "unknown",
                "email": "unknown",
                "telefoon": "unknown"
            }


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

    from utils.inventarisatie.load_inventarisatie import load_inventarisatie
    from utils.inventarisatie.update_inventarisatie import update_inventarisatie
    from utils.inventarisatie.delete_inventarisatie import delete_inventarisatie

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

    new_geojson = draw_inventarisatie_geometry(
        key=f"edit_inv_map_{project_id}",
        existing_geometry=geometry
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
        klant_informatie["contactpersoon"] = {
            "naam": "unknown",
            "email": "unknown",
            "telefoon": "unknown"
        }

    # -----------------------------
    # 8. Save button
    # -----------------------------
    if st.button("Inventarisatie opslaan"):

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
            st.rerun()
        else:
            st.error(f"Fout bij opslaan: {error}")

    # -----------------------------
    # 9. Delete button
    # -----------------------------
    if st.button("Verwijder inventarisatie"):
        confirm = st.checkbox("Ik weet zeker dat ik dit project wil verwijderen.")
        if confirm:
            ok, err = delete_inventarisatie(project_id)
            if ok:
                st.success("Project verwijderd.")
                st.rerun()
            else:
                st.error(f"Fout bij verwijderen: {err}")

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

