import streamlit as st

# Hide sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)


def image_button(label, image_path, page):
    button_html = f"""
        <style>
            .img-button {{
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 18px;
                background-color: #f0f2f6;
                border-radius: 10px;
                border: 1px solid #d3d3d3;
                cursor: pointer;
                transition: 0.2s;
                margin-bottom: 12px;
            }}
            .img-button:hover {{
                background-color: #e0e2e6;
            }}
            .img-button img {{
                width: 50px;
                height: 50px;
            }}
            .img-button span {{
                font-size: 20px;
                font-weight: 500;
            }}
        </style>

        <div class="img-button" onclick="window.location.href='#{page}'">
            <img src="{image_path}">
            <span>{label}</span>
        </div>
    """

    clicked = st.markdown(button_html, unsafe_allow_html=True)
    if clicked:
        st.switch_page(page)
