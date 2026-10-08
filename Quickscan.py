import streamlit as st
from utils.auth import check_password

if check_password():
    st.title("Quickscan")
    st.write("Hier komt de Quickscan module.")
