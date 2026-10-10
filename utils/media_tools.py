import uuid
from utils.supabase_client import supabase

BUCKET = "new_app"

def save_photos(quickscan_id, quickscan_name, photos):
    safe_name = quickscan_name.replace(" ", "_")

    for item in photos:
        file = item["file"]
        beschrijving = item["beschrijving"]
        soortgroepen_foto = item["soortgroepen"]

        # Ensure bytes
        data = file.read() if hasattr(file, "read") else file

        unique_id = str(uuid.uuid4())
        filename = f"quickscan/fotos/{unique_id}.jpg"

        supabase.storage.from_(BUCKET).upload(
            filename,
            data,
            file_options={"content-type": "image/jpeg", "x-upsert": "true"}
        )

        supabase.table("new_app_quickscan_fotos").insert({
            "quickscan_naam": safe_name,
            "foto_pad": filename,
            "beschrijving": beschrijving,
            "soortgroep": soortgroepen_foto,
            "quickscan_id": quickscan_id,
        }).execute()

