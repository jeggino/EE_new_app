import streamlit as st

@st.dialog("💸")
def money_dialog():

    st.image(
        "https://i.makeagif.com/media/5-28-2018/lVOI3M.gif",
        use_container_width=True
    )

    st.markdown(
        """
        <div style="text-align:center;">
            <h1>💰 MONEY MONEY MONEY 💰</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
