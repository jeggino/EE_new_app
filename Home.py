import streamlit as st
from utils.auth import check_password

st.set_page_config(page_title="Ecologisch Advies - Home", page_icon="🌿")

if check_password():

    st.markdown(
        """
        <div style="text-align: center;">
            <img src="utils/pictures/signal-2026-08-31-14-39-37-051 (1).jpg"
                 alt="Ecologisch Advies"
                 style="width: 300px; border-radius: 10px;">
        </div>
        """,
        unsafe_allow_html=True
    )

    st.title("Welkom bij de Ecologisch Advies Applicatie")
    st.write(
        """
        Deze applicatie ondersteunt ecologisch adviseurs bij het uitvoeren van 
        **Quickscans**, **Inventarisaties** en **Controles**.

        Gebruik de **zijbalk** om te navigeren tussen de verschillende modules.  
        Elke module bevat duidelijke stappen om je werk efficiënt en overzichtelijk te maken.

        - **Quickscan** – Maak projecten aan, teken geometrieën en upload foto’s  
        - **Inventarisatie** – Registreer soorten, locaties en veldnotities  
        - **Control** – Voer controles uit en bekijk eerdere resultaten  

        Je blijft ingelogd zolang je de browser open houdt.
        """
    )

    st.divider()

    st.subheader("Ga verder naar een module")

    st.page_link("pages/Quickscan.py", label="Quickscan", icon="🗺️")
    st.page_link("pages/Inventarisatie.py", label="Inventarisatie", icon="📋")
    st.page_link("pages/Control.py", label="Control", icon="🔍")


