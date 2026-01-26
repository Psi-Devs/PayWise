import streamlit as st

st.set_page_config(
    page_title="PayWise – Smart EMI Comparison",
    layout="wide",
    page_icon="assets/favicon.png",  # 👈 THIS
)


from utils.calculations import generate_emi_schedule, yearly_view
from modules.simpleView import render_simple_view
from modules.detailedView import render_detailed_view
from state.scenarios import init_scenarios, save_scenario
from utils.pdf_export import generate_pdf_report

# ---------------- UI THEME ----------------
st.markdown(
    """
    <style>
    body { background-color: #0f0f1a; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.set_page_config(page_title="PayWise – Smart EMI Comparison", layout="wide")
init_scenarios()

st.markdown("## 💳 PayWise \n### *Make smarter payment decisions.*")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    view_mode = st.radio("Experience", ["Simple (Recommended)", "Detailed Breakdown"])

    purchase_amount = st.number_input(
        "Purchase Amount (₹)", 1_000, 100_00_000, 20_000, step=1_000
    )
    interest_rate = st.number_input(
        "Interest Rate (% p.a.)", 0.0, 40.0, 16.0, step=0.05
    )

    tenure = st.number_input(
        "Tenure (months)",
        min_value=3,
        max_value=360,
        value=6,
        step=1        
    )
    st.caption("Minimum 3 months")

    st.markdown("### Processing Fee")

    fee_type = st.radio("Fee Type", ["Fixed", "Percentage"], horizontal=True)

    if fee_type == "Fixed":
        processing_fee_base = st.number_input("Processing Fee (₹)", 0, 5000, 299)
    else:
        fee_pct = st.number_input("Processing Fee (%)", 0.0, 5.0, 1.0, step=0.1)
        processing_fee_base = purchase_amount * fee_pct / 100

    cashback_full = st.number_input("Full Payment Cashback", 0, 50_000, 0)
    cashback_emi = st.number_input("Normal EMI Cashback", 0, 50_000, 0)
    cashback_nocost = st.number_input("No-Cost EMI Cashback", 0, 50_000, 0)

    schedule_view = st.radio("Schedule View", ["Monthly", "Yearly"])

# ---------------- CALCULATIONS ----------------
emi_df, emi_value = generate_emi_schedule(
    purchase_amount, interest_rate, tenure, processing_fee_base
)

total_interest = emi_df["Interest"].sum()
total_gst_interest = emi_df["GST on Interest (@18%)"].sum()

total_processing_fee = emi_df["Processing Fee"].sum()
total_gst_processing_fee = emi_df["GST on Processing Fee (@18%)"].sum()

total_fee_with_gst = total_processing_fee + total_gst_processing_fee

normal_total = emi_df["Total Payment"].sum() - cashback_emi

no_cost_total = (
    purchase_amount
    + total_gst_interest
    + total_fee_with_gst
    - cashback_nocost
)

full_total = purchase_amount - cashback_full

avg_monthly = normal_total / tenure
avg_principal = purchase_amount / tenure
avg_interest = total_interest / tenure

avg_tax = total_gst_interest / tenure   # ✅ FIXED

# ---------------- RENDER ----------------
if view_mode == "Simple (Recommended)":
    render_simple_view(
        purchase_amount,
        full_total,
        normal_total,
        no_cost_total,
        avg_monthly,
        avg_principal,
        avg_interest,
        avg_tax,
        total_interest,
        total_gst_interest,
        total_fee_with_gst,
        emi_df,
        schedule_view,
        yearly_view,
    )
else:
    render_detailed_view(
        purchase_amount,
        full_total,
        normal_total,
        no_cost_total,    
        avg_monthly,
        avg_principal,
        avg_interest,
        avg_tax,
        total_interest,
        total_gst_interest,
        total_fee_with_gst,
        emi_df,
        schedule_view,
    )

st.markdown("### 📄 Download")

pdf_buffer = generate_pdf_report(
    purchase_amount,
    full_total,
    normal_total,
    no_cost_total,
    total_interest,
    total_gst_interest,
    total_fee_with_gst,
    emi_df,
)

st.download_button(
    label="Download Detailed PDF",
    data=pdf_buffer,
    file_name="PayWise_EMI_Report.pdf",
    mime="application/pdf",
)



st.markdown(
    "<hr style='opacity:0.2'>"
    "<small style='opacity:0.6'>"
    "© 2025 Psi Dev — PayWise. \n"
    "Independent EMI calculator. Actual charges may vary by bank or merchant."
    "</small>",
    unsafe_allow_html=True,
)


