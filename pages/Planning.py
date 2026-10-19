import streamlit as st
from datetime import datetime, timedelta

from utils.auth import check_password
from utils.supabase_client import supabase
from utils.planing.protocols import PROTOCOLS
from utils.inventarisatie.helpers import get_full_name


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


st.title("Planning van Surveys")


# ---------------------------------------------------------
# 1. Laad actieve projecten
# ---------------------------------------------------------
projecten = supabase.table("new_app_inventarisatie") \
    .select("id, project_naam, aangemaakt_op, survey_informatie, gebruikers") \
    .eq("status", "actief") \
    .execute().data

if not projecten:
    st.info("Er zijn geen actieve projecten om te plannen.")
    st.stop()


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
gebruikers = keuze["gebruikers"]


# ---------------------------------------------------------
# 3. Kies soort + surveytype
# ---------------------------------------------------------
st.markdown("### Kies een soort")

soorten = list(survey_info.keys())
gekozen_soort = st.selectbox("Soort:", soorten)

st.markdown("### Kies een surveytype")

surveytypes = list(survey_info[gekozen_soort].keys())
gekozen_surveytype = st.selectbox("Surveytype:", surveytypes)

survey_details = survey_info[gekozen_soort][gekozen_surveytype]
aantal_personen = survey_details["aantal_personen"]

st.markdown(f"Deze survey vereist **{aantal_personen} veldwerkers**.")


# ---------------------------------------------------------
# 4. Kies datum
# ---------------------------------------------------------
datum = st.date_input("Datum van de survey")


# ---------------------------------------------------------
# 5. Kies veldwerkers
# ---------------------------------------------------------
alle_namen = [get_full_name(email) for email in gebruikers]

geselecteerde_werkers = st.multiselect(
    "Kies veldwerkers:",
    options=alle_namen
)

# Validatie: aantal personen moet kloppen
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
    # vleermuizen heeft subtypes
    if surveytype in PROTOCOLS[soort]:
        regels = PROTOCOLS[soort][surveytype]
    # andere soorten hebben "algemeen"
    elif "algemeen" in PROTOCOLS[soort]:
        regels = PROTOCOLS[soort]["algemeen"]

if regels:
    min_dagen = regels["min_dagen_tussen_surveys"]
    verplichte_maand = regels["verplichte_maand_derde_survey"]

    # Haal eerdere surveys op
    eerdere_surveys = supabase.table("planning") \
        .select("*") \
        .eq("project_id", project_id) \
        .eq("soort", gekozen_soort) \
        .eq("survey_type", gekozen_surveytype) \
        .execute().data

    # Regel 1: minimum dagen tussen surveys
    if eerdere_surveys:
        laatste_datum = max([datetime.fromisoformat(s["datum"]) for s in eerdere_surveys])
        verschil = (datum - laatste_datum.date()).days

        if verschil < min_dagen:
            st.error(
                f"Volgens het protocol moeten er minimaal **{min_dagen} dagen** tussen deze surveys zitten."
            )
            st.stop()

    # Regel 2: derde survey moet in specifieke maand
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
    supabase.table("planning").insert({
        "project_id": project_id,
        "soort": gekozen_soort,
        "survey_type": gekozen_surveytype,
        "datum": str(datum),
        "veldwerkers": geselecteerde_werkers
    }).execute()

    st.success("Survey succesvol gepland!")

