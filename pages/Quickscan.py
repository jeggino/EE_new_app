import json
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import ast


from utils.auth import check_password
from utils.geometry_tools import draw_geometry
from utils.quickscan_tools import save_quickscan
from utils.supabase_client import supabase
from utils.species_groups import SPECIES_GROUPS
from utils.media_tools import save_photos





if check_password():

    st.title("Quickscan")

    tab_create, tab_edit, tab_view = st.tabs(["Nieuwe Quickscan", "Quickscan bewerken", "Quickscan bekijken"])

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

        beschikbare_soortgroepen = []
        
        for group, value in soorten_results.items():
            if value is True:
                # Group was marked suitable but has no subspecies
                beschikbare_soortgroepen.append(group)
        
            elif isinstance(value, list) and len(value) > 0:
                # Add each selected species inside the group
                for species in value:
                    beschikbare_soortgroepen.append(species)

                
                
        photos_to_upload = []
        
        add_photo = st.toggle("Wil je een foto toevoegen?", key="add_photo_first")
        
        while add_photo:
            index = len(photos_to_upload)
        
            photo = st.file_uploader(
                "Upload een foto",
                type=["jpg", "jpeg", "png"],
                key=f"photo_{index}"
            )
        
            if photo:
                beschrijving = st.text_area(
                    "Schrijf een beschrijving voor deze foto",
                    key=f"beschrijving_{index}"
                )
        
                soortgroepen_foto = st.multiselect(
                    "Voor welke soortgroepen is dit habitat potentieel geschikt?",
                    beschikbare_soortgroepen,
                    key=f"soortgroepen_{index}"
                )
        
                photos_to_upload.append({
                    "file": photo,
                    "beschrijving": beschrijving,
                    "soortgroepen": soortgroepen_foto
                })
        
                st.success("Foto toegevoegd.")
        
            # IMPORTANT: give this toggle a UNIQUE key
            add_photo = st.toggle(
                "Nog een foto toevoegen?",
                key=f"add_photo_{index}"
            )




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

    
    with tab_view:
        st.header("Quickscan bekijken")
    
        # Load all quickscans
        all_qs = supabase.table("new_app_quickscan") \
            .select("naam, datum") \
            .order("datum", desc=True) \
            .execute()
    
        if not all_qs.data:
            st.info("Nog geen Quickscans beschikbaar.")
            st.stop()
    
        # Dropdown
        qs_labels = [f"{qs['naam']} ({qs['datum']})" for qs in all_qs.data]
        selected_label = st.selectbox("Kies een Quickscan:", qs_labels)
    
        selected_name = selected_label.split(" (")[0]
    
        # Load selected Quickscan
        qs = supabase.table("new_app_quickscan") \
            .select("*") \
            .eq("naam", selected_name) \
            .single() \
            .execute().data
    
        # Show info
        st.subheader("Projectinformatie")
        st.write(f"**Naam:** {qs['naam']}")
        st.write(f"**Datum:** {qs['datum']}")
        st.write(f"**Veldwerker:** {qs['veldwerker']}")
        st.write(f"**Opmerking:** {qs['opmerking']}")
    
        st.subheader("Weersomstandigheden")
        st.write(f"**Temperatuur:** {qs['temperatuur']} °C")
        st.write(f"**Wind:** {qs['windsnelheid']} Bft")
        st.write(f"**Regen:** {qs['regen']}")
    
        st.subheader("Soortgeschiktheid")

        
        soorten = qs["soorten"]
        
        rows = []
        
        for group, value in soorten.items():
            if value is True:
                rows.append([group, "Geschikt", "—"])
            elif value is False:
                rows.append([group, "Niet geschikt", "—"])
            elif isinstance(value, list):
                rows.append([group, "Geschikt", ", ".join(value)])
        
        df = pd.DataFrame(rows, columns=["Soortgroep", "Geschiktheid", "Soorten"])
        
        st.table(df)
        
    
        # Photos
        st.subheader("Foto's")
        fotos = supabase.table("new_app_quickscan_fotos") \
            .select("*") \
            .eq("quickscan_naam", qs["naam"]) \
            .execute()
        
        if not fotos.data:
            st.info("Geen foto's toegevoegd.")
        else:
            import ast
        
            for foto in fotos.data:
                url = supabase.storage.from_("new_app").get_public_url(foto["foto_pad"])
                st.image(url, caption=foto["beschrijving"])
        
                soorten_list = foto["soortgroep"]
        
                # Convert JSON string → Python list
                if isinstance(soorten_list, str):
                    soorten_list = ast.literal_eval(soorten_list)
        
                st.write(f"**Soorten:** {', '.join(soorten_list)}")
                st.markdown("---")


    
        # Geometry
        st.subheader("Gebied op kaart")
    
        geojson_url = supabase.storage.from_("new_app").get_public_url(qs["geometry_path"])

        import requests
        import json
    
        try:
            geojson_data = requests.get(geojson_url).json()
            st.map(geojson_data)
        except:
            st.error("Kon de geometrie niet laden.")
    
    
            st.subheader("Download PDF")
        
            pdf_text = f"""
            Quickscan Rapport
            -----------------
        
            Naam: {qs['naam']}
            Datum: {qs['datum']}
            Veldwerker: {qs['veldwerker']}
            Opmerking: {qs['opmerking']}
        
            Weersomstandigheden:
            - Temperatuur: {qs['temperatuur']} °C
            - Wind: {qs['windsnelheid']} Bft
            - Regen: {qs['regen']}
        
            Soortgeschiktheid:
            {json.dumps(qs['soorten'], indent=4)}
            """
        
            st.download_button(
                "Download Quickscan PDF",
                pdf_text,
                file_name=f"{qs['naam']}.txt",  # you can convert to PDF later
                mime="text/plain"
            )







