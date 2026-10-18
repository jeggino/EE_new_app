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
    Step 1: Insert metadata (without geometry)
    Step 2: Upload geometry using project ID as filename
    Step 3: Update row with geometry filename
    """

    try:
        # ----------------------------------------------------
        # 1. Insert metadata (geometry_file will be added later)
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

        if "error" in insert_resp:
            return {"success": False, "error": insert_resp["error"]["message"]}

        project_id = insert_resp["data"][0]["id"]

        # ----------------------------------------------------
        # 2. Upload geometry using project_id.json
        # ----------------------------------------------------
        geometry_filename = f"{project_id}.json"
        geometry_json = json.dumps(geometry)

        upload_resp = supabase.storage.from_("new_app").upload(
            path=f"inventarisatie_geometry/{geometry_filename}",
            file=geometry_json,
            file_options={"content-type": "application/json"}
        )

        if upload_resp.get("error"):
            return {
                "success": False,
                "error": f"Geometry upload failed: {upload_resp['error']['message']}"
            }

        # # ----------------------------------------------------
        # # 3. Update row with geometry filename
        # # ----------------------------------------------------
        # update_resp = supabase.table("new_app_inventarisatie").update(
        #     {"geometry_file": geometry_filename}
        # ).eq("id", project_id).execute()

        # if "error" in update_resp:
        #     return {"success": False, "error": update_resp["error"]["message"]}

        # ----------------------------------------------------
        # 4. Success
        # ----------------------------------------------------
        return {
            "success": True,
            "project_id": project_id,
            "geometry_file": geometry_filename
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

