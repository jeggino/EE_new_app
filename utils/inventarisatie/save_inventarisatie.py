# utils/inventarisatie/save_inventarisatie.py

import json
from utils.supabase_client import supabase


def save_inventarisatie(
    project_naam: str,
    project_beschrijving: str,
    actief: bool,
    gebruikers: list,
    survey_informatie: dict,
    klant_informatie: dict,
    geometry: dict
):
    """
    Save a new Inventarisatie project into Supabase.
    Step 1: Insert metadata
    Step 2: Upload geometry using project ID as filename
    """

    try:
        # ----------------------------------------------------
        # 1. Insert metadata
        # ----------------------------------------------------
        insert_data = {
            "project_naam": project_naam,
            "project_beschrijving": project_beschrijving,
            "actief": actief,
            "gebruikers": gebruikers,
            "survey_informatie": survey_informatie,
            "klant_informatie": klant_informatie
        }

        insert_resp = supabase.table("new_app_inventarisatie").insert(insert_data).execute()

        # Supabase v2: check error
        if insert_resp.error:
            return {"success": False, "error": insert_resp.error.message}

        # Supabase v2: access data
        project_id = insert_resp.data[0]["id"]

        # ----------------------------------------------------
        # 2. Upload geometry using project_id.json
        # ----------------------------------------------------
        geometry_filename = f"{project_id}.json"
        geometry_json = json.dumps(geometry)

        # encode to bytes for upload
        geometry_bytes = geometry_json.encode("utf-8")

        upload_resp = supabase.storage.from_("new_app").upload(
            path=f"inventarisatie/geometries/{geometry_filename}",
            file=geometry_bytes,
            file_options={"content-type": "application/json"}
        )

        if upload_resp.error:
            return {
                "success": False,
                "error": f"Geometry upload failed: {upload_resp.error.message}"
            }

        # ----------------------------------------------------
        # 3. Success
        # ----------------------------------------------------
        return {
            "success": True,
            "project_id": project_id,
            "geometry_file": geometry_filename
        }


    except Exception as e:
        return {"success": False, "error": str(e)}


