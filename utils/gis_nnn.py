import folium
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import transform
import pyproj
import base64
from branca.element import Element
from streamlit_folium import st_folium
from utils.supabase_client import supabase

RD = "EPSG:28992"
WGS = "EPSG:4326"

project_to_rd = pyproj.Transformer.from_crs(WGS, RD, always_xy=True).transform
project_to_wgs = pyproj.Transformer.from_crs(RD, WGS, always_xy=True).transform


def flatten_geometry(gdf):
    def flatten(geom):
        if geom is None:
            return None
        if geom.has_z:
            if geom.geom_type == "Polygon":
                exterior = [(x, y) for (x, y, *_) in geom.exterior.coords]
                interiors = [
                    [(x, y) for (x, y, *_) in ring.coords]
                    for ring in geom.interiors
                ]
                return Polygon(exterior, interiors)
            elif geom.geom_type == "MultiPolygon":
                return MultiPolygon([flatten(p) for p in geom.geoms])
        return geom

    gdf["geometry"] = gdf["geometry"].apply(flatten)
    return gdf


def load_nnn_cached():
    # Cache key
    key = "cached_nnn_gdf"

    # If already loaded, return cached version
    if key in st.session_state:
        return st.session_state[key]

    # Otherwise load from Supabase
    file_bytes = supabase.storage.from_("new_app").download(
        "quickscan/data/inspire-pv-ps.nlps-nnn.gml"
    )

    gdf = gpd.read_file(file_bytes, driver="GML")
    gdf = gdf.set_crs("EPSG:3035", allow_override=True)
    gdf = gdf.to_crs("EPSG:28992")
    gdf = flatten_geometry(gdf)

    # Store in cache
    st.session_state[key] = gdf

    return gdf



def voer_gis_analyse_nnn(qs):
    # Load Quickscan polygon
    geometry_path = f"quickscan/geometries/{qs['id']}.geojson"
    data = supabase.storage.from_("new_app").download(geometry_path)
    qs_gdf = gpd.read_file(data).set_crs(WGS)

    # Centroid
    centroid = qs_gdf.geometry.centroid.iloc[0]
    lat = centroid.y
    lon = centroid.x

    # Convert centroid to RD
    x_rd, y_rd = transform(project_to_rd, Point(lon, lat)).coords[0]

    # Load NNN from Supabase
    nnn = load_nnn_cached()


    # Bounding box (10 km)
    bbox = Point(x_rd, y_rd).buffer(10000)
    nnn_filtered = nnn[nnn.intersects(bbox)]

    # Convert to WGS
    nnn_wgs = nnn_filtered.to_crs(WGS)

    # Create 1 km buffer
    buffer_nnn = Point(x_rd, y_rd).buffer(1000)
    buffer_nnn_wgs = transform(project_to_wgs, buffer_nnn)

    # Build map
    m = folium.Map(
        location=[lat, lon],
        zoom_start=11,
        control_scale=True,
        zoom_control=False,
        tiles="https://api.mapbox.com/styles/v1/jeggino/cmhdim6mj005g01s618ln55m2/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiamVnZ2lubyIsImEiOiJjbHdscmRkZHAxMTl1MmlyeTJpb3Z2eHdzIn0.N9TRN7xxTikk235dVs1YeQ",
        attr="Mapbox"
    )

    layer_nnn = folium.FeatureGroup(name="NNN", show=True)
    layer_buffers = folium.FeatureGroup(name="Buffers", show=True)

    # Add NNN polygons
    for _, row in nnn_wgs.iterrows():
        folium.GeoJson(
            row.geometry.__geo_interface__,
            style_function=lambda x: {
                "color": "green",
                "weight": 2,
                "fillColor": "green",
                "fillOpacity": 0.3
            }
        ).add_to(layer_nnn)

    # Add buffer
    folium.GeoJson(
        buffer_nnn_wgs,
        style_function=lambda x: {
            "color": "blue",
            "weight": 2,
            "fillOpacity": 0.1
        },
        tooltip="1 km NNN buffer"
    ).add_to(layer_buffers)

    # Add centroid marker
    folium.Marker(
        [lat, lon],
        popup="Centroid Quickscan",
        icon=folium.Icon(color="blue", icon="home", prefix="fa")
    ).add_to(m)

    layer_nnn.add_to(m)
    layer_buffers.add_to(m)

    # Legend
    legend_html = """
    <div style="
        position: fixed;
        top: 15px;
        left: 15px;
        width: 150px;
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid #444;
        border-radius: 6px;
        padding: 8px;
        z-index: 9999;
        font-size: 12px;
        color: black;
    ">
    <i class="fa fa-home" style="color: blue;"></i> Locatie<br><br>
    <span style="color: blue;">&#9608;</span> 1 km buffer<br>
    <span style="color: green;">&#9608;</span> NNN gebied<br>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))


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

    # # -----------------------------
    # # Shrink & simplify the scale bar (Leaflet control)
    # # -----------------------------
    # scale_css = """
    # <style>
    # /* Make the scale bar smaller */
    # .leaflet-control-scale {
    #     font-size: 11px !important;
    #     line-height: 11px !important;
    #     padding: 2px !important;
    # }
    
    # /* Style the metric line (keep it visible) */
    # .leaflet-control-scale-line {
    #     border: 1px solid #000 !important;
    #     padding: 2px 4px !important;
    #     background: rgba(255,255,255,0.9) !important;
    #     color: #000 !important;
    # }
    
    # /* Hide the imperial (feet) line ONLY */
    # .leaflet-control-scale-line.leaflet-control-scale-line-imperial {
    #     display: none !important;
    # }
    
    # /* Reduce spacing */
    # .leaflet-control-scale-line:not(.leaflet-control-scale-line-imperial) {
    #     margin-top: 0px !important;
    # }
    # </style>
    # """
    
    # m.get_root().html.add_child(folium.Element(scale_css))





    # Display in Streamlit
    st_folium(m, width=700, height=500, returned_objects=[])


