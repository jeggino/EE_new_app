import json
import streamlit as st
from utils.supabase_client import supabase, BUCKET

def save_quickscan(project_name,description,geojson,datum,veldwerker,starttijd,eindtijd,temperatuur,windsnelheid,regen):

    if not geojson:
        st.error("Teken eerst een geometrie.")
        st.stop()

    if not project_name:
        st.error("Projectnaam ontbreekt.")
        st.stop()


    safe_name = project_name.replace(" ", "_")
    filename = f"quickscan/geometries/{safe_name}.geojson"

    supabase.storage.from_(BUCKET).upload(
        filename,
        json.dumps(geojson).encode("utf-8"),
        file_options={"content-type": "application/geo+json", "x-upsert": "true"}
    )

    supabase.table("new_app_quickscan").insert({
        "name": project_name.replace(" ", "_"),
        "description": description,
        "geometry_path": filename,
        "datum": datum.isoformat(),
        "veldwerker": veldwerker,
        "starttijd": starttijd.strftime("%H:%M:%S"),
        "eindtijd": eindtijd.strftime("%H:%M:%S"),
        "temperatuur": temperatuur,
        "windsnelheid": windsnelheid,
        "regen": regen
    }).execute()

