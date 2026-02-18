import streamlit as st

from app_core import run_app


def apply_theme(mode: str) -> None:
    theme_bg = "#0f0f1a" if mode == "PayWise" else "#0b1416"
    accent = "#ff4d5a" if mode == "PayWise" else "#2bb673"
    toggle_bg = "#2b2f3a" if mode == "PayWise" else "#1c2a2e"

    st.markdown(
        f"""
        <style>
        body {{ background-color: {theme_bg}; transition: background-color 0.25s ease-in-out; }}
        .stApp {{ background-color: {theme_bg}; transition: background-color 0.25s ease-in-out; }}
        section[data-testid="stSidebar"] {{
            background-color: {toggle_bg};
            transition: background-color 0.25s ease-in-out;
        }}
        [data-testid="stToggle"] {{
            transform: scale(1.55);
            transform-origin: left center;
            margin-bottom: 4px;
        }}
        [data-testid="stToggle"] > label {{
            background: transparent !important;
        }}
        [data-testid="stToggle"] div[role="switch"] {{
            width: 96px !important;
            height: 44px !important;
            border-radius: 999px !important;
            background: {toggle_bg} !important;
            position: relative !important;
            box-shadow: 0 6px 18px rgba(0,0,0,0.35);
            transition: all 0.3s ease-in-out;
        }}
        [data-testid="stToggle"] div[role="switch"]::after {{
            content: "PayWise";
            position: absolute;
            right: 10px;
            top: 12px;
            font-size: 11px;
            color: #f1f1f1;
            letter-spacing: 0.3px;
            opacity: 0.85;
            transition: all 0.3s ease-in-out;
        }}
        [data-testid="stToggle"] input:checked + div[role="switch"]::after {{
            content: "Invest";
            left: 8px;
            right: auto;
        }}
        [data-testid="stToggle"] div[role="switch"]::before {{
            width: 36px !important;
            height: 36px !important;
            left: 4px !important;
            top: 4px !important;
            background: #f4f4f4 !important;
            border-radius: 999px !important;
            box-shadow: 0 6px 12px rgba(0,0,0,0.25);
            transition: all 0.3s ease-in-out;
        }}
        [data-testid="stToggle"] input:checked + div[role="switch"]::before {{
            transform: translateX(48px);
        }}
        [data-testid="stToggle"] input:checked + div[role="switch"] {{
            background: {accent} !important;
        }}
        [data-testid="stSlider"] div[role="slider"] {{
            transition: all 0.25s ease-in-out;
        }}
        [data-testid="stSlider"] [data-baseweb="slider"] > div {{
            padding-top: 4px;
            padding-bottom: 4px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_app() -> None:
    run_app(apply_theme=apply_theme)


def main() -> None:
    st.set_page_config(
        page_title="PayWise – Smart EMI Comparison",
        layout="wide",
        page_icon="assets/favicon.png",
    )
    render_app()


if __name__ == "__main__":
    main()

