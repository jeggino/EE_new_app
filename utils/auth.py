import streamlit as st
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

# ----------------- INIT -----------------
@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# ----------------- SESSION DEFAULTS -----------------
DEFAULTS = {
    "logged_in": False,
    "user": None,
    "session": None,
    "show_signup": False,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ----------------- AUTH FUNCTIONS -----------------
def login(email: str, password: str):
    try:
        res = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        return res
    except Exception:
        return None


def logout():
    supabase.auth.sign_out()
    st.session_state.clear()
    for k, v in DEFAULTS.items():
        st.session_state[k] = v
    st.rerun()


def restore_session():
    """
    Ensures the user stays logged in after refresh.
    Supabase automatically persists the session in the browser.
    """
    session = supabase.auth.get_session()

    if session and session.user:
        st.session_state.logged_in = True
        st.session_state.user = session.user
        st.session_state.session = session
    else:
        st.session_state.logged_in = False


# ----------------- UI: LOGIN -----------------
def show_login():
    st.sidebar.title("Login")

    with st.sidebar.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            res = login(email, password)
            if res and res.user:
                st.session_state.logged_in = True
                st.session_state.user = res.user
                st.session_state.session = res.session
                st.rerun()
            else:
                st.sidebar.error("Invalid email or password")

    if st.sidebar.button("Create Account"):
        st.session_state.show_signup = True
        st.rerun()


# ----------------- UI: SIGNUP -----------------
def show_signup():
    st.sidebar.title("Create Account")

    with st.sidebar.form("signup_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        full_name = st.text_input("Full Name")
        category = st.selectbox("Category", ["beginner", "senior"])
        role = st.selectbox("Role", ["guest", "user", "creator"])

        submitted = st.form_submit_button("Create Account")

        if submitted:
            try:
                supabase.auth.admin.create_user({
                    "email": email,
                    "password": password,
                    "user_metadata": {
                        "full_name": full_name,
                        "category": category,
                        "role": role
                    }
                })
                st.success("Account created! You can now log in.")
                st.session_state.show_signup = False
                st.rerun()
            except Exception as e:
                st.error(f"Error creating account: {e}")

    if st.sidebar.button("Back to Login"):
        st.session_state.show_signup = False
        st.rerun()


# ----------------- MAIN AUTH HANDLER -----------------
def auth_gate(app_function):
    """
    Wrap your app with this function:
    - Restores session
    - Shows login/signup if needed
    - Runs your app when logged in
    """

    restore_session()

    if not st.session_state.logged_in:
        if st.session_state.show_signup:
            show_signup()
        else:
            show_login()
    else:
        app_function()


