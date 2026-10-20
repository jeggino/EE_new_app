import streamlit as st
from datetime import datetime, timedelta

from utils.auth import check_password
from utils.supabase_client import supabase
from utils.planing.protocols import PROTOCOLS
from utils.inventarisatie.helpers import get_full_name

from streamlit_calendar import calendar


# Verberg sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)


# Login check
if not check_password():
    st.stop()

col1, col2 = st.columns([2, 1])
# col1.title("Quickscan",text_alignment="center",)
if col2.button("⬅️ Terug naar menu"):
    st.switch_page("Home.py")
    
pagina = st.pills(
    "Navigatie",
    ["Plan een survey", "Agenda"],
    default="Plan een survey",
    # icons=["calendar_add_on", "calendar_month"]
)


if pagina == "Plan een survey":
    # ---------------------------------------------------------
    # 1. Laad actieve projecten
    # ---------------------------------------------------------
    projecten = supabase.table("new_app_inventarisatie") \
        .select("id, project_naam, aangemaakt_op, survey_informatie, gebruikers") \
        .eq("actief", True) \
        .execute().data

    if not projecten:
        st.info("Er zijn geen actieve projecten om te plannen.")
        st.stop()

    # ---------------------------------------------------------
    # 1b. Laad alle medewerkers
    # ---------------------------------------------------------
    employees = supabase.table("new_app_employees") \
        .select("email, volledige_naam") \
        .execute().data

    if not employees:
        st.error("Er zijn geen medewerkers beschikbaar.")
        st.stop()

    email_to_name = {e["email"]: e["volledige_naam"] for e in employees}
    alle_emails = list(email_to_name.keys())

    # ---------------------------------------------------------
    # 2. Kies project
    # ---------------------------------------------------------
    keuze = st.selectbox(
        "Kies een project:",
        options=projecten,
        format_func=lambda p: f"{p['project_naam']} ({p['aangemaakt_op'][:10]})"
    )

    project_id = keuze["id"]
    survey_info = keuze["survey_informatie"]

    # ---------------------------------------------------------
    # 3. Kies soort + surveytype
    # ---------------------------------------------------------    
    # Filter soorten die null zijn
    soorten = [s for s, v in survey_info.items() if v is not None]
    gekozen_soort = st.selectbox("Soort:", soorten)
        
    value = survey_info[gekozen_soort]
    
    # Filter subtypes die null zijn
    if isinstance(value, dict):
        value = {k: v for k, v in value.items() if v is not None}
    
    if isinstance(value, dict) and all(isinstance(v, dict) for v in value.values()):
        # soort heeft subassignments
        surveytypes = list(value.keys())
        gekozen_surveytype = st.selectbox("Surveytype:", surveytypes)
        survey_details = value[gekozen_surveytype]
        subassignment = gekozen_surveytype
    else:
        # soort heeft GEEN subassignments
        gekozen_surveytype = "algemeen"
        survey_details = value
        subassignment = ""


    aantal_personen = survey_details["aantal_personen"]

    # ---------------------------------------------------------
    # 4. Kies datum
    # ---------------------------------------------------------
    datum = st.date_input("Datum van de survey")

    # ---------------------------------------------------------
    # 5. Kies veldwerkers (uit new_app_employees)
    # ---------------------------------------------------------
    geselecteerde_werkers = st.multiselect(
        "Kies veldwerkers:",
        options=alle_emails,
        format_func=lambda e: email_to_name[e]
    )

    if len(geselecteerde_werkers) != aantal_personen:
        st.error(f"Je moet precies **{aantal_personen}** veldwerkers kiezen.")
        st.stop()

    # ---------------------------------------------------------
    # 6. Protocolvalidatie
    # ---------------------------------------------------------
    soort = gekozen_soort.lower()
    surveytype = gekozen_surveytype.lower()

    regels = None

    if soort in PROTOCOLS:
        if subassignment and subassignment.lower() in PROTOCOLS[soort]:
            regels = PROTOCOLS[soort][subassignment.lower()]
        elif "algemeen" in PROTOCOLS[soort]:
            regels = PROTOCOLS[soort]["algemeen"]

    if regels:
        min_dagen = regels["min_dagen_tussen_surveys"]
        verplichte_maand = regels["verplichte_maand_derde_survey"]

        eerdere_surveys = supabase.table("new_app_planning") \
            .select("*") \
            .eq("project_naam", keuze["project_naam"]) \
            .eq("assignment", gekozen_soort) \
            .execute().data

        if eerdere_surveys:
            laatste_datum = max([datetime.fromisoformat(s["datum"]) for s in eerdere_surveys])
            verschil = (datum - laatste_datum.date()).days

            if verschil < min_dagen:
                st.error(
                    f"Volgens het protocol moeten er minimaal **{min_dagen} dagen** tussen deze surveys zitten."
                )
                st.stop()

        if verplichte_maand and len(eerdere_surveys) == 2:
            if datum.month != verplichte_maand:
                maandnaam = ["januari","februari","maart","april","mei","juni",
                             "juli","augustus","september","oktober","november","december"][verplichte_maand-1]
                st.error(
                    f"De derde survey moet volgens protocol in **{maandnaam}** plaatsvinden."
                )
                st.stop()

    # ---------------------------------------------------------
    # 7. Opslaan
    # ---------------------------------------------------------
    if st.button("Survey plannen"):
        user = st.session_state.get("user")
        aangemaakt_door = user.user_metadata.get("volledige_naam", user.email)

        supabase.table("new_app_planning").insert({
            "project_naam": keuze["project_naam"],
            "assignment": gekozen_soort,
            "subassignment": subassignment,
            "datum": str(datum),
            "veldwerkers": geselecteerde_werkers,
            "aangemaakt_door": aangemaakt_door
        }).execute()

        st.success("Survey succesvol gepland!")


