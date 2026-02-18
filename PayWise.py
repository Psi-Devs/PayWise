import streamlit as st

from _internal.dark import render_app as render_dark_app
from _internal.light import render_app as render_light_app


def detect_theme() -> str:
    theme_info = getattr(st.context, "theme", {}) or {}
    theme_type = theme_info.get("type")
    if theme_type in {"light", "dark"}:
        return theme_type

    base = st.get_option("theme.base")
    if base in {"light", "dark"}:
        return base

    return "dark"


def _check_theme_and_rerun() -> None:
    current = detect_theme()
    previous = st.session_state.get("_active_theme")

    if previous is None:
        st.session_state["_active_theme"] = current
        return

    if previous != current:
        st.session_state["_active_theme"] = current
        st.rerun()


if hasattr(st, "fragment"):

    @st.fragment(run_every="1s")
    def watch_theme_changes() -> None:
        _check_theme_and_rerun()

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


def render_paywise_sidebar() -> PaywiseInputs:
    with st.sidebar:
        view_mode = st.radio(
            "Experience",
            [
                "Simple (For Most People)",
                "Detailed (For Learners)",
                "Mechanism (How It Works)",
            ],
        )

        purchase_amount = st.number_input(
            "Purchase Amount (₹)", 1_000, 100_00_000, 20_000, step=1_000
        )
        interest_rate = st.number_input(
            "Interest Rate (% p.a.)", 0.0, 40.0, 12.0, step=0.05
        )

        tenure = st.number_input(
            "Tenure (months)",
            min_value=3,
            max_value=360,
            value=6,
            step=1,
        )
        st.caption("Minimum 3 months")

        st.markdown("### Processing Fee")
        fee_type = st.radio("Fee Type", ["Fixed", "Percentage"], horizontal=True)

        if fee_type == "Fixed":
            processing_fee_base = st.number_input("Processing Fee (₹)", 0, 5000, 299)
            st.caption("Fixed fee is charged upfront in month 1.")
        else:
            fee_pct = st.number_input("Processing Fee (%)", 0.0, 5.0, 1.0, step=0.1)
            processing_fee_base = purchase_amount * fee_pct / 100
            st.caption("Percentage fee is financed (added to principal with GST).")

        cashback_full = st.number_input("Full Payment Cashback", 0, 50_000, 0)
        cashback_emi = st.number_input("Normal EMI Cashback", 0, 50_000, 0)
        cashback_nocost = st.number_input("No-Cost EMI Cashback", 0, 50_000, 0)

        schedule_view = st.radio("Schedule View", ["Monthly", "Yearly"])

    return PaywiseInputs(
        view_mode=view_mode,
        purchase_amount=purchase_amount,
        interest_rate=interest_rate,
        tenure=tenure,
        processing_fee_base=processing_fee_base,
        fee_type=fee_type,
        cashback_full=cashback_full,
        cashback_emi=cashback_emi,
        cashback_nocost=cashback_nocost,
        schedule_view=schedule_view,
    )


def render_paywise_header() -> None:
    st.markdown("## 💳 PayWise \n### *Make smarter payment decisions.*")

    def watch_theme_changes() -> None:
        _check_theme_and_rerun()


def main() -> None:
    st.set_page_config(
        page_title="PayWise – Smart EMI Comparison",
        layout="wide",
        page_icon="assets/favicon.png",
    )

    watch_theme_changes()

    if detect_theme() == "light":
        render_light_app()
    else:
        render_dark_app()


if __name__ == "__main__":
    main()
