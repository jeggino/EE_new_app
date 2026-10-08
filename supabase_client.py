from supabase import create_client
import streamlit as st

url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]

supabase = create_client(url, key)

BUCKET = "new_app"

def ensure_bucket():
    buckets = supabase.storage.list_buckets()
    names = [b["name"] for b in buckets]

    if BUCKET not in names:
        supabase.storage.create_bucket(BUCKET, public=True)
