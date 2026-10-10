import streamlit as st

@st.dialog("Welkom")
def show_info_dialog():

    # Center the image
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(
            "utils/pictures/signal-2026-08-31-14-39-37-051 (1).jpg",
            use_column_width=True
        )

    # Title centered
    st.markdown(
        "<h2 style='text-align: center;'>Welkom bij de Elsken Ecologie Advies Applicatie</h2>",
        unsafe_allow_html=True
    )

    # Info text
    st.markdown(
        """
        Deze applicatie ondersteunt ecologisch adviseurs bij het uitvoeren van 
        **Quickscans**, **Inventarisaties** en **Controles**.

        Gebruik de **zijbalk** om te navigeren tussen de verschillende modules.  
        Elke module bevat duidelijke stappen om je werk efficiënt en overzichtelijk te maken.

        ### 📘 Quickscan
        In deze sectie kun je alle gegevens voor de Quickscan invoeren, bewerken en opnieuw ophalen.  
        Je beheert hier de volledige projectinformatie, inclusief veldgegevens, foto’s en soortgeschiktheid.  
        Ook kun je een automatisch gegenereerd rapport downloaden.

        ### 📗 Inventarisatie
        Hier kun je nieuwe inventarisatieprojecten aanmaken of bestaande Quickscan‑projecten overnemen.  
        Je vult alle relevante inventarisatiegegevens in en kunt aanvullende survey‑informatie toevoegen.

        ### 📙 Control
        In deze sectie volg je de voortgang en resultaten van elk project.  
        Je ziet direct of alle stappen correct zijn uitgevoerd en of er ecologische bevindingen zijn.

        Je blijft ingelogd zolang je de browser open houdt.
        """,
        unsafe_allow_html=True
    )