elif pagina == "Agenda":
    st.header("Agenda-overzicht")

    # Haal alle geplande surveys op
    planning = supabase.table("new_app_planning") \
        .select("*") \
        .order("datum") \
        .execute().data

    if not planning:
        st.info("Er zijn nog geen geplande surveys.")
        st.stop()

    # ------------------------------------------
    # Filters: project of veldwerker
    # ------------------------------------------
    filter_type = st.radio(
        "Filter op:",
        ["Project", "Veldwerker"],
        horizontal=True
    )

    if filter_type == "Project":
        projecten = sorted(list({p["project_naam"] for p in planning}))
        gekozen_project = st.selectbox("Kies een project:", projecten)
        gefilterd = [p for p in planning if p["project_naam"] == gekozen_project]

    else:
        alle_werkers = sorted(list({w for p in planning for w in p["veldwerkers"]}))
        gekozen_werker = st.selectbox("Kies een veldwerker:", alle_werkers)
        gefilterd = [p for p in planning if gekozen_werker in p["veldwerkers"]]

    # ------------------------------------------
    # Kalenderweergave
    # ------------------------------------------
    from streamlit_calendar import calendar

    events = []

    for item in gefilterd:
        events.append({
            "title": f"{item['assignment']} ({item['subassignment'] or 'algemeen'})",
            "start": item["datum"],
            "end": item["datum"],
            "extendedProps": {
                "project": item["project_naam"],
                "veldwerkers": ", ".join(item["veldwerkers"]),
                "aangemaakt_door": item["aangemaakt_door"],
                "assignment": item["assignment"],
                "subassignment": item["subassignment"] or "algemeen"
            }
        })

    calendar_options = {
        "initialView": "dayGridMonth",
        "locale": "nl",
        "height": 650,
        "eventColor": "#2E7D32",
        "eventDisplay": "block"
    }

    st.markdown("### Kalender")
    clicked = calendar(events=events, options=calendar_options)

    # ------------------------------------------
    # Event info onder de kalender
    # ------------------------------------------
    if clicked and "event" in clicked:
        event = clicked["event"]
        props = event.get("extendedProps", {})

        st.markdown("### 📌 Details van geselecteerde survey")

        st.info(
            f"""
            **Project:** {props.get('project')}  
            **Soort:** {props.get('assignment')}  
            **Surveytype:** {props.get('subassignment')}  
            **Datum:** {event.get('start')}  
            **Veldwerkers:** {props.get('veldwerkers')}  
            **Aangemaakt door:** {props.get('aangemaakt_door')}
            """
        )





