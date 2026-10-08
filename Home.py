import streamlit as st
from utils.auth import check_password

st.set_page_config(page_title="Ecologisch Advies - Home", page_icon="🌿")

if check_password():

    st.title("Ecologisch Advies Applicatie")
    st.subheader("Kies een module")

    st.page_link("Quickscan.py", label="Quickscan", icon="🗺️")
    st.page_link("Inventarisatie.py", label="Inventarisatie", icon="📋")
    st.page_link("Control.py", label="Control", icon="🔍")
