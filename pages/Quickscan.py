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
from utils.geometry_tools import draw_geometry, draw_geometry_with_existing
from utils.quickscan_tools import save_quickscan
from utils.supabase_client import supabase
from utils.species_groups import SPECIES_GROUPS
from utils.media_tools import save_photos
from utils.gis_natura2000 import voer_gis_analyse_natura2000
from utils.gis_nnn import voer_gis_analyse_nnn
from utils.buttons import image_button
from utils.delete_quickscan import verwijder_quickscan
from utils.dialogs import money_dialog

import base64
from branca.element import Element




# Hide sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)



if check_password():
    col1, col2 = st.columns([2, 1])
    # col1.title("Quickscan",text_alignment="center",)
    if col2.button("⬅️ Terug naar menu"):
        st.switch_page("Home.py")

    # menu = st.pills(
    #     "Kies een onderdeel",
    #     default="Nieuwe Quickscan",
    #     selection_mode="single",
    #     options={
    #         "Nieuwe Quickscan": ":material/add_circle:",
    #         "Veldbezoek uitvoeren": ":material/forest:",
    #         "Quickscan bewerken": ":material/edit:",
    #         "Quickscan bekijken": ":material/visibility:"
    #     }
    # )

    col1, col2 = st.columns(2)
    
    with col1:
    
        if st.button(
            "➕\nNieuwe Quickscan",
            use_container_width=True
        ):
            st.session_state.menu = "Nieuwe Quickscan"
    
        if st.button(
            "✏️\nQuickscan Bewerken",
            use_container_width=True
        ):
            st.session_state.menu = "Veldbezoek uitvoeren"
    
    with col2:
    
        if st.button(
            "🌳\nVeldbezoek",
            use_container_width=True
        ):
            st.session_state.menu = "Veldbezoek uitvoeren"
    
        if st.button(
            "👁️\nQuickscan Bekijken",
            use_container_width=True
        ):
            st.session_state.menu = "Quickscan bekijken"
    
    menu = st.session_state.get("menu", "nieuw")    
    # --------------------------------------------------
    # PROJECT
    # --------------------------------------------------
    if menu == "Nieuwe Quickscan":

        # st.title("Nieuwe Quickscan",text_alignment="center", divider="blue")

        st.markdown(
            """
            <h1 style="text-align:center;">Nieuwe Quickscan</h1>
            <hr style="border:2px solid #0078D4;">
            """,
            unsafe_allow_html=True,
        )
        
        geojson = draw_geometry(
            key="project_map"
        )
    
        naam = st.text_input(
            "Projectnaam"
        )
    
        opmerking = st.text_area(
            "Beschrijving"
        )
    
        st.subheader(
            "Opdrachtgever"
        )
    
        opdrachtgever_naam = st.text_input(
            "Naam opdrachtgever"
        )
    
        opdrachtgever_tel = st.text_input(
            "Telefoonnummer"
        )
    
        opdrachtgever_email = st.text_input(
            "E-mail"
        )
    
        st.divider()
    
        if st.button(
            "💾 Project opslaan",
            use_container_width=True,
            type="primary"
        ):
    
            if not geojson:
                st.error(
                    "Teken eerst een gebied."
                )
                st.stop()
    
            if not naam:
                st.error(
                    "Projectnaam ontbreekt."
                )
                st.stop()
    
            bestaande_projecten = (
                supabase
                .table("new_app_quickscan")
                .select("naam")
                .eq("naam", naam)
                .execute()
            )
    
            if bestaande_projecten.data:
                st.error(
                    "Projectnaam bestaat al."
                )
                st.stop()
    
            with st.spinner(
                "Project opslaan en GIS-analyse uitvoeren..."
            ):
    
                # --------------------------------------
                # Project opslaan
                # --------------------------------------
    
                resp = (
                    supabase
                    .table("new_app_quickscan")
                    .insert({
                        "naam": naam,
                        "opmerking": opmerking,
    
                        "opdrachtgever_naam":
                            opdrachtgever_naam,
    
                        "opdrachtgever_telefoon":
                            opdrachtgever_tel,
    
                        "opdrachtgever_email":
                            opdrachtgever_email,
    
                        "status": "created"
                    })
                    .execute()
                )
    
                qs_id = resp.data[0]["id"]
    
                # --------------------------------------
                # Geometry opslaan
                # --------------------------------------
    
                geometry_path = (
                    f"quickscan/geometries/"
                    f"{qs_id}.geojson"
                )
    
                supabase.storage \
                    .from_("new_app") \
                    .upload(
                        geometry_path,
                        json.dumps(
                            geojson
                        ).encode("utf-8"),
                        file_options={
                            "content-type":
                                "application/geo+json",
                            "x-upsert":
                                "true"
                        }
                    )
    
                qs = {
                    "id": qs_id
                }
    
                # --------------------------------------
                # NATURA2000
                # --------------------------------------
    
                natura_result = (
                    voer_gis_analyse_natura2000(
                        qs
                    )
                )
    
                natura_map = (
                    natura_result["map"]
                )
    
                natura_html = (
                    natura_result["html"]
                )
    
                natura_table = (
                    natura_result["table"]
                )
    
                natura_html_path = (
                    f"quickscan/html/"
                    f"{qs_id}_natura2000.html"
                )
    
                supabase.storage \
                    .from_("new_app") \
                    .upload(
                        natura_html_path,
                        natura_html.encode(
                            "utf-8"
                        ),
                        file_options={
                            "content-type":
                                "text/html",
                            "x-upsert":
                                "true"
                        }
                    )
    
                # --------------------------------------
                # NNN
                # --------------------------------------
    
                nnn_result = (
                    voer_gis_analyse_nnn(
                        qs
                    )
                )
    
                nnn_map = (
                    nnn_result["map"]
                )
    
                nnn_html = (
                    nnn_result["html"]
                )
    
                nnn_table = (
                    nnn_result["table"]
                )
    
                nnn_html_path = (
                    f"quickscan/html/"
                    f"{qs_id}_nnn.html"
                )
    
                supabase.storage \
                    .from_("new_app") \
                    .upload(
                        nnn_html_path,
                        nnn_html.encode(
                            "utf-8"
                        ),
                        file_options={
                            "content-type":
                                "text/html",
                            "x-upsert":
                                "true"
                        }
                    )
    
                # --------------------------------------
                # Update paden
                # --------------------------------------
    
                try:

                    nnn_json = nnn_table.to_dict(
                        orient="records"
                    )
                    
                    natura_json = natura_table.to_dict(
                        orient="records"
                    )
                
                    supabase.table(
                        "new_app_quickscan"
                    ).update({
                
                        "nnn_html_path": nnn_html_path,
                        "natura2000_html_path": natura_html_path,
                        "nnn_data": nnn_json,
                        "natura2000_data": natura_json
                
                    }).eq(
                        "id",
                        qs_id
                    ).execute()
                
                except Exception as e:
                
                    st.error(str(e))
                    st.exception(e)

    
            st.success(
                "Project succesvol opgeslagen."
            )
    
            # ======================================
            # RESULTATEN TONEN
            # ======================================
    
            st.markdown("## 🟥 Natura 2000")
            
            st_folium(
                natura_map,
                height=650,
                width=None,
                returned_objects=[]
            )
            
            if natura_table.empty:
            
                st.info(
                    "Geen Natura 2000-gebieden binnen 3 km gevonden."
                )
            
            else:
            
                st.success(
                    f"{len(natura_table)} Natura 2000-gebied(en) gevonden."
                )
            
                st.dataframe(
                    natura_table[
                        [
                            "Gebied",
                            "Type",
                            "Afstand (m)"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )
    
            st.markdown(
                "## 🟩 Natuurnetwerk Nederland"
            )
            
            st_folium(
                nnn_map,
                width=1200,
                height=500,
                returned_objects=[]
            )
            
            if nnn_table.empty:
            
                st.info(
                    "Geen NNN-gebieden binnen 1 km gevonden."
                )
            
            else:
            
                st.success(
                    f"{len(nnn_table)} NNN-gebied(en) binnen 1 km gevonden."
                )
            
                st.dataframe(
                    nnn_table,
                    use_container_width=True,
                    hide_index=True
                )

    import json
    import folium
    from shapely.geometry import shape
    from streamlit_folium import st_folium
    from datetime import datetime
    from zoneinfo import ZoneInfo
    
    if menu == "Veldbezoek uitvoeren":
    
        # st.title("Veldbezoek",text_alignment="center",divider="blue")

        st.markdown(
            """
            <h1 style="text-align:center;">Veldbezoek</h1>
            <hr style="border:2px solid #0078D4;">
            """,
            unsafe_allow_html=True,
        )
    
        projects = (
            supabase.table("new_app_quickscan")
            .select("*")
            .eq("status", "created")
            .order("naam")
            .execute()
        )
    
        if not projects.data:
            st.info("Er zijn momenteel geen projecten beschikbaar.")
            st.stop()
    
        selected_project_name = st.selectbox(
            "Selecteer een project",
            [p["naam"] for p in projects.data]
        )
    
        project = next(
            p for p in projects.data
            if p["naam"] == selected_project_name
        )
    
        project_id = project["id"]
    
        st.divider()
    
        st.subheader(project["naam"])
    
        # ==================================================
        # PROJECT INFO
        # ==================================================
    
        col1, col2 = st.columns(2)
    
        with col1:
    
            if project.get("opmerking"):
                st.info(project["opmerking"])
    
        with col2:
    
            st.markdown("### Opdrachtgever")
    
            st.write(
                f"**Naam:** {project.get('opdrachtgever_naam') or '-'}"
            )
    
            st.write(
                f"**Telefoon:** {project.get('opdrachtgever_telefoon') or '-'}"
            )
    
            st.write(
                f"**E-mail:** {project.get('opdrachtgever_email') or '-'}"
            )
    
            if project.get("opdrachtgever_telefoon"):
    
                st.link_button(
                    "📞 Bel opdrachtgever",
                    f"tel:{project['opdrachtgever_telefoon']}"
                )
    
            if project.get("opdrachtgever_email"):
    
                st.link_button(
                    "✉️ Mail opdrachtgever",
                    f"mailto:{project['opdrachtgever_email']}"
                )
    
        st.divider()
    
        # ==================================================
        # GEOJSON
        # ==================================================
    
        try:
    
            geojson_path = (
                f"quickscan/geometries/{project_id}.geojson"
            )
    
            geojson_bytes = (
                supabase.storage
                .from_("new_app")
                .download(geojson_path)
            )
    
            geojson = json.loads(
                geojson_bytes.decode("utf-8")
            )
    
            # YOUR FILE IS A SINGLE FEATURE
            geometry = shape(
                geojson["geometry"]
            )
    
            centroid = geometry.centroid
    
            lat = centroid.y
            lon = centroid.x
    
            st.subheader("Projectgebied")
    
            m = folium.Map(
                location=[lat, lon],
                zoom_start=17,
                zoom_control=False,
                control_scale=True
            )

            tiles = 'https://api.mapbox.com/styles/v1/jeggino/cmn7ms1u3001f01pl691k0eyu/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiamVnZ2lubyIsImEiOiJjbHdscmRkZHAxMTl1MmlyeTJpb3Z2eHdzIn0.N9TRN7xxTikk235dVs1YeQ'
            folium.TileLayer(tiles=tiles,
                             attr='XXX Mapbox Attribution',
                                 max_zoom=24,
                max_native_zoom=22,
                overlay=False,
                control=True,name="OpenStreetMap").add_to(m)
            
            
            # Satellite
            folium.TileLayer(
                tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                attr="Esri",
                name="Satellite",
                max_native_zoom=21,
                max_zoom=21,
                overlay=False,
                control=True
            ).add_to(m)
        
        
            folium.LayerControl().add_to(m)

            # Logo
            logo_path = "utils/pictures/pngwing.com.png"
            with open(logo_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
        
            logo_html = f"""
            <div id="map-logo" style="
                position: fixed;
                top: 15px;
                right: 15px;
                z-index: 999999;
                background: rgba(255,255,255,0.7);
                padding: 6px;
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.25);
            ">
                <img src="data:image/jpeg;base64,{encoded}" style="width:55px;">
            </div>
            """
            m.get_root().html.add_child(Element(logo_html))


            folium.GeoJson(
                geojson,
                style_function=lambda x: {
                    "color": "#ff0000",
                    "weight": 3,
                    "fillColor": "#ff0000",
                    "fillOpacity": 0.20
                }
            ).add_to(m)
    
            folium.Marker(
                [lat, lon],
                tooltip="Projectlocatie"
            ).add_to(m)
    
            st_folium(
                m,
                height=450,
                use_container_width=True
            )
    
            google_maps_url = (
                f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
            )
    
            st.link_button(
                "📍 Navigeer naar projectlocatie",
                google_maps_url,
                use_container_width=True
            )
    
        except Exception as e:
    
            st.warning(
                f"GeoJSON kon niet worden geladen: {e}"
            )
    
        st.divider()
    
        st.markdown("""
        ### Instructie
    
        Bekijk eerst het projectgebied.
    
        Beoordeel vervolgens welke soortgroepen potentieel aanwezig zijn.
    
        Maak indien relevant habitatfoto's.
    
        Vul daarna de veldgegevens in en sla het veldbezoek op.
        """)
    
        # ==================================================
        # VELDGEGEVENS
        # ==================================================
    
        st.subheader("Veldgegevens")
    
        datum = st.date_input("Datum")
    
        veldwerker = st.text_input("Veldwerker")
    
        now_local = datetime.now(
            ZoneInfo("Europe/Amsterdam")
        ).time()
    
        starttijd = st.time_input(
            "Starttijd",
            value=now_local
        )
    
        eindtijd = st.time_input(
            "Eindtijd",
            value=now_local
        )
    
        temperatuur = st.number_input(
            "Temperatuur (°C)",
            step=0.1
        )
    
        windsnelheid = st.selectbox(
            "Windsnelheid",
            [
                "0 - Stil",
                "1 - Zwak",
                "2 - Matig",
                "3 - Vrij krachtig",
                "4 - Sterk",
                "5 - Storm"
            ]
        )
    
        regen = st.selectbox(
            "Regen",
            [
                "Geen",
                "Licht",
                "Matig",
                "Hevig"
            ]
        )
    
        # ==================================================
        # SOORTGESCHIKTHEID
        # ==================================================
    
        st.subheader("Soortgeschiktheid")
    
        soorten_results = {}
    
        for group, species_data in SPECIES_GROUPS.items():
    
            suitable = st.toggle(
                f"Is het gebied geschikt voor {group}?"
            )
    
            if not suitable:
                soorten_results[group] = False
                continue
    
            if isinstance(species_data, list):
    
                if species_data:
    
                    selected = st.multiselect(
                        f"Welke soorten binnen {group}?",
                        species_data,
                        key=f"species_{group}"
                    )
    
                    soorten_results[group] = selected
    
                else:
    
                    soorten_results[group] = True
    
            elif isinstance(species_data, dict):
    
                group_results = {}
    
                for subcat, species_list in species_data.items():
    
                    sub_suitable = st.toggle(
                        subcat,
                        key=f"toggle_{group}_{subcat}"
                    )
    
                    if sub_suitable:
    
                        selected = st.multiselect(
                            f"Welke soorten binnen {subcat}?",
                            species_list,
                            key=f"species_{group}_{subcat}"
                        )
    
                        group_results[subcat] = selected
    
                    else:
    
                        group_results[subcat] = False
    
                soorten_results[group] = group_results

        # ====================================
        # FOTO'S
        # ====================================
        
        beschikbare_soortgroepen = []
        
        for group, value in soorten_results.items():
        
            if value is True:
        
                beschikbare_soortgroepen.append(group)
        
            elif isinstance(value, list):
        
                for species in value:
                    beschikbare_soortgroepen.append(species)
        
            elif isinstance(value, dict):
        
                for subcat, subvalue in value.items():
        
                    if isinstance(subvalue, list):
        
                        for species in subvalue:
                            beschikbare_soortgroepen.append(species)
        
        st.subheader("Foto's",text_alignment="center")
        
        photos_to_upload = []
        
        add_photo = st.toggle(
            "Wil je een foto toevoegen?",
            key="add_photo_first"
        )
        
        while add_photo:
        
            index = len(photos_to_upload)
        
            photo = st.file_uploader(
                "Upload een foto",
                type=["jpg", "jpeg", "png"],
                key=f"photo_{index}"
            )
        
            if photo:
        
                beschrijving = st.text_area(
                    "Beschrijving van de foto",
                    key=f"beschrijving_{index}"
                )
        
                soortgroepen_foto = st.multiselect(
                    "Voor welke soortgroepen is dit habitat geschikt?",
                    beschikbare_soortgroepen,
                    key=f"soortgroepen_{index}"
                )
        
                photos_to_upload.append(
                    {
                        "file": photo,
                        "beschrijving": beschrijving,
                        "soortgroepen": soortgroepen_foto
                    }
                )
        
                st.success("Foto toegevoegd")
        
            add_photo = st.toggle(
                "Nog een foto toevoegen?",
                key=f"add_photo_{index}"
            )

        # ====================================
        # EINDOPMERKING
        # ====================================
        
        st.divider()
        
        st.subheader("Eindopmerking")
        
        eindopmerking = st.text_area(
            "Beschrijf de bevindingen van het veldbezoek",
            height=200,
            placeholder="Voer hier de eindopmerking van het veldbezoek in..."
        )
    
        # ==================================================
        # OPSLAAN
        # ==================================================
    
        if st.button(
            "💾 Veldbezoek opslaan",
            use_container_width=True
        ):
    
            try:
    
                (
                    supabase
                    .table("new_app_quickscan")
                    .update(
                        {
                            "datum": str(datum),
                            "veldwerker": veldwerker,
                            "starttijd": str(starttijd),
                            "eindtijd": str(eindtijd),
                            "temperatuur": temperatuur,
                            "windsnelheid": windsnelheid,
                            "regen": regen,
                            "soorten": soorten_results,
                            "eindopmerking": eindopmerking,
                            "status": "completed"
                        }
                    )
                    .eq("id", project_id)
                    .execute()
                )
    
                if photos_to_upload:
                
                    save_photos(
                        project_id,
                        photos_to_upload
                    )
                
                st.success(
                    "✅ Veldbezoek succesvol opgeslagen."
                )
    
                st.rerun()
    
            except Exception as e:
    
                st.error(
                    f"Fout bij opslaan: {e}"
                )

    if menu == "Quickscan bekijken":
    

        st.markdown(
            """
            <h1 style="text-align:center;">Quickscan bekijken</h1>
            <hr style="border:2px solid #0078D4;">
            """,
            unsafe_allow_html=True,
        )
    
        # ==================================================
        # STATUS FILTER
        # ==================================================
    
        selected_status = st.selectbox(
            "Status",
            [
                "created",
                "completed"
            ]
        )
    
        projects = (
            supabase.table("new_app_quickscan")
            .select("*")
            .eq("status", selected_status)
            .order("naam")
            .execute()
        )
    
        if not projects.data:
            st.info("Geen projecten gevonden.")
            st.stop()
    
        # ==================================================
        # PROJECT SELECTIE
        # ==================================================
    
        selected_project_name = st.selectbox(
            "Project",
            [p["naam"] for p in projects.data]
        )
    
        project = next(
            p for p in projects.data
            if p["naam"] == selected_project_name
        )
    
        project_id = project["id"]
    
        st.divider()
    
        # ==================================================
        # PROJECT INFO
        # ==================================================
    
        st.subheader(project["naam"])
    
        col1, col2 = st.columns(2)
    
        with col1:
    
            st.markdown("### Projectinformatie")
    
            st.write(
                f"**Status:** {project.get('status', '-')}"
            )
    
            if project.get("opmerking"):
    
                st.info(project["opmerking"])
    
        with col2:
    
            st.markdown("### Opdrachtgever")
    
            st.write(
                f"**Naam:** {project.get('opdrachtgever_naam') or '-'}"
            )
    
            st.write(
                f"**Telefoon:** {project.get('opdrachtgever_telefoon') or '-'}"
            )
    
            st.write(
                f"**E-mail:** {project.get('opdrachtgever_email') or '-'}"
            )
    
        st.divider()
    
        # ==================================================
        # KAART
        # ==================================================
    
        try:
    
            geojson_path = (
                f"quickscan/geometries/{project_id}.geojson"
            )
    
            geojson_bytes = (
                supabase.storage
                .from_("new_app")
                .download(geojson_path)
            )
    
            geojson = json.loads(
                geojson_bytes.decode("utf-8")
            )
    
            geometry = shape(
                geojson["geometry"]
            )
    
            centroid = geometry.centroid
    
            lat = centroid.y
            lon = centroid.x
    
            st.subheader("Projectgebied")

            m = folium.Map(
                location=[lat, lon],
                zoom_start=17,
                zoom_control=False,
                control_scale=True,
                tiles=None
            )
            
            tiles = 'https://api.mapbox.com/styles/v1/jeggino/cmn7ms1u3001f01pl691k0eyu/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiamVnZ2lubyIsImEiOiJjbHdscmRkZHAxMTl1MmlyeTJpb3Z2eHdzIn0.N9TRN7xxTikk235dVs1YeQ'
            folium.TileLayer(tiles=tiles,
                             attr='XXX Mapbox Attribution',
                                max_zoom=24,
                                max_native_zoom=22,
                                overlay=False,
                                control=True,name="OpenStreetMap").add_to(m)
            


            # Logo
            logo_path = "utils/pictures/pngwing.com.png"
            with open(logo_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
        
            logo_html = f"""
            <div id="map-logo" style="
                position: fixed;
                top: 15px;
                right: 15px;
                z-index: 999999;
                background: rgba(255,255,255,0.7);
                padding: 6px;
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.25);
            ">
                <img src="data:image/jpeg;base64,{encoded}" style="width:55px;">
            </div>
            """
            m.get_root().html.add_child(Element(logo_html))


            folium.GeoJson(
                geojson,
                style_function=lambda x: {
                    "color": "#ff0000",
                    "weight": 3,
                    "fillColor": "#ff0000",
                    "fillOpacity": 0.20
                }
            ).add_to(m)
    
            # folium.Marker(
            #     [lat, lon],
            #     tooltip="Projectlocatie"
            # ).add_to(m)
    
    
            st_folium(
                m,
                height=450,
                use_container_width=True
            )
    
    
        except Exception as e:
    
            st.warning(
                f"Kon kaart niet laden: {e}"
            )
    
        st.divider()
    
        # ==================================================
        # NNN / NATURA2000
        # ==================================================
    
    
        import streamlit.components.v1 as components
        
        if project.get("nnn_html_path"):
        
            try:
        
                html_bytes = (
                    supabase.storage
                    .from_("new_app")
                    .download(
                        project["nnn_html_path"]
                    )
                )
        
                html_content = html_bytes.decode(
                    "utf-8"
                )
        
                st.subheader("NNN Analyse")
        
                components.html(
                    html_content,
                    height=450,
                    scrolling=True
                )

                st.dataframe(
                    pd.DataFrame(project["nnn_data"]),
                    use_container_width=True
                )
        
            except Exception as e:
        
                st.warning(
                    f"NNN analyse kon niet worden geladen: {e}"
                )
    
        if project.get("natura2000_html_path"):
        
            try:
        
                html_bytes = (
                    supabase.storage
                    .from_("new_app")
                    .download(
                        project["natura2000_html_path"]
                    )
                )
        
                html_content = html_bytes.decode(
                    "utf-8"
                )
        
                st.subheader(
                    "Natura2000 Analyse"
                )
        
                components.html(
                    html_content,
                    height=450,
                    scrolling=True
                )

                st.dataframe(
                    pd.DataFrame(project["natura2000_data"]),
                    use_container_width=True
                )
        
            except Exception as e:
        
                st.warning(
                    f"Natura2000 analyse kon niet worden geladen: {e}"
                )
    
        st.divider()
        if selected_status == "completed":
            # ==================================================
            # VELDGEGEVENS
            # ==================================================
        
            st.subheader("Veldgegevens")
        
            col1, col2, col3 = st.columns(3)
        
            with col1:
        
                st.write(
                    f"**Datum:** {project.get('datum') or '-'}"
                )
        
                st.write(
                    f"**Veldwerker:** {project.get('veldwerker') or '-'}"
                )
        
            with col2:
        
                st.write(
                    f"**Starttijd:** {project.get('starttijd') or '-'}"
                )
        
                st.write(
                    f"**Eindtijd:** {project.get('eindtijd') or '-'}"
                )
        
            with col3:
        
                st.write(
                    f"**Temperatuur:** {project.get('temperatuur') or '-'} °C"
                )
        
                st.write(
                    f"**Windsnelheid:** {project.get('windsnelheid') or '-'}"
                )
        
                st.write(
                    f"**Regen:** {project.get('regen') or '-'}"
                )
        
            st.divider()
        
            # ==================================================
            # SOORTEN
            # ==================================================
        
            st.subheader("Soortgeschiktheid")
        
            soorten = project.get("soorten")
            
            if not soorten:
                st.info("Geen soortgegevens beschikbaar.")
            
            else:
            
                for groep, waarde in soorten.items():
            
                    if waarde is False:
                        continue
            
                    with st.expander(
                        groep.replace("_", " ").title(),
                        expanded=True
                    ):
            
                        if isinstance(waarde, list):
            
                            for soort in waarde:
                                st.write(f"• {soort}")
            
                        elif isinstance(waarde, dict):
            
                            for subgroep, soortenlijst in waarde.items():
            
                                if soortenlijst is False:
                                    continue
            
                                st.markdown(
                                    f"**{subgroep.replace('_', ' ').title()}**"
                                )
            
                                if isinstance(soortenlijst, list):
            
                                    for soort in soortenlijst:
                                        st.write(f"• {soort}")
            
                                else:
                                    st.write("Aanwezig")
            
                        else:
            
                            st.write("Geschikt habitat aanwezig")
        
            st.divider()
        
            # ==================================================
            # FOTO'S
            # ==================================================
        
            st.subheader("Foto's")
        
            fotos = (
                supabase.table(
                    "new_app_quickscan_fotos"
                )
                .select("*")
                .eq(
                    "quickscan_id",
                    project_id
                )
                .order(
                    "aangemaakt_op"
                )
                .execute()
            )
        
            if not fotos.data:
        
                st.info(
                    "Geen foto's gevonden."
                )
        
            else:
        
                for foto in fotos.data:
        
                    try:
        
                        image_bytes = (
                            supabase.storage
                            .from_("new_app")
                            .download(
                                foto["foto_pad"]
                            )
                        )
        
                        st.image(
                            image_bytes,
                            use_container_width=True
                        )
        
                        if foto.get("beschrijving"):
        
                            st.write(
                                f"**Beschrijving:** {foto['beschrijving']}"
                            )
        
                        if foto.get("soortgroep"):
        
                            st.write(
                                f"**Soortgroep(en):** {foto['soortgroep']}"
                            )
        
                        st.divider()
        
                    except Exception as e:
        
                        st.warning(
                            f"Foto kon niet worden geladen: {e}"
                        )

            st.divider()
            
            # ==================================================
            # EINDOPMERKING
            # ==================================================
            
            st.subheader("Eindopmerking")
            
            if project.get("eindopmerking"):
            
                st.info(project["eindopmerking"])
            
            else:
            
                st.info(
                    "Geen eindopmerking beschikbaar."
                )

            st.divider()
            
            # ==================================================
            # RAPPORT EXPORT
            # ==================================================
            
            st.subheader("Quickscan rapport")
            
            with st.expander(
                "Hoe werkt dit?",
                expanded=False
            ):
            
                st.markdown(
                    """
                    Met deze functie wordt een uitgebreide AI-prompt gegenereerd op basis van:
            
                    - Projectgegevens
                    - Opdrachtgevergegevens
                    - Veldbezoekinformatie
                    - Habitatbeoordeling
                    - Soortgeschiktheid
                    - Foto's en beschrijvingen
                    - Eindopmerking
            
                    De gegenereerde tekst kan worden ingevoerd in ChatGPT, Claude,
                    Copilot of een andere AI-toepassing om automatisch een
                    professioneel ecologisch quickscanrapport op te stellen.
            
                    Tevens bevat de prompt vaste instructies over:
            
                    - Structuur van het rapport
                    - Schrijfstijl
                    - Conclusies
                    - Aanbevelingen
                    - Wettelijk kader
                    - Professionele ecologische rapportage
                    """
                )

                rapporttekst = f"""
                Je bent een senior ecologisch adviseur.
                
                Schrijf een professioneel ecologisch quickscanrapport in het Nederlands.
                
                BELANGRIJK:
                
                - Gebruik een zakelijke rapportstijl.
                - Corrigeer spelfouten.
                - Negeer onprofessionele of irrelevante opmerkingen.
                - Verbeter onduidelijke tekst waar mogelijk.
                - Trek geen conclusies die niet uit de data volgen.
                - Vermeld onzekerheden indien informatie ontbreekt.
                - Schrijf alsof het rapport wordt opgeleverd aan een opdrachtgever.
                
                Het rapport moet minimaal de volgende hoofdstukken bevatten:
                
                1. Samenvatting
                2. Aanleiding en doel
                3. Projectlocatie
                4. Onderzoeksopzet
                5. Veldbezoek
                6. Habitatkenmerken
                7. Beoordeling soortgroepen
                8. Mogelijke risico's
                9. Aanbevelingen
                10. Conclusie
                
                PROJECTGEGEVENS
                
                Project: {project.get('naam')}
                Status: {project.get('status')}
                
                OPDRACHTGEVER
                
                Naam: {project.get('opdrachtgever_naam')}
                Telefoon: {project.get('opdrachtgever_telefoon')}
                Email: {project.get('opdrachtgever_email')}
                
                PROJECTOMSCHRIJVING
                
                {project.get('opmerking')}
                
                VELDGEGEVENS
                
                Datum: {project.get('datum')}
                Veldwerker: {project.get('veldwerker')}
                Starttijd: {project.get('starttijd')}
                Eindtijd: {project.get('eindtijd')}
                Temperatuur: {project.get('temperatuur')}
                Windsnelheid: {project.get('windsnelheid')}
                Regen: {project.get('regen')}
                
                SOORTGESCHIKTHEID
                
                {json.dumps(project.get("soorten"), indent=2, ensure_ascii=False)}
                
                EINDOPMERKING
                
                {project.get('eindopmerking')}
                """
            
            with st.expander(
                "Rapporttekst bekijken",
                expanded=False
            ):
            
                st.text_area(
                    "AI rapporttekst",
                    rapporttekst,
                    height=500
                )

                col1, col2 = st.columns(2)
                
                with col1:
                
                    st.download_button(
                        "📄 Download AI Prompt",
                        rapporttekst,
                        file_name=f"{project['naam']}_AI_prompt.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with col2:
                
                    if st.button(
                        "🤖 Genereer rapport",
                        use_container_width=True
                    ):
                        money_dialog()

            # ==================================================
            # PDF FOTOBIJLAGE
            # ==================================================
            
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                PageBreak,
                Image
            )
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import utils
            import tempfile
            import io
            import ast

            "---"
            st.subheader("Download Fotobijlage")
            
            try:
            
                if not fotos.data:
            
                    st.info("Geen foto's beschikbaar voor de PDF.")
            
                else:
            
                    pdf_buffer = io.BytesIO()
            
                    doc_pdf = SimpleDocTemplate(pdf_buffer)
            
                    styles = getSampleStyleSheet()
            
                    elements = []
            
                    elements.append(
                        Paragraph(
                            f"Fotobijlage Quickscan - {project['naam']}",
                            styles["Title"]
                        )
                    )
            
                    elements.append(Spacer(1, 20))
            
                    for i, foto in enumerate(fotos.data, start=1):
            
                        try:
            
                            # ============================
                            # FOTO DOWNLOADEN
                            # ============================
            
                            img_bytes = (
                                supabase.storage
                                .from_("new_app")
                                .download(foto["foto_pad"])
                            )
            
                            with tempfile.NamedTemporaryFile(
                                delete=False,
                                suffix=".jpg"
                            ) as tmp:
            
                                tmp.write(img_bytes)
            
                                image_path = tmp.name
            
                            # ============================
                            # AFBEELDING PASSEND SCHALEN
                            # ============================
            
                            img = utils.ImageReader(image_path)
            
                            width, height = img.getSize()
            
                            max_width = 450
                            max_height = 350
            
                            ratio = min(
                                max_width / width,
                                max_height / height
                            )
            
                            width *= ratio
                            height *= ratio
            
                            elements.append(
                                Paragraph(
                                    f"Figuur {i}",
                                    styles["Heading2"]
                                )
                            )
            
                            elements.append(
                                Image(
                                    image_path,
                                    width=width,
                                    height=height
                                )
                            )
            
                            elements.append(
                                Spacer(1, 10)
                            )
            
                            # ============================
                            # BESCHRIJVING
                            # ============================
            
                            beschrijving = (
                                foto.get("beschrijving")
                                or "Geen beschrijving beschikbaar."
                            )
            
                            elements.append(
                                Paragraph(
                                    f"<b>Beschrijving:</b><br/>{beschrijving}",
                                    styles["BodyText"]
                                )
                            )
            
                            elements.append(
                                Spacer(1, 5)
                            )
            
                            # ============================
                            # SOORTGROEP
                            # ============================
            
                            soorten = foto.get("soortgroep")
            
                            if soorten:
            
                                try:
            
                                    if isinstance(soorten, str):
            
                                        try:
                                            soorten = ast.literal_eval(soorten)
                                        except:
                                            soorten = [soorten]
            
                                    if not isinstance(soorten, list):
                                        soorten = [str(soorten)]
            
                                except Exception:
                                    soorten = [str(soorten)]
            
                                elements.append(
                                    Paragraph(
                                        f"<b>Potentieel geschikt voor:</b><br/>{', '.join(soorten)}",
                                        styles["BodyText"]
                                    )
                                )
            
                            elements.append(
                                Spacer(1, 20)
                            )
            
                            if i < len(fotos.data):
            
                                elements.append(
                                    PageBreak()
                                )
            
                        except Exception as foto_error:
            
                            elements.append(
                                Paragraph(
                                    f"Foto kon niet worden toegevoegd: {foto_error}",
                                    styles["BodyText"]
                                )
                            )
            
                    # ============================
                    # PDF BOUWEN
                    # ============================
            
                    doc_pdf.build(elements)
            
                    pdf_buffer.seek(0)
            
                    st.download_button(
                        label="📄 Download Fotobijlage PDF",
                        data=pdf_buffer,
                        file_name=f"{project['naam']}_fotobijlage.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            
            except Exception as e:
            
                st.error(
                    f"PDF generatie mislukt: {e}"
                )

            # ==================================================
            # WORD FOTOBIJLAGE
            # ==================================================
            
            from docx import Document
            from docx.shared import Inches
            import tempfile
            import io
            import ast
                        
            try:
            
                if not fotos.data:
            
                    st.info("Geen foto's beschikbaar.")
            
                else:
            
                    doc = Document()
            
                    doc.add_heading(
                        f"Fotobijlage Quickscan - {project['naam']}",
                        level=1
                    )
            
                    for i, foto in enumerate(fotos.data, start=1):
            
                        try:
            
                            # Foto downloaden uit Supabase
                            img_bytes = (
                                supabase.storage
                                .from_("new_app")
                                .download(
                                    foto["foto_pad"]
                                )
                            )
            
                            # Tijdelijke file maken
                            with tempfile.NamedTemporaryFile(
                                delete=False,
                                suffix=".jpg"
                            ) as tmp:
            
                                tmp.write(img_bytes)
            
                                image_path = tmp.name
            
                            # Figuur titel
                            doc.add_heading(
                                f"Figuur {i}",
                                level=2
                            )
            
                            # Afbeelding toevoegen
                            doc.add_picture(
                                image_path,
                                width=Inches(5.5)
                            )
            
                            # Beschrijving
                            beschrijving = (
                                foto.get("beschrijving")
                                or "Geen beschrijving beschikbaar."
                            )
            
                            doc.add_paragraph(
                                f"Beschrijving: {beschrijving}"
                            )
            
                            # Soortgroep
                            soorten = foto.get(
                                "soortgroep",
                                ""
                            )
            
                            if isinstance(soorten, str):
            
                                try:
                                    soorten = ast.literal_eval(
                                        soorten
                                    )
                                except:
                                    soorten = [soorten]
            
                            if isinstance(
                                soorten,
                                list
                            ):
                                soorten_text = ", ".join(
                                    soorten
                                )
                            else:
                                soorten_text = str(
                                    soorten
                                )
            
                            doc.add_paragraph(
                                f"Potentieel geschikt voor: {soorten_text}"
                            )
            
                            # Nieuwe pagina
                            if i < len(fotos.data):
            
                                doc.add_page_break()
            
                        except Exception as foto_error:
            
                            doc.add_paragraph(
                                f"Foto kon niet worden toegevoegd: {foto_error}"
                            )
            
                    # Opslaan in memory
                    word_buffer = io.BytesIO()
            
                    doc.save(word_buffer)
            
                    word_buffer.seek(0)
            
                    st.download_button(
                        label="📄 Download Fotobijlage Word",
                        data=word_buffer,
                        file_name=f"{project['naam']}_fotobijlage.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
            
            except Exception as e:
            
                st.error(
                    f"Word-document kon niet worden gemaakt: {e}"
                )




        else:
        
            st.info(
                "Voor dit project is nog geen veldbezoek uitgevoerd."
            )



            



    # # with tab_edit:
    # elif menu == "Quickscan bewerken":
    #     # st.subheader("Quickscan bewerken", text_alignment="center")
        
    #     # 1. Haal alle quickscans op
    #     resp = supabase.table("new_app_quickscan").select("id, naam, datum").execute()
    #     quickscans = resp.data
        
    #     if not quickscans:
    #         st.info("Geen quickscans gevonden.")
    #         st.stop()
        
    #     # 2. Dropdown
    #     keuze = st.selectbox(
    #         "Kies een Quickscan:",
    #         options=quickscans,
    #         format_func=lambda x: f"{x['naam']} ({x['datum']})"
    #     )

    #     qs_id = keuze["id"]

    #     qs_resp = supabase.table("new_app_quickscan") \
    #         .select("*") \
    #         .eq("id", qs_id) \
    #         .single() \
    #         .execute()
    
    #     qs = qs_resp.data
    
    #     if not qs:
    #         st.error("Quickscan niet gevonden.")
    #         st.stop()
        


        
    #     # -----------------------------
    #     # 1. Geometrie laden
    #     # -----------------------------
    #     # Huidige geometrie ophalen
    #     geometry_path = f"quickscan/geometries/{qs['id']}.geojson"
    #     geometry_data = supabase.storage.from_("new_app").download(geometry_path)
        
    #     import json
        
    #     # Decode bytes → JSON dict
    #     current_geojson = json.loads(geometry_data.decode("utf-8"))
        
    #     st.write("Nieuwe geometrie tekenen (optioneel):")
        
    #     nieuwe_geojson = draw_geometry_with_existing(current_geojson, key="edit_map")

        
    #     # -----------------------------
    #     # 2. Basisgegevens
    #     # -----------------------------
    #     naam = st.text_input("Projectnaam", value=qs["naam"],key=f"naam_edit_{qs['id']}")
    #     opmerking = st.text_area("Beschrijving", value=qs["opmerking"],key=f"beschrijving_edit_{qs['id']}")
        
    #     # -----------------------------
    #     # 3. Veldgegevens
    #     # -----------------------------
    #     st.subheader("Veldgegevens")
        
    #     datum = st.date_input("Datum", value=qs["datum"],key=f"datum_edit_{qs['id']}")
    #     veldwerker = st.text_input("Veldwerker", value=qs["veldwerker"],key=f"veldwerker_edit_{qs['id']}")
        
    #     starttijd = st.time_input("Starttijd", value=qs.get("starttijd"),key=f"starttijd_edit_{qs['id']}")
    #     eindtijd = st.time_input("Eindtijd", value=qs.get("eindtijd"),key=f"eindtijd_edit_{qs['id']}")
        
    #     temperatuur = st.number_input("Temperatuur (°C)", step=0.1, value=qs["temperatuur"],key=f"temperatuur_edit_{qs['id']}")
        
    #     windsnelheid = st.selectbox(
    #         "Windsnelheid",
    #         ["0 - Stil", "1 - Zwak", "2 - Matig", "3 - Vrij krachtig", "4 - Sterk", "5 - Storm"],
    #         index=["0 - Stil", "1 - Zwak", "2 - Matig", "3 - Vrij krachtig", "4 - Sterk", "5 - Storm"].index(qs["windsnelheid"]),
    #         key=f"windsnelheid_edit_{qs['id']}"
    #     )
        
    #     regen = st.selectbox(
    #         "Regen",
    #         ["Geen", "Licht", "Matig", "Hevig"],
    #         index=["Geen", "Licht", "Matig", "Hevig"].index(qs["regen"]),
    #         key=f"regen_{qs['id']}"
    #     )


    #     # -----------------------------
    #     # 4. Soortgeschiktheid
    #     # -----------------------------
    #     st.subheader("Soortgeschiktheid")
        
    #     soorten_results = qs["soorten"]  # JSON dict from database
    #     nieuwe_soorten = {}
        
    #     for group, species_data in SPECIES_GROUPS.items():
        
    #         huidige_waarde = soorten_results.get(group)
        
    #         # Determine if the group was previously marked suitable
    #         if isinstance(huidige_waarde, dict):
    #             # vogels → suitable if ANY subcategory was True or had selected species
    #             suitable_default = any(
    #                 (v is True) or (isinstance(v, list) and len(v) > 0)
    #                 for v in huidige_waarde.values()
    #             )
    #         else:
    #             suitable_default = (huidige_waarde is True or isinstance(huidige_waarde, list))
        
    #         suitable = st.toggle(
    #             f"Is het gebied geschikt voor {group}?",
    #             value=suitable_default,
    #             key=f"suitable_{group}_{qs['id']}"
    #         )
        
    #         # ---------------------------
    #         # CASE 1: group is NOT suitable
    #         # ---------------------------
    #         if not suitable:
    #             nieuwe_soorten[group] = False
    #             continue
        
    #         # ---------------------------
    #         # CASE 2: group has NO subcategories (simple list)
    #         # ---------------------------
    #         if isinstance(species_data, list):
        
    #             if species_data:
    #                 default_list = (
    #                     huidige_waarde if isinstance(huidige_waarde, list) else []
    #                 )
        
    #                 selected = st.multiselect(
    #                     f"Welke soorten binnen {group}?",
    #                     species_data,
    #                     default=default_list,
    #                     key=f"species_{group}_{qs['id']}"
    #                 )
        
    #                 nieuwe_soorten[group] = selected
        
    #             else:
    #                 nieuwe_soorten[group] = True
        
    #         # ---------------------------
    #         # CASE 3: group HAS subcategories (vogels)
    #         # ---------------------------
    #         elif isinstance(species_data, dict):
        
    #             subcat_results = {}
        
    #             # Indentation using columns
    #             main_col, sub_col = st.columns([1, 3])
        
    #             with sub_col:
    #                 st.markdown("### Subcategorieën")
        
    #                 for subcat, species_list in species_data.items():
        
    #                     # Determine default toggle state
    #                     huidige_sub = None
    #                     if isinstance(huidige_waarde, dict):
    #                         huidige_sub = huidige_waarde.get(subcat)
        
    #                     sub_default = (
    #                         huidige_sub is True or
    #                         (isinstance(huidige_sub, list) and len(huidige_sub) > 0)
    #                     )
        
    #                     sub_suitable = st.toggle(
    #                         f"{subcat}",
    #                         value=sub_default,
    #                         key=f"toggle_{group}_{subcat}_{qs['id']}"
    #                     )
        
    #                     if sub_suitable:
    #                         default_species = (
    #                             huidige_sub if isinstance(huidige_sub, list) else []
    #                         )
        
    #                         selected = st.multiselect(
    #                             f"Welke soorten binnen {subcat}?",
    #                             species_list,
    #                             default=default_species,
    #                             key=f"species_{group}_{subcat}_{qs['id']}"
    #                         )
        
    #                         subcat_results[subcat] = selected
        
    #                     else:
    #                         subcat_results[subcat] = False
        
    #             nieuwe_soorten[group] = subcat_results
        
    #         else:
    #             nieuwe_soorten[group] = True

        
    #     # -----------------------------
    #     # 5. Foto's beheren
    #     # -----------------------------
    #     st.subheader("Foto's")
        
    #     fotos_resp = supabase.table("new_app_quickscan_fotos") \
    #         .select("*") \
    #         .eq("quickscan_id", qs["id"]) \
    #         .execute()
        
    #     fotos = fotos_resp.data
        
    #     # Build available species/groups based on Quickscan suitability
    #     soorten_results = nieuwe_soorten
    #     beschikbare_soortgroepen = []
        
    #     for group, value in soorten_results.items():
        
    #         # CASE 1: group is simply True (no species list)
    #         if value is True:
    #             beschikbare_soortgroepen.append(group)
        
    #         # CASE 2: group is a list of selected species
    #         elif isinstance(value, list) and len(value) > 0:
    #             beschikbare_soortgroepen.extend(value)
        
    #         # CASE 3: group has subcategories (vogels)
    #         elif isinstance(value, dict):
    #             for subcat, subvalue in value.items():
        
    #                 # Subcategory marked suitable but no species selected
    #                 if subvalue is True:
    #                     beschikbare_soortgroepen.append(f"{group} – {subcat}")
        
    #                 # Species selected inside this subcategory
    #                 elif isinstance(subvalue, list) and len(subvalue) > 0:
    #                     beschikbare_soortgroepen.extend(subvalue)
        
    #                 # If subvalue is False → nothing added

        
    #     for foto in fotos:
    #         import os
    #         filename = os.path.basename(foto["foto_pad"])
        
        
    #         data = supabase.storage.from_("new_app").download(foto["foto_pad"])
    #         st.image(data)
    
    #         nieuwe_beschrijving = st.text_area(
    #             f"Beschrijving",
    #             value=foto.get("beschrijving", ""),
    #             key=f"beschrijving_{qs['id']}_{foto['id']}"
    #         )
    
    #         nieuwe_soorten_list = st.multiselect(
    #             f"Soortgroepen",
    #             beschikbare_soortgroepen,
    #             key=f"soorten_{qs['id']}_{foto['id']}"
    #         )
            
    #         col1, col2 = st.columns([1, 1])
    #         if col1.button("Opslaan wijzigingen", key=f"save_{qs['id']}_{foto['id']}"):
    #             supabase.table("new_app_quickscan_fotos") \
    #                 .update({
    #                     "beschrijving": nieuwe_beschrijving,
    #                     "soortgroep": nieuwe_soorten_list
    #                 }) \
    #                 .eq("id", foto["id"]) \
    #                 .execute()
    
    #             st.success("Foto metadata bijgewerkt.")
    #             st.rerun()
    
    #         if col2.button(f"Verwijder", key=f"delete_{qs['id']}_{foto['id']}"):
    #             supabase.storage.from_("new_app").remove(foto["foto_pad"])
    #             supabase.table("new_app_quickscan_fotos") \
    #                 .delete() \
    #                 .eq("id", foto["id"]) \
    #                 .execute()
    
    #             st.warning(f"verwijderd.")
    #             st.rerun()

    #         "---"


    #     if "upload_key" not in st.session_state:
    #         st.session_state.upload_key = f"upload_{qs['id']}"
        
    #     nieuwe_foto = st.file_uploader(
    #         "Nieuwe foto uploaden",
    #         type=["jpg", "jpeg", "png"],
    #         key=st.session_state.upload_key
    #     )

        
    #     if nieuwe_foto:
    #         import uuid
    #         unique_id = str(uuid.uuid4())
    #         safe_name = naam.replace(" ", "_")
        
    #         filename = f"quickscan/fotos/{unique_id}.jpg"
        
    #         # Upload to storage
    #         supabase.storage.from_("new_app").upload(
    #             filename,
    #             nieuwe_foto.read(),
    #             file_options={"content-type": "image/jpeg", "x-upsert": "true"}
    #         )
        
    #         # Insert metadata row
    #         supabase.table("new_app_quickscan_fotos").insert({
    #             "quickscan_id": qs["id"],
    #             "foto_pad": filename,
    #             "beschrijving": "",
    #             "soortgroep": []
    #         }).execute()
        
    #         st.success("Foto geüpload.")
            
    #        # Reset uploader key to clear the file
    #         st.session_state.upload_key = f"upload_{qs['id']}_{uuid.uuid4()}"
            
    #         st.rerun()

        
    #     # -----------------------------
    #     # 6. Opslaan
    #     # -----------------------------

        

    #     if st.button("Quickscan opslaan"):
    #         with st.spinner("Quickscan wordt opgeslagen…"):
    #             update_data = {
    #                 "naam": naam,
    #                 "opmerking": opmerking,
    #                 "datum": str(datum),
    #                 "veldwerker": veldwerker,
    #                 "starttijd": str(starttijd),
    #                 "eindtijd": str(eindtijd),
    #                 "temperatuur": temperatuur,
    #                 "windsnelheid": windsnelheid,
    #                 "regen": regen,
    #                 "soorten": nieuwe_soorten,
    #             }
            
    #             # Geometrie vervangen indien nieuwe getekend
    #             if nieuwe_geojson:
    
    #                 import json
                    
    #                 data = json.dumps(nieuwe_geojson).encode("utf-8")
    #                 path = f"quickscan/geometries/{qs['id']}.geojson"
    #                 supabase.storage.from_("new_app").upload(
    #                     path,
    #                     data,
    #                     file_options={"content-type": "application/geo+json", "x-upsert": "true"}
    #                 )
    
    
            
    #             supabase.table("new_app_quickscan").update(update_data).eq("id", qs["id"]).execute()
            
    #             st.success("Quickscan bijgewerkt.")
    #             st.session_state.edit_mode = False
    #             st.rerun()

    #     verwijder_quickscan(qs["id"], supabase)

