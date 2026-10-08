import streamlit as st
from utils.auth import check_password

if check_password():
    st.title("Inventarisatie")
    st.write("Hier komt de Inventarisatie module.")
