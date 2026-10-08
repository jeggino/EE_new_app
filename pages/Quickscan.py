import json
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

from utils.auth import check_password
from utils.geometry_tools import draw_geometry
from utils.quickscan_tools import save_quickscan


if check_password():

    st.title("Quickscan")

    tab_create, tab_edit = st.tabs(["Nieuwe Quickscan", "Quickscan bewerken"])

    with tab_create:
        st.subheader("Nieuwe Quickscan")

        geojson = draw_geometry()

        project_name = st.text_input("Projectnaam")
        description = st.text_area("Beschrijving")

        st.subheader("Veldgegevens")
        
        datum = st.date_input("Datum")
        veldwerker = st.text_input("Veldwerker")
        now_local = datetime.now(ZoneInfo("Europe/Amsterdam")).time()
        starttijd = st.time_input("Starttijd",value=now_local)
        eindtijd = st.time_input("Eindtijd",value=now_local)
        
        temperatuur = st.number_input("Temperatuur (°C)", step=0.1)
        windsnelheid = st.selectbox(
            "Windsnelheid",
            ["0 - Stil", "1 - Zwak", "2 - Matig", "3 - Vrij krachtig", "4 - Sterk", "5 - Storm"]
        )
        regen = st.selectbox(
            "Regen",
            ["Geen", "Licht", "Matig", "Hevig"]
        )


        if st.button("Project opslaan"):
        
            if not geojson:
                st.error("Teken eerst een geometrie.")
                st.stop()
        
            if not project_name:
                st.error("Voer een projectnaam in.")
                st.stop()
        
            st.write("DEBUG:", project_name, description, datum, veldwerker, starttijd, eindtijd, temperatuur, windsnelheid, regen)
        
            save_quickscan(
                project_name,
                description,
                geojson,
                datum,
                veldwerker,
                starttijd,
                eindtijd,
                temperatuur,
                windsnelheid,
                regen
            )




            st.success("Quickscan succesvol opgeslagen.")
            # st.rerun()

    with tab_edit:
        st.subheader("Quickscan bewerken")
        st.info("Hier komt de lijst met bestaande Quickscans.")

