# utils/inventarisatie/save_inventarisatie.py

import json
from utils.supabase_client import supabase


def _resp_error(resp):
    try:
        if hasattr(resp, "error") and resp.error:
            return getattr(resp.error, "message", str(resp.error))
        if isinstance(resp, dict) and "error" in resp and resp["error"]:
            err = resp["error"]
            return err.get("message") if isinstance(err, dict) else str(err)
    except Exception:
        pass
    return None


def _resp_data(resp):
    try:
        if hasattr(resp, "data") and resp.data is not None:
            return resp.data
        if isinstance(resp, dict) and "data" in resp:
            return resp["data"]
    except Exception:
        pass
    return None


def save_inventarisatie(
    project_naam: str,
    project_beschrijving: str,
    actief: bool,
    gebruikers: list,
    survey_informatie: dict,
    klant_informatie: dict,
    geometry: dict
):

    # ----------------------------------------------------
    # 0. Prevent duplicate project names (simple version)
    # ----------------------------------------------------
    existing = supabase.table("new_app_inventarisatie") \
        .select("project_naam") \
        .eq("project_naam", project_naam) \
        .execute()

    existing_data = _resp_data(existing)

    if existing_data and len(existing_data) > 0:
        return {
            "success": False,
            "error": f"Er bestaat al een project met de naam '{project_naam}'."
        }

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
        print("INSERT RESP:", insert_resp)

        err = _resp_error(insert_resp)
        if err:
            return {"success": False, "error": f"Insert failed: {err}"}

        data = _resp_data(insert_resp)
        if not data or not isinstance(data, list) or not data[0].get("id"):
            return {"success": False, "error": "Insert succeeded but no ID returned."}

        project_id = data[0]["id"]

        # ----------------------------------------------------
        # 2. Upload geometry using project_id.json
        # ----------------------------------------------------
        geometry_filename = f"{project_id}.json"

        try:
            geometry_json = json.dumps(geometry)
        except Exception as e:
            return {"success": False, "error": f"Geometry not JSON-serializable: {e}"}

        geometry_bytes = geometry_json.encode("utf-8")

        upload_resp = supabase.storage.from_("new_app").upload(
            path=f"inventarisatie/geometries/{geometry_filename}",
            file=geometry_bytes
        )

        print("UPLOAD RESP:", upload_resp)

        err_up = _resp_error(upload_resp)
        if err_up:
            return {"success": False, "error": f"Geometry upload failed: {err_up}"}

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







