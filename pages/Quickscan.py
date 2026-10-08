import json
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

from utils.auth import check_password
from utils.geometry_tools import draw_geometry
from utils.quickscan_tools import save_quickscan
from utils.supabase_client import supabase
from utils.species_groups import SPECIES_GROUPS
from utils.media_tools import save_photos





if check_password():

    st.title("Quickscan")

    tab_create, tab_edit = st.tabs(["Nieuwe Quickscan", "Quickscan bewerken"])

    with tab_create:
        st.subheader("Nieuwe Quickscan")

        geojson = draw_geometry()

        naam = st.text_input("Projectnaam")
        opmerking = st.text_area("Beschrijving")

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

        st.subheader("Soortgeschiktheid")
        
        soorten_results = {}
        
        for group, species_list in SPECIES_GROUPS.items():
            suitable = st.toggle(f"Is het gebied geschikt voor {group}?")
        
            if suitable:
                if species_list:
                    selected = st.multiselect(
                        f"Welke soorten binnen {group}?",
                        species_list,
                        key=f"species_{group}"
                    )
                    soorten_results[group] = selected
                else:
                    soorten_results[group] = True
            else:
                soorten_results[group] = False


        st.subheader("Foto's")

        # Only show species groups that were selected earlier
        beschikbare_soortgroepen = []
        
        for group, value in soorten_results.items():
            if value:  # True or list
                beschikbare_soortgroepen.append(group)
                
        
        add_photo = st.toggle("Wil je een foto toevoegen?")
        
        while add_photo:
            photo = st.file_uploader(
                "Upload een foto",
                type=["jpg", "jpeg", "png"],
                key=f"photo_{len(photos_to_upload)}"
            )
        
            if photo:
        
                beschrijving = st.text_area("Schrijf een beschrijving voor deze foto")
        
                # MULTISELECT with only the groups the user selected earlier
                soortgroepen_foto = st.multiselect(
                    "Voor welke soortgroepen is dit habitat potentieel geschikt?",
                    beschikbare_soortgroepen,
                    key=f"species_photo_{len(photos_to_upload)}"
                )
        
                photos_to_upload.append({
                    "file": photo,
                    "beschrijving": beschrijving,
                    "soortgroepen": soortgroepen_foto
                })
        
                st.success("Foto toegevoegd.")
        
            add_photo = st.toggle("Nog een foto toevoegen?")






        if st.button("Project opslaan"):
        
            if not geojson:
                st.error("Teken eerst een geometrie.")
                st.stop()
        
            if not naam:
                st.error("Voer een projectnaam in.")
                st.stop()
        
            # Check if project name already exists
            existing = supabase.table("new_app_quickscan").select("naam").eq("naam", naam.replace(" ", "_")).execute()
            if existing.data:
                st.error("Projectnaam bestaat al. Kies een andere naam.")
                st.stop()
        
            with st.spinner("Quickscan wordt opgeslagen…"):
            
                save_quickscan(
                    naam,
                    opmerking,
                    geojson,
                    datum,
                    veldwerker,
                    starttijd,
                    eindtijd,
                    temperatuur,
                    windsnelheid,
                    regen,
                    soorten_results
                )
            
                if photos_to_upload:
                    save_photos(naam, photos_to_upload)
            
            st.success("Quickscan succesvol opgeslagen!")


    with tab_edit:
        st.subheader("Quickscan bewerken")
        st.info("Hier komt de lijst met bestaande Quickscans.")

