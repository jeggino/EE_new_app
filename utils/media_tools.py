import uuid
from utils.supabase_client import supabase

BUCKET = "new_app"

def save_photos(quickscan_id, photos):

    for item in photos:
        file = item["file"]
        beschrijving = item["beschrijving"]
        soortgroepen_foto = item["soortgroepen"]

        # Reset file pointer so multiple reads work
        if hasattr(file, "read"):
            file.seek(0)
            data = file.read()
        else:
            data = file

        unique_id = str(uuid.uuid4())
        filename = f"quickscan/fotos/{unique_id}.jpg"

        supabase.storage.from_(BUCKET).upload(
            filename,
            data,
            file_options={"content-type": "image/jpeg", "x-upsert": "true"}
        )

        supabase.table("new_app_quickscan_fotos").insert({
            "foto_pad": filename,
            "beschrijving": beschrijving,
            "soortgroep": soortgroepen_foto,   # your list stays a list
            "quickscan_id": quickscan_id,
        }).execute()

