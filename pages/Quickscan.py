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
        
                st.write(f"**Potentieel geschikt voor:** {', '.join(soorten_list)}")
                st.markdown("---")


    
        st.subheader("Gebied op kaart")
        
        import json
        import folium
        from streamlit_folium import st_folium
        
        try:
            # Download GeoJSON from Supabase
            data = supabase.storage.from_("new_app").download(qs["geometry_path"])
            geojson_data = json.loads(data.decode("utf-8"))
        
            # Create a map (centered on NL)
            m = folium.Map(location=[52.5, 5.75], zoom_start=10)
        
            # Add GeoJSON directly — Folium handles centering automatically
            folium.GeoJson(
                geojson_data,
                name="Gebied",
                style_function=lambda x: {
                    "color": "green",
                    "weight": 3,
                    "fillOpacity": 0.3
                }
            ).add_to(m)
        
            # # Fit map to GeoJSON bounds
            # folium.GeoJson(geojson_data).add_to(m)
            # m.fit_bounds(folium.GeoJson(geojson_data).get_bounds())
        
            # Show map
            st_folium(m, width=700, height=500)
        
        except Exception as e:
            st.error(f"Kon de geometrie niet laden: {e}")

        st.subheader("EXTA GIS ANALYSSY")

        url = (
            "https://services.geodataoverijssel.nl/geoserver/B46_natuur_en_landschap/ows?"
            "service=WFS&version=2.0.0&request=GetFeature&"
            "typeName=B46_natuur_en_landschap:B4_Natura_2000-gebieden&"
            "outputFormat=application/json"
        )
        
        n2000 = gpd.read_file(url).to_crs(4326)

        data = supabase.storage.from_("new_app").download(qs["geometry_path"])
        
        qs_gdf = gpd.read_file(data).set_crs(4326)

        centroid = qs_gdf.geometry.centroid.iloc[0]

        centroid_m = gpd.GeoSeries([centroid], crs=4326).to_crs(3857)
        buffer_m = centroid_m.buffer(3000)  # 3 km
        buffer = buffer_m.to_crs(4326)

        intersections = gpd.overlay(n2000, gpd.GeoDataFrame(geometry=buffer, crs=4326), how="intersection")

        if len(intersections) > 0:
            gebieden = intersections["NAAM_N2K"].unique().tolist()
        else:
            gebieden = []

        if gebieden:
            st.success("Intersectie met de volgende Natura2000‑gebieden:")
            for g in gebieden:
                st.write(f"- **{g}**")
        else:
            st.info("Geen intersectie met Natura2000‑gebieden binnen 3 km.")
            

        import folium
        from streamlit_folium import st_folium
        
        # Center map on centroid
        m = folium.Map(location=[centroid.y, centroid.x], zoom_start=12)
        
        # -----------------------------
        # Quickscan polygon (groen)
        # -----------------------------
        folium.GeoJson(
            qs_gdf,
            name="Quickscan gebied",
            style_function=lambda x: {
                "color": "green",
                "weight": 3,
                "fillOpacity": 0.3
            }
        ).add_to(m)
        
        # -----------------------------
        # 3 km buffer (blauw)
        # -----------------------------
        folium.GeoJson(
            buffer,
            name="3 km buffer",
            style_function=lambda x: {
                "color": "blue",
                "weight": 2,
                "fillOpacity": 0.05
            }
        ).add_to(m)
        
        # -----------------------------
        # Natura2000 volledige dataset (rood)
        # -----------------------------
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
        
        # -----------------------------
        # Natura2000 intersecties (geel)
        # -----------------------------
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
        
        # -----------------------------
        # Centroid marker
        # -----------------------------
        folium.Marker(
            location=[centroid.y, centroid.x],
            icon=folium.Icon(color="red")
        ).add_to(m)





        
        
        
        from branca.element import Element
        
        logo_html = f"""
        <style>
        #map-logo {{
            position: fixed;
            bottom: 15px;      /* bottom-left */
            left: 15px;
            z-index: 999999;
            background: rgba(255, 255, 255, 0.7);  /* white semi-transparent box */
            padding: 10px 10px;                    /* bigger box */
            border-radius: 10px;
            backdrop-filter: blur(3px);            /* frosted-glass effect */
            box-shadow: 0 2px 6px rgba(0,0,0,0.25);
        }}
        
        #map-logo img {{
            width: 75px;       /* bigger image (~1.7 cm) */
            height: auto;
            display: block;
        }}
        </style>
        
        <div id="map-logo">
            <img src="data:image/jpeg;base64,{encoded}">
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







