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




    resp = supabase.table("new_app_quickscan").insert({
        "naam": naam,
        "opmerking": opmerking,
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

    filename = f"quickscan/geometries/{qs_id}.geojson"

    supabase.storage.from_(BUCKET).upload(
        filename,
        json.dumps(geojson).encode("utf-8"),
        file_options={"content-type": "application/geo+json", "x-upsert": "true"}
    )

    return qs_id



def save_project(
    naam,
    opmerking,
    opdrachtgever_naam,
    opdrachtgever_telefoon,
    opdrachtgever_email,
    geojson,
    nnn_html=None,
    natura_html=None
):

    if not geojson:
        st.error("Teken eerst een geometrie.")
        st.stop()

    if not naam:
        st.error("Projectnaam ontbreekt.")
        st.stop()

    resp = supabase.table("new_app_quickscan").insert({
        "naam": naam,
        "opmerking": opmerking,

        "opdrachtgever_naam": opdrachtgever_naam,
        "opdrachtgever_telefoon": opdrachtgever_telefoon,
        "opdrachtgever_email": opdrachtgever_email,

        "status": "project"
    }).execute()

    qs_id = resp.data[0]["id"]

    geojson_path = f"quickscan/geometries/{qs_id}.geojson"

    supabase.storage.from_(BUCKET).upload(
        geojson_path,
        json.dumps(geojson).encode("utf-8"),
        file_options={
            "content-type": "application/geo+json",
            "x-upsert": "true"
        }
    )

    nnn_path = None
    natura_path = None

    if nnn_html:

        nnn_path = f"quickscan/html/{qs_id}_nnn.html"

        supabase.storage.from_(BUCKET).upload(
            nnn_path,
            nnn_html.encode("utf-8"),
            file_options={
                "content-type": "text/html",
                "x-upsert": "true"
            }
        )

    if natura_html:

        natura_path = f"quickscan/html/{qs_id}_natura2000.html"

        supabase.storage.from_(BUCKET).upload(
            natura_path,
            natura_html.encode("utf-8"),
            file_options={
                "content-type": "text/html",
                "x-upsert": "true"
            }
        )

    supabase.table("new_app_quickscan") \
        .update({
            "nnn_html_path": nnn_path,
            "natura2000_html_path": natura_path
        }) \
        .eq("id", qs_id) \
        .execute()

    return qs_id
