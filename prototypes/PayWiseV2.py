# =====================================================
# IMPORTS
# =====================================================
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import io

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="PayWise – Smart EMI Comparison",
    layout="wide"
)

GST = 0.18


# =====================================================
# EMI CORE LOGIC
# =====================================================
def calculate_emi(principal, annual_rate, months):
    r = annual_rate / 12 / 100
    if r == 0:
        return principal / months
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)


def generate_emi_schedule(
    principal,
    annual_rate,
    months,
    processing_fee
):
    emi = calculate_emi(principal, annual_rate, months)
    balance = principal
    rows = []

    for m in range(1, months + 1):
        interest = balance * (annual_rate / 12 / 100)
        gst = interest * GST
        principal_paid = emi - interest
        balance -= principal_paid

        rows.append({
            "Month": m,
            "Principal Paid": principal_paid,
            "Interest": interest,
            "GST on Interest (@18%)": gst,
            "Processing Fee": processing_fee if m == 1 else 0,
            "Total Payment": emi + gst + (processing_fee if m == 1 else 0),
            "Principal Remaining": max(balance, 0),
        })

    return pd.DataFrame(rows), emi


def yearly_view(df):
    return (
        df.groupby((df.index // 12) + 1)
        .sum()
        .reset_index(drop=True)
    )


# =====================================================
# DONUT CHART
# =====================================================
def render_donut(principal, interest, tax, fee, title):
    fig, ax = plt.subplots(figsize=(4, 4))
    values = [principal, interest, tax, fee]
    labels = ["Principal", "Interest", "Tax", "Fees"]

    ax.pie(
        values,
        labels=labels,
        startangle=90,
        colors=["#4c72b0", "#dd8452", "#c44e52", "#8172b2"]
    )
    centre = plt.Circle((0, 0), 0.65, fc="white")
    ax.add_artist(centre)
    ax.text(
        0, 0,
        f"{sum(values):,.0f}",
        ha="center",
        va="center",
        fontsize=11,
        weight="bold"
    )
    ax.set_title(title)
    st.pyplot(fig)


# =====================================================
# SESSION STATE
# =====================================================
if "scenarios" not in st.session_state:
    st.session_state.scenarios = {}


# =====================================================
# TOP INTRO
# =====================================================
st.markdown("""
## 💳 PayWise  
### *Make smarter payment decisions.*

Compare **Full Payment**, **Normal EMI**, and **No-Cost EMI**  
with **GST, fees, cashback, and clear breakdowns**.
""")


# =====================================================
# SIDEBAR — VIEW MODE
# =====================================================
with st.sidebar:
    st.markdown("### View Mode")
    view_mode = st.radio(
        "Experience",
        ["Simple (Recommended)", "Detailed Breakdown"]
    )

    st.markdown("### Purchase Details")

    purchase_amount = st.number_input(
        "Purchase Amount (₹)",
        1_000, 50_00_000, 50_000, step=1_000
    )

    interest_rate = st.number_input(
        "Interest Rate (% p.a.)",
        0.0, 40.0, 15.0, step=0.25
    )

    tenure = st.selectbox(
        "Tenure (months)",
        [3, 6, 9, 12, 18, 24, 36]
    )

    # Processing Fee
    st.markdown("### Processing Fee")

    if view_mode == "Detailed Breakdown":
        fee_type = st.radio("Fee Type", ["Fixed", "Percentage"])
        if fee_type == "Fixed":
            fee_base = st.number_input("Fee Amount (₹)", 0, 5000, 199)
        else:
            fee_base = purchase_amount * st.number_input(
                "Fee (%)", 0.0, 5.0, 1.0, step=0.1
            ) / 100
    else:
        fee_base = st.number_input("Fee Amount (₹)", 0, 5000, 199)

    processing_fee = fee_base * (1 + GST)

    # Cashback
    st.markdown("### Cashback (Optional)")

    if view_mode == "Detailed Breakdown":
        cashback_full = st.number_input("Full Payment Cashback", 0, 50000, 0)
        cashback_emi = st.number_input("Normal EMI Cashback", 0, 50000, 0)
        cashback_nocost = st.number_input("No-Cost EMI Cashback", 0, 50000, 0)
    else:
        cashback_full = cashback_emi = cashback_nocost = 0

    schedule_view = st.radio(
        "Schedule View",
        ["Monthly", "Yearly"]
    )


# =====================================================
# CALCULATIONS
# =====================================================
emi_df, emi_value = generate_emi_schedule(
    purchase_amount,
    interest_rate,
    tenure,
    processing_fee
)

total_interest = emi_df["Interest"].sum()
total_tax = emi_df["GST on Interest (@18%)"].sum()

normal_total = emi_df["Total Payment"].sum() - cashback_emi
no_cost_total = purchase_amount + total_tax + processing_fee - cashback_nocost
full_total = purchase_amount + processing_fee - cashback_full

avg_monthly = normal_total / tenure
avg_principal = purchase_amount / tenure
avg_interest = total_interest / tenure
avg_tax = total_tax / tenure


# =====================================================
# COST SUMMARY
# =====================================================
st.markdown("### 📌 Cost Summary")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Full Payment", f"{full_total:,.0f}")
    st.caption("One-time payment")

with c2:
    st.metric("Normal EMI", f"{normal_total:,.0f}")
    st.caption(
        f"~₹{avg_monthly:,.0f}/month  "
        f"(₹{avg_principal:,.0f} + ₹{avg_interest:,.0f} + "
        f"₹{avg_tax:,.0f} tax)"
    )

with c3:
    st.metric("No-Cost EMI", f"{no_cost_total:,.0f}")
    st.caption("Interest discounted, taxes & fees apply")

st.caption(
    "ℹ️ No-Cost EMI assumes interest is discounted by the merchant. "
    "GST and processing fees still apply."
)


# =====================================================
# DONUT (STAGED)
# =====================================================
st.markdown("### 📊 Cost Breakdown")

selected_method = st.radio(
    "View breakdown for",
    ["Normal EMI", "No-Cost EMI", "Full Payment"],
    horizontal=True
)

if selected_method == "Normal EMI":
    render_donut(
        purchase_amount,
        total_interest,
        total_tax,
        processing_fee,
        "Normal EMI Breakdown"
    )

elif selected_method == "No-Cost EMI":
    render_donut(
        purchase_amount,
        0,
        total_tax,
        processing_fee,
        "No-Cost EMI Breakdown"
    )

else:
    render_donut(
        purchase_amount,
        0,
        0,
        processing_fee,
        "Full Payment Breakdown"
    )


# =====================================================
# PAYMENT SCHEDULE
# =====================================================
st.markdown("### 📅 Payment Schedule")

display_df = emi_df if schedule_view == "Monthly" else yearly_view(emi_df)

if view_mode == "Simple (Recommended)":
    display_df = display_df[[
        "Month" if "Month" in display_df.columns else display_df.columns[0],
        "Total Payment",
        "Principal Remaining"
    ]]

st.dataframe(
    display_df.style.format("{:,.0f}")
)


# =====================================================
# SAVE SCENARIO
# =====================================================
st.markdown("### 💾 Save Scenario")

scenario_name = st.text_input("Scenario Name")

if st.button("Save Scenario") and scenario_name:
    st.session_state.scenarios[scenario_name] = {
        "summary": {
            "Full Payment": full_total,
            "Normal EMI": normal_total,
            "No-Cost EMI": no_cost_total
        }
    }
    st.success("Scenario saved")


# =====================================================
# DISCLAIMER
# =====================================================
st.markdown("""
### ⚠️ Disclaimer

PayWise is for **educational purposes only**.  
Actual EMI terms depend on banks, card issuers, and merchant offers.
""")
