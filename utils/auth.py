import streamlit as st
import time

# def check_password():
#     PASSWORD = st.secrets["auth"]["password"]

#     # Initialize session state
#     if "authenticated" not in st.session_state:
#         st.session_state.authenticated = False
#         st.session_state.login_time = None

#     # If already authenticated, keep user logged in
#     if st.session_state.authenticated:
#         return True

#     # Login UI
#     st.title("Inloggen")
#     password = st.text_input("Voer het wachtwoord in:", type="password")

#     if st.button("Inloggen"):
#         if password == PASSWORD:
#             st.session_state.authenticated = True
#             st.session_state.login_time = time.time()
#             return True
#         else:
#             st.error("Onjuist wachtwoord")

#     return False

# utils/auth.py

import streamlit as st
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_password():
    # Als er al een geldige Supabase sessie is → ingelogd blijven
    if "supabase_session" in st.session_state and st.session_state.supabase_session:
        return True

    # Login formulier
    email = st.text_input("Email")
    password = st.text_input("Wachtwoord", type="password")

    if st.button("Login"):
        try:
            data = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            # Sessie opslaan
            st.session_state.supabase_session = data.session
            st.session_state.user = data.user

            st.rerun()
            return True

        except Exception:
            st.error("Login mislukt")
            return False

    return False

def logout():
    supabase.auth.sign_out()
    st.session_state.supabase_session = None
    st.session_state.user = None
    st.rerun()


