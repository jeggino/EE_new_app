import streamlit as st

def check_password():
    # Load password from secrets
    PASSWORD = st.secrets["auth"]["password"]

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("Inloggen")
    password = st.text_input("Voer het wachtwoord in:", type="password")

    if st.button("Inloggen"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            return True
        else:
            st.error("Onjuist wachtwoord")

    return False

