import streamlit as st
from utils.auth import check_password


st.set_page_config(page_title="Ecologisch Advies - Home", page_icon="🌿",initial_sidebar_state="collapsed")

if check_password():

    # Center the image using Streamlit columns
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("utils/pictures/signal-2026-08-31-14-39-37-051 (1).jpg", use_column_width=True)

    st.title("Welkom bij de Elsken Ecologie Advies Applicatie")

    st.write(
        """
        Deze applicatie ondersteunt ecologisch adviseurs bij het uitvoeren van 
        **Quickscans**, **Inventarisaties** en **Controles**.

        Gebruik de **zijbalk** om te navigeren tussen de verschillende modules.  
        Elke module bevat duidelijke stappen om je werk efficiënt en overzichtelijk te maken.

        - :blue[**Quickscan**] – In deze sectie kun je alle gegevens voor de Quickscan invoeren, bewerken en opnieuw ophalen. Je beheert hier de volledige projectinformatie, inclusief veldgegevens, foto’s en soortgeschiktheid. Daarnaast is het mogelijk om een conclusie te schrijven of te actualiseren. Zodra alle informatie compleet is, kun je een automatisch gegenereerd .doc‑rapport downloaden waarin alle ingevoerde gegevens, inclusief de conclusie en projectfoto’s, zijn samengevoegd. 
        - :blue[**Inventarisatie**] – In deze sectie kun je nieuwe projecten voor de inventarisatie aanmaken of bestaande projecten uit de Quickscan overnemen. Je vult hier alle relevante inventarisatiegegevens in, zoals het type inventarisatie, het aantal rondes, de benodigde uren en de toegewezen veldwerkers. Ook kun je de contactpersoon voor het project registreren. Daarnaast is het mogelijk om aanvullende survey‑informatie toe te voegen, zodat de veldwerker volledig zelfstandig kan werken en alle benodigde instructies en projectdetails direct beschikbaar heeft.  
        - :blue[**Control**] – In deze sectie kun je de voortgang en resultaten van elk inventarisatie‑ of Quickscan‑project volgen. Je ziet hier in één overzicht of er roest‑ of nestlocaties zijn gevonden, of de dagverslagen volledig zijn ingevuld en of alle stappen van het protocol correct zijn uitgevoerd. Deze module maakt het mogelijk om de kwaliteit van het veldwerk te bewaken en direct actie te ondernemen wanneer afwijkingen, ontbrekende gegevens of urgente ecologische bevindingen worden vastgesteld.  

        Je blijft ingelogd zolang je de browser open houdt.
        """
    )

    st.divider()

    st.subheader("Ga verder naar een module")

    # st.page_link("pages/Quickscan.py", label="Quickscan", icon="🗺️")
    # st.page_link("pages/Inventarisatie.py", label="Inventarisatie", icon="📋")
    # st.page_link("pages/Control.py", label="Control", icon="🔍")

    # st.markdown("""
    # <div style="display:flex; gap:40px;">
    
    # <a href="/Quickscan" target="_self" style="text-decoration:none;">
    #     <div style="text-align:center; padding:20px;">
    #         <span style="font-size:60px;">🗺️</span><br>
    #         <span style="font-size:22px; font-weight:bold;">Quickscan</span>
    #     </div>
    # </a>
    
    # <a href="/Inventarisatie" target="_self" style="text-decoration:none;">
    #     <div style="text-align:center; padding:20px;">
    #         <span style="font-size:60px;">📋</span><br>
    #         <span style="font-size:22px; font-weight:bold;">Inventarisatie</span>
    #     </div>
    # </a>
    
    # <a href="/Control" target="_self" style="text-decoration:none;">
    #     <div style="text-align:center; padding:20px;">
    #         <span style="font-size:60px;">🔍</span><br>
    #         <span style="font-size:22px; font-weight:bold;">Control</span>
    #     </div>
    # </a>
    
    # </div>
    # """, unsafe_allow_html=True)




    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.image("utils/pictures/icons/quickscan.png", width=120)
        st.page_link("pages/Quickscan.py", label="Quickscan")
    
    with col2:
        st.image("utils/pictures/icons/inventarisatie.png", width=120)
        st.page_link("pages/Inventarisatie.py", label="Inventarisatie")
    
    with col3:
        st.image("utils/pictures/icons/control.png", width=120)
        st.page_link("pages/Control.py", label="Control")




