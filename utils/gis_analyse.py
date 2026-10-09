import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from branca.element import Element
import base64

def voer_gis_analyse_uit(qs, supabase):
    with st.spinner("GIS‑analyse wordt uitgevoerd..."):


        data = supabase.storage.from_("new_app").download(qs["geometry_path"])
        qs_gdf = gpd.read_file(data).set_crs(4326)



        # -----------------------------
        # 1. Quickscan centroid bepalen
        # -----------------------------
        centroid = qs_gdf.geometry.centroid.iloc[0]
        lat = centroid.y
        lon = centroid.x
        
        # -----------------------------
        # 2. 10 km buffer in graden
        #    (ongeveer 0.1° = 11 km)
        # -----------------------------
        buffer_deg = 0.1
        
        bbox = f"{lon-buffer_deg},{lat-buffer_deg},{lon+buffer_deg},{lat+buffer_deg}"
        
        # -----------------------------
        # 3. Natura2000 gefilterd op 10 km
        # -----------------------------
        url = (
            "https://services.geodataoverijssel.nl/geoserver/B46_natuur_en_landschap/ows?"
            "service=WFS&version=2.0.0&request=GetFeature&"
            "typeName=B46_natuur_en_landschap:B4_Natura_2000-gebieden&"
            f"bbox={bbox},EPSG:4326&"
            "outputFormat=application/json"
        )
        
        n2000 = gpd.read_file(url).to_crs(4326)

        # -----------------------------
        # 3. Centroid + buffer
        # -----------------------------

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
        m = folium.Map(location=[centroid.y, centroid.x], zoom_start=12, zoom_control=False)

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

        # -----------------------------
        # 7. Logo toevoegen
        # -----------------------------
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

        # -----------------------------
        # 8. Legenda toevoegen
        # -----------------------------
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
        .legend-marker {
            background: url('https://cdn-icons-png.flaticon.com/512/2776/2776067.png');
            background-size: cover;
        }
        .legend-circle {
            background: none;
            border: 3px solid #0066ff;
            border-radius: 50%;
        }
        .legend-yellow {
            background: #FFD700;
            border: 2px solid #C9A000;
            border-radius: 4px;
        }
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

        # -----------------------------
        # 9. Kaart tonen
        # -----------------------------
        st_folium(m, width=700, height=500)
