import streamlit as st
from utils.auth import check_password

if check_password():
    st.title("Control")
    st.write("Hier komt de Control module.")
