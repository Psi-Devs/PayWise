import streamlit as st
from dataclasses import dataclass

from modules.detailedView import render_detailed_view
from modules.investView import render_invest_view
from modules.mechanismView import render_mechanism_view
from modules.simpleView import render_simple_view
from utils.calculations import compute_paywise, yearly_view
from utils.pdf_export import generate_pdf_report
from utils.paywise_summary import build_paywise_summary


st.set_page_config(
    page_title="PayWise – Smart EMI Comparison",
    layout="wide",
    page_icon="assets/favicon.png",
)


@dataclass(frozen=True)
class PaywiseInputs:
    view_mode: str
    purchase_amount: int
    interest_rate: float
    tenure: int
    processing_fee_base: float
    fee_type: str
    cashback_full: float
    cashback_emi: float
    cashback_nocost: float
    schedule_view: str


def render_mode_toggle():
    with st.sidebar:
        st.markdown("### Mode")
        mode_invest = st.toggle("PayWise / Invest", value=False)
        mode = "Invest" if mode_invest else "PayWise"

        st.markdown(
            f"<div style='display:flex; justify-content:space-between; font-size:0.9rem; opacity:0.85;'>"
            f"<span style='font-weight:{'700' if mode == 'PayWise' else '400'}'>PayWise</span>"
            f"<span style='font-weight:{'700' if mode == 'Invest' else '400'}'>Invest</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    prev_mode = st.session_state.get("mode", "PayWise")
    mode_changed = mode != prev_mode
    st.session_state["mode"] = mode

    return mode, mode_changed


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


def render_paywise_view(inputs: PaywiseInputs) -> None:
    data = compute_paywise(
        purchase_amount=inputs.purchase_amount,
        interest_rate=inputs.interest_rate,
        tenure=inputs.tenure,
        processing_fee_base=inputs.processing_fee_base,
        fee_mode=inputs.fee_type,
        cashback_full=inputs.cashback_full,
        cashback_emi=inputs.cashback_emi,
        cashback_nocost=inputs.cashback_nocost,
    )

    emi_df = data["emi_df"]
    breakdowns = data["breakdowns"]
    summary = build_paywise_summary(inputs.purchase_amount, inputs.tenure, data)

    if inputs.view_mode == "Simple (For Most People)":
        render_simple_view(
            inputs.purchase_amount,
            summary.full_total,
            summary.normal_total,
            summary.no_cost_total,
            summary.avg_monthly,
            summary.avg_principal,
            summary.avg_interest,
            summary.avg_tax,
            summary.avg_fee,
            emi_df,
            inputs.schedule_view,
            yearly_view,
            breakdowns,
        )
    elif inputs.view_mode == "Detailed (For Learners)":
        render_detailed_view(
            inputs.purchase_amount,
            summary.full_total,
            summary.normal_total,
            summary.no_cost_total,
            summary.avg_monthly,
            summary.avg_principal,
            summary.avg_interest,
            summary.avg_tax,
            summary.avg_fee,
            emi_df,
            inputs.schedule_view,
            inputs.fee_type,
            breakdowns,
        )
    else:
        render_mechanism_view(
            inputs.purchase_amount,
            inputs.interest_rate,
            inputs.tenure,
            inputs.processing_fee_base,
            inputs.fee_type,
            inputs.cashback_full,
            inputs.cashback_emi,
            inputs.cashback_nocost,
            data,
        )

    st.markdown("### 📄 Download")

    pdf_buffer = generate_pdf_report(
        inputs.purchase_amount,
        summary.full_total,
        summary.normal_total,
        summary.no_cost_total,
        summary.total_interest,
        summary.total_gst_interest,
        summary.total_fee_with_gst,
        emi_df,
        breakdowns,
        inputs.fee_type,
    )

    st.download_button(
        label="Download Detailed PDF",
        data=pdf_buffer,
        file_name="PayWise_EMI_Report.pdf",
        mime="application/pdf",
    )


def render_footer() -> None:
    st.markdown(
        "<hr style='opacity:0.2'>"
        "<small style='opacity:0.6'>"
        "© 2025 Psi Dev — PayWise. \n"
        "Independent EMI calculator. Actual charges may vary by bank or merchant."
        "</small>",
        unsafe_allow_html=True,
    )


def main() -> None:
    mode, mode_changed = render_mode_toggle()
    apply_theme(mode)

    if mode == "PayWise":
        inputs = render_paywise_sidebar()
        render_paywise_header()
        render_paywise_view(inputs)
        render_footer()
    else:
        render_invest_view(animate=not mode_changed)


if __name__ == "__main__":
    main()
