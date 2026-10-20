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

    name_to_email = {e["volledige_naam"]: e["email"] for e in employees}
    alle_namen = list(name_to_email.keys())


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
    
    # soort heeft subtypes als value een dict is met minstens 1 geldige subtype
    heeft_subtypes = isinstance(value, dict) and any(
        isinstance(v, dict) for v in value.values()
    )
    
    if heeft_subtypes:
        # Filter subtypes die null zijn
        value = {k: v for k, v in value.items() if isinstance(v, dict)}
    
        surveytypes = list(value.keys())
        gekozen_surveytype = st.selectbox("onderzoektype:", surveytypes)
        survey_details = value[gekozen_surveytype]
        subassignment = gekozen_surveytype
    else:
        # soort heeft GEEN subtypes
        gekozen_surveytype = "algemeen"
        survey_details = value
        subassignment = ""



    aantal_personen = survey_details["aantal_personen"]

    # ---------------------------------------------------------
    # 4. Kies datum
    # ---------------------------------------------------------
    datum = st.date_input("Datum van de onderzoek")

    # ---------------------------------------------------------
    # 5. Kies veldwerkers (uit new_app_employees)
    # ---------------------------------------------------------
    geselecteerde_namen = st.multiselect(
        "Kies veldwerkers:",
        options=alle_namen
    )
    
    # converteer namen → emails
    geselecteerde_werkers = [name_to_email[n] for n in geselecteerde_namen]


    if len(geselecteerde_werkers) != aantal_personen:
        st.error(f"Je moet precies **{aantal_personen}** veldwerkers kiezen.")
        st.stop()


    # ---------------------------------------------------------
    # 6. Protocolvalidatie
    # ---------------------------------------------------------
    
    # Haal eerdere surveys op voor dit project + soort
    eerdere_surveys = supabase.table("new_app_planning") \
        .select("*") \
        .eq("project_naam", keuze["project_naam"]) \
        .eq("assignment", gekozen_soort) \
        .execute().data
    
    regels = PROTOCOLS.get(gekozen_soort, {}).get(gekozen_surveytype, {})
    
    min_dagen = regels.get("min_dagen")
    derde_maand = regels.get("derde_survey_maand")
    periode_start = regels.get("periode_start")
    periode_eind = regels.get("periode_eind")
    
    # -----------------------------------------
    # 1. Minimum dagen tussen surveys
    # -----------------------------------------
    if min_dagen and eerdere_surveys:
        laatste_datum = max([datetime.fromisoformat(s["datum"]) for s in eerdere_surveys])
        verschil = (datum - laatste_datum.date()).days
    
        if verschil < min_dagen:
            st.error(
                f"Er moeten minimaal **{min_dagen} dagen** tussen twee surveys zitten."
            )
            st.stop()
    
    # -----------------------------------------
    # 2. Derde survey verplichte maand
    # -----------------------------------------
    if derde_maand and len(eerdere_surveys) == 2:
        if datum.month != derde_maand:
            maandnaam = [
                "januari","februari","maart","april","mei","juni",
                "juli","augustus","september","oktober","november","december"
            ][derde_maand - 1]
    
            st.error(
                f"De derde survey moet plaatsvinden in **{maandnaam}**."
            )
            st.stop()
    
    # -----------------------------------------
    # 3. Periode waarin surveys mogen plaatsvinden
    # -----------------------------------------
    if periode_start and periode_eind:
        start = datetime.fromisoformat(periode_start).date()
        eind = datetime.fromisoformat(periode_eind).date()
    
        if not (start <= datum <= eind):
            st.error(
                f"Deze survey moet plaatsvinden tussen **{start.strftime('%d-%m-%Y')}** "
                f"en **{eind.strftime('%d-%m-%Y')}**."
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

    # ---------------------------------------------------------
    # 1. Toon alleen events waar de ingelogde gebruiker in zit
    # ---------------------------------------------------------
    user = st.session_state.get("user")
    user_email = user.email

    planning_user = [p for p in planning if user_email in p["veldwerkers"]]

    if not planning_user:
        st.info("Je hebt geen geplande surveys.")
        st.stop()

    # ---------------------------------------------------------
    # 2. Range slider voor maanden
    # ---------------------------------------------------------
    maanden = {
        1: "Januari", 2: "Februari", 3: "Maart", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Augustus",
        9: "September", 10: "Oktober", 11: "November", 12: "December"
    }

    st.markdown("### Filter op maanden")

    gekozen_maanden = st.select_slider(
        "Kies een periode:",
        options=list(maanden.keys()),
        value=(1, 12),  # standaard: hele jaar
        format_func=lambda m: maanden[m]
    )

    maand_start, maand_eind = gekozen_maanden

    planning_user = [
        p for p in planning_user
        if maand_start <= datetime.fromisoformat(p["datum"]).month <= maand_eind
    ]

    # ---------------------------------------------------------
    # 3. Filter op project
    # ---------------------------------------------------------
    projecten = sorted(list({p["project_naam"] for p in planning_user}))
    gekozen_project = st.selectbox("Filter op project:", ["Alle projecten"] + projecten)

    if gekozen_project != "Alle projecten":
        planning_user = [p for p in planning_user if p["project_naam"] == gekozen_project]

    # ---------------------------------------------------------
    # 4. Lijstweergave van events
    # ---------------------------------------------------------
    st.markdown("### 📅 Jouw geplande surveys")

    if not planning_user:
        st.info("Geen surveys gevonden voor deze filters.")
        st.stop()

    geselecteerd_event = None

    for p in planning_user:
        datum_str = datetime.fromisoformat(p["datum"]).strftime("%d-%m-%Y")
        label = f"{datum_str} — {p['assignment']} ({p['subassignment'] or 'algemeen'}) — {p['project_naam']}"

        if st.button(label):
            geselecteerd_event = p

    # ---------------------------------------------------------
    # 5. Details onder de lijst
    # ---------------------------------------------------------
    if geselecteerd_event:
        st.markdown("### 📌 Details van geselecteerde survey")

        st.info(
            f"""
            **Project:** {geselecteerd_event['project_naam']}  
            **Soort:** {geselecteerd_event['assignment']}  
            **Surveytype:** {geselecteerd_event['subassignment'] or 'algemeen'}  
            **Datum:** {geselecteerd_event['datum']}  
            **Veldwerkers:** {", ".join(geselecteerd_event['veldwerkers'])}  
            **Aangemaakt door:** {geselecteerd_event['aangemaakt_door']}
            """
        )







