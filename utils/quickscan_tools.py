import json
import streamlit as st
from utils.supabase_client import supabase, BUCKET

def save_quickscan(naam,opmerking,geojson,datum,veldwerker,starttijd,eindtijd,temperatuur,windsnelheid,regen,soorten_results):

    if not geojson:
        st.error("Teken eerst een geometrie.")
        st.stop()

    if not naam:
        st.error("Projectnaam ontbreekt.")
        st.stop()


    safe_name = naam.replace(" ", "_")
    filename = f"quickscan/geometries/{safe_name}.geojson"

    supabase.storage.from_(BUCKET).upload(
        filename,
        json.dumps(geojson).encode("utf-8"),
        file_options={"content-type": "application/geo+json", "x-upsert": "true"}
    )

    resp = supabase.table("new_app_quickscan").insert({
        "naam": naam,
        "opmerking": opmerking,
        "geometry_path": geometry_path,
        "datum": str(datum),
        "veldwerker": veldwerker,
        "starttijd": str(starttijd),
        "eindtijd": str(eindtijd),
        "temperatuur": temperatuur,
        "windsnelheid": windsnelheid,
        "regen": regen,
        "soorten": soorten_results
    }).execute()

    # ⭐ Supabase returns the inserted row
    qs_id = resp.data[0]["id"]

    return qs_id


