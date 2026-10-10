import streamlit as st

def image_button(label, image_path, page, key):
    # CSS styling
    st.markdown(f"""
        <style>
            .img-button-{key} {{
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
            .img-button-{key}:hover {{
                background-color: #e0e2e6;
            }}
            .img-button-{key} img {{
                width: 50px;
                height: 50px;
            }}
            .img-button-{key} span {{
                font-size: 20px;
                font-weight: 500;
            }}
        </style>
    """, unsafe_allow_html=True)

    # De echte Streamlit knop (onzichtbaar)
    clicked = st.button(
        label=f"{label}",
        key=f"btn_{key}"
    )

    # De visuele HTML knop
    st.markdown(
        f"""
        <div class="img-button-{key}">
            <img src="{image_path}">
            <span>{label}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Als de gebruiker klikt → switch_page
    if clicked:
        st.switch_page(page)

