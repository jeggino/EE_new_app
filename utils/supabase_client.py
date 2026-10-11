from supabase import create_client
import streamlit as st

url = st.secrets["supabase"]["url"]
anon_key = st.secrets["supabase"]["key"]
service_role_key = st.secrets["supabase"]["service_role_key"]

# Normal client (anon key)
supabase = create_client(url, anon_key)

# Admin client (service-role key)
supabase_admin = create_client(url, service_role_key)

BUCKET = "new_app"

def ensure_bucket():
    buckets = supabase.storage.list_buckets()
    names = [b["name"] for b in buckets]

    if BUCKET not in names:
        supabase.storage.create_bucket(BUCKET, public=True)
