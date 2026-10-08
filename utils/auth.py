import streamlit as st
import time

def check_password():
    PASSWORD = st.secrets["auth"]["password"]

    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.login_time = None

    # If already authenticated, keep user logged in
    if st.session_state.authenticated:
        return True

    # Login UI
    st.title("Inloggen")
    password = st.text_input("Voer het wachtwoord in:", type="password")

    if st.button("Inloggen"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.session_state.login_time = time.time()
            return True
        else:
            st.error("Onjuist wachtwoord")

    return False


