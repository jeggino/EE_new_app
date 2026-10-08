import json
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import geopandas as gpd
import ast

import requests
import folium
from streamlit_folium import st_folium


from utils.auth import check_password
from utils.geometry_tools import draw_geometry
from utils.quickscan_tools import save_quickscan
from utils.supabase_client import supabase
from utils.species_groups import SPECIES_GROUPS
from utils.media_tools import save_photos





if check_password():

    st.title("Quickscan",text_alignment="center",)

    tab_create, tab_edit, tab_view = st.tabs(["Nieuwe Quickscan", "Quickscan bewerken", "Quickscan bekijken"])

    with tab_create:
        st.subheader("Nieuwe Quickscan",text_alignment="center",)

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
        st.header("Quickscan bekijken",text_alignment="center",)
    
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
        st.write(f"**Beschrijving:** {qs['opmerking']}")
    
        st.subheader("Weersomstandigheden")
        st.write(f"**Temperatuur:** {qs['temperatuur']} °C")
        st.write(f"**Wind:** {qs['windsnelheid']} Bft")
        st.write(f"**Regen:** {qs['regen']}")
        
        "---"
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
        
    
        "---"
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
        
                st.write(f"**Potentieel geschikt voor:** {', '.join(soorten_list)}")
               

        "---"
        st.markdown("""
        ### Extra GIS‑analyse: afstand tot Natura 2000‑gebieden
        
        Met deze aanvullende analyse wordt gecontroleerd of het onderzoeksgebied zich binnen een straal van **3 kilometer** van een Natura 2000‑gebied bevindt.  
        De tool berekent automatisch:
        
        - het **centroid** van het Quickscan‑gebied  
        - een **buffer van 3 km** rond dit punt  
        - de **intersectie** met alle Natura 2000‑gebieden  
        - een **kaartvisualisatie** met alle relevante lagen  
        
        Klik op de knop hieronder om de analyse uit te voeren.
        """)

        run_analysis = st.toggle(
            "Wil je controleren of het onderzoeksgebied binnen 3 km van een Natura 2000‑gebied ligt?"
        )


        if run_analysis:
            with st.spinner("GIS‑analyse wordt uitgevoerd..."):
        
                # -----------------------------
                # 1. Natura2000 dataset laden
                # -----------------------------
                url = (
                    "https://services.geodataoverijssel.nl/geoserver/B46_natuur_en_landschap/ows?"
                    "service=WFS&version=2.0.0&request=GetFeature&"
                    "typeName=B46_natuur_en_landschap:B4_Natura_2000-gebieden&"
                    "outputFormat=application/json"
                )
                n2000 = gpd.read_file(url).to_crs(4326)
        
                # -----------------------------
                # 2. Quickscan geometrie laden
                # -----------------------------
                data = supabase.storage.from_("new_app").download(qs["geometry_path"])
                qs_gdf = gpd.read_file(data).set_crs(4326)
        
                # -----------------------------
                # 3. Centroid + buffer
                # -----------------------------
                centroid = qs_gdf.geometry.centroid.iloc[0]
        
                centroid_m = gpd.GeoSeries([centroid], crs=4326).to_crs(3857)
                buffer_m = centroid_m.buffer(3000)  # 3 km
                buffer = buffer_m.to_crs(4326)
        
                # -----------------------------
                # 4. Intersectie met Natura2000
                # -----------------------------
                intersections = gpd.overlay(
                    n2000,
                    gpd.GeoDataFrame(geometry=buffer, crs=4326),
                    how="intersection"
                )
        
                if len(intersections) > 0:
                    gebieden = intersections["NAAM_N2K"].unique().tolist()
                else:
                    gebieden = []
        
                # -----------------------------
                # 5. Resultaten tonen
                # -----------------------------
                if gebieden:
                    st.success("Intersectie met de volgende Natura2000‑gebieden:")
                    for g in gebieden:
                        st.write(f"- **{g}**")
                else:
                    st.info("Geen intersectie met Natura2000‑gebieden binnen 3 km.")
        
                # -----------------------------
                # 6. Folium kaart bouwen
                # -----------------------------
                import folium
                from streamlit_folium import st_folium
        
                m = folium.Map(location=[centroid.y, centroid.x], zoom_start=12)
        
                # Quickscan polygon
                folium.GeoJson(
                    qs_gdf,
                    name="Quickscan gebied",
                    style_function=lambda x: {
                        "color": "green",
                        "weight": 3,
                        "fillOpacity": 0.3
                    }
                ).add_to(m)
        
                # 3 km buffer
                folium.GeoJson(
                    buffer,
                    name="3 km buffer",
                    style_function=lambda x: {
                        "color": "blue",
                        "weight": 2,
                        "fillOpacity": 0.05
                    }
                ).add_to(m)
        
                # Natura2000 dataset
                folium.GeoJson(
                    n2000,
                    name="Natura2000",
                    style_function=lambda x: {
                        "color": "red",
                        "weight": 1,
                        "fillOpacity": 0.1
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=["NAAM_N2K", "STATUS", "BESCHERMIN"],
                        aliases=["Naam", "Status", "Bescherming"],
                        sticky=True
                    )
                ).add_to(m)
        
                # Intersecties
                if len(intersections) > 0:
                    folium.GeoJson(
                        intersections,
                        name="Intersectie",
                        style_function=lambda x: {
                            "color": "yellow",
                            "weight": 3,
                            "fillOpacity": 0.4
                        }
                    ).add_to(m)
        
                # Centroid marker
                folium.Marker(
                    location=[centroid.y, centroid.x],
                    icon=folium.Icon(color="red")
                ).add_to(m)
        
                # Legenda + windroos
                import base64
                from pathlib import Path
                from branca.element import Element
        
                logo_path = "utils/pictures/pngwing.com.png"
                with open(logo_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()
        
                logo_html = f"""
                <div id="map-logo" style="
                    position: fixed;
                    bottom: 15px;
                    left: 15px;
                    z-index: 999999;
                    background: rgba(255,255,255,0.7);
                    padding: 10px;
                    border-radius: 10px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.25);
                ">
                    <img src="data:image/jpeg;base64,{encoded}" style="width:75px;">
                </div>
                """
                m.get_root().html.add_child(Element(logo_html))
        
                from branca.element import Element
                
                legend_html = """
                <style>
                #map-legend {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 999999;
                    background: rgba(255, 255, 255, 0.9);
                    padding: 14px 18px;
                    border-radius: 10px;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.25);
                    font-family: 'Arial', sans-serif;
                    font-size: 14px;
                    color: #222;
                    width: 190px;
                }
                
                .legend-item {
                    display: flex;
                    align-items: center;
                    margin-bottom: 10px;
                }
                
                .legend-symbol {
                    width: 22px;
                    height: 22px;
                    margin-right: 10px;
                    flex-shrink: 0;
                }
                
                /* Professionele blauwe marker */
                .legend-marker {
                    background: url('https://cdn-icons-png.flaticon.com/512/2776/2776067.png');
                    background-size: cover;
                    border-radius: 0;
                }
                
                /* 1 km buffer (blauwe cirkel) */
                .legend-circle {
                    background: none;
                    border: 3px solid #0066ff;
                    border-radius: 50%;
                }
                
                /* Overlap (geel) */
                .legend-yellow {
                    background: #FFD700;
                    border: 2px solid #C9A000;
                    border-radius: 4px;
                }
                
                /* Natura2000 (rood) */
                .legend-red {
                    background: orange;
                    border: 2px solid #B22222;
                    border-radius: 4px;
                }
                </style>
                
                <div id="map-legend">
                
                    <div class="legend-item">
                        <div class="legend-symbol legend-marker"></div>
                        <span><b>Locatie</b></span>
                    </div>
                
                    <div class="legend-item">
                        <div class="legend-symbol legend-circle"></div>
                        <span><b>3 km buffer</b></span>
                    </div>
                
                    <div class="legend-item">
                        <div class="legend-symbol legend-yellow"></div>
                        <span><b>Overlap</b></span>
                    </div>
                
                    <div class="legend-item">
                        <div class="legend-symbol legend-red"></div>
                        <span><b>Natura2000‑gebied</b></span>
                    </div>
                
                </div>
                """
                
                m.get_root().html.add_child(Element(legend_html))

        
                st_folium(m, width=700, height=500)

        "---"
        st.markdown("""
        ### Conclusie van de Quickscan
        
        In dit onderdeel kun je een conclusie toevoegen aan de Quickscan.  
        Deze conclusie wordt opgeslagen in de database en vormt het eindadvies van de ecologische beoordeling.
        """)

        # 1. Vraag of gebruiker een conclusie wil schrijven
        write_conclusion = st.toggle("Wil je een conclusie toevoegen of bewerken?")
        
        # Haal bestaande conclusie op (indien aanwezig)
        existing = supabase.table("new_app_quickscan_conclusions") \
            .select("*") \
            .eq("project_naam", qs["naam"]) \
            .execute()
        
        existing_text = None
        existing_id = None
        
        if existing.data:
            existing_text = existing.data[0]["conclusie"]
            existing_id = existing.data[0]["id"]
        
        if write_conclusion:
                
            st.markdown("#### Schrijf of bewerk de conclusie")
        
            conclusion_text = st.text_area(
                "Conclusie:",
                value=existing_text if existing_text else "",
                placeholder="..."
            )
        
            if existing_id:
        
                st.info("Er is al een conclusie opgeslagen voor dit project.")
        
                col1, col2, col3 = st.columns(3)
        
                # --- Bijwerken ---
                with col1:
                    if st.button("Conclusie bijwerken"):
                        if conclusion_text.strip() == "":
                            st.error("De conclusie mag niet leeg zijn.")
                        else:
                            supabase.table("new_app_quickscan_conclusions") \
                                .update({"conclusie": conclusion_text}) \
                                .eq("id", existing_id) \
                                .execute()
        
                            st.success("De conclusie is bijgewerkt.")
                            st.rerun()   # 🔄 nieuwe reload
        
                # --- Verwijderen ---
                with col2:
                    if st.button("Conclusie verwijderen"):
                        supabase.table("new_app_quickscan_conclusions") \
                            .delete() \
                            .eq("id", existing_id) \
                            .execute()
        
                        st.warning("De conclusie is verwijderd.")
                        st.rerun()   # 🔄 nieuwe reload
        
                # --- Handmatige reload ---
                with col3:
                    if st.button("Vernieuwen"):
                        st.rerun()   # 🔄 nieuwe reload
        
            else:
                if st.button("Nieuwe conclusie opslaan"):
                    if conclusion_text.strip() == "":
                        st.error("De conclusie mag niet leeg zijn.")
                    else:
                        supabase.table("new_app_quickscan_conclusions") \
                            .insert({
                                "project_naam": qs["naam"],
                                "conclusie": conclusion_text
                            }).execute()
        
                        st.success("De conclusie is succesvol opgeslagen.")
                        st.rerun()   # 🔄 nieuwe reload




        "---"
        from docx import Document
        from docx.shared import Inches
        import io
        
        st.subheader("Download Quickscan Rapport (.docx)")
        
        # Haal conclusie op
        conclusion_data = supabase.table("new_app_quickscan_conclusions") \
            .select("*") \
            .eq("project_naam", qs["naam"]) \
            .execute()
        
        conclusion_text = (
            conclusion_data.data[0]["conclusie"]
            if conclusion_data.data else "Geen conclusie opgeslagen."
        )
        
        # Maak Word-document
        doc = Document()
        
        doc.add_heading("Quickscan Rapport", level=1)
        
        doc.add_heading("Projectinformatie", level=2)
        doc.add_paragraph(f"Naam: {qs['naam']}")
        doc.add_paragraph(f"Datum: {qs['datum']}")
        doc.add_paragraph(f"Veldwerker: {qs['veldwerker']}")
        doc.add_paragraph(f"Opmerking: {qs['opmerking']}")
        
        doc.add_heading("Weersomstandigheden", level=2)
        doc.add_paragraph(f"Temperatuur: {qs['temperatuur']} °C")
        doc.add_paragraph(f"Wind: {qs['windsnelheid']} Bft")
        doc.add_paragraph(f"Regen: {qs['regen']}")
        

        
        # Voeg foto toe (als aanwezig)
        if "foto_path" in qs:
            img_bytes = supabase.storage.from_("new_app").download(qs["foto_path"])
            doc.add_heading("Foto", level=2)
            doc.add_picture(io.BytesIO(img_bytes), width=Inches(4))
        
        # Document in geheugen opslaan
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        # Download-knop
        st.download_button(
            "Download Quickscan Rapport (.docx)",
            buffer,
            file_name=f"{qs['naam']}_quickscan.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )








