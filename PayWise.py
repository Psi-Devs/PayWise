# =====================================================
# IMPORTS
# =====================================================
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="PayWise – Smart EMI Comparison",
    layout="wide"
)

GST = 0.18


# =====================================================
# EMI LOGIC
# =====================================================
def calculate_emi(principal, annual_rate, months):
    r = annual_rate / 12 / 100
    if r == 0:
        return principal / months
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)


def generate_schedule(principal, rate, months, fee_base, fee_tax):
    emi = calculate_emi(principal, rate, months)
    bal = principal
    rows = []

    for m in range(1, months + 1):
        interest = bal * (rate / 12 / 100)
        gst_i = interest * GST
        principal_paid = emi - interest
        bal -= principal_paid

        fee = fee_base if m == 1 else 0
        fee_gst = fee_tax if m == 1 else 0

        rows.append({
            "Month": m,
            "Principal Paid": principal_paid,
            "Interest": interest,
            "GST on Interest": gst_i,
            "Processing Fee": fee,
            "GST on Fee": fee_gst,
            "Total Payment": emi + gst_i + fee + fee_gst,
            "Principal Remaining": max(bal, 0)
        })

    return pd.DataFrame(rows), emi


# =====================================================
# MINI DONUT
# =====================================================
def mini_donut(values, selected):
    fig, ax = plt.subplots(figsize=(1.9, 1.9))
    ax.pie(
        values,
        startangle=90,
        colors=["#4c72b0", "#dd8452", "#c44e52", "#8172b2"]
    )
    ax.add_artist(plt.Circle((0, 0), 0.6, color="white"))

    if not selected:
        ax.patch.set_alpha(0.35)
    else:
        ax.patch.set_edgecolor("#4c72b0")
        ax.patch.set_linewidth(2)

    ax.axis("off")
    st.pyplot(fig)


# =====================================================
# HEADER
# =====================================================
st.markdown("""
## 💳 PayWise  
### *Make smarter payment decisions.*

Compare **Full Payment**, **Normal EMI**, and **No-Cost EMI**  
with **GST, fees, cashback, and transparency**.
""")


# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    view_mode = st.radio(
        "View Mode",
        ["Simple (Recommended)", "Detailed Breakdown"]
    )

    purchase = st.number_input("Purchase Amount (₹)", 1_000, 50_00_000, 50_000, 1_000)
    rate = st.number_input("Interest Rate (% p.a.)", 0.0, 40.0, 15.0, 0.25)
    tenure = st.selectbox("Tenure (months)", [3, 6, 9, 12, 18, 24, 36])

    fee_base = st.number_input("Processing Fee (₹)", 0, 5000, 199)
    fee_tax = fee_base * GST

    if view_mode == "Detailed Breakdown":
        cb_full = st.number_input("Cashback – Full", 0, 50000, 0)
        cb_emi = st.number_input("Cashback – EMI", 0, 50000, 0)
        cb_nc = st.number_input("Cashback – No-Cost", 0, 50000, 0)
    else:
        cb_full = cb_emi = cb_nc = 0

    schedule_view = st.radio("Schedule View", ["Monthly", "Yearly"])


# =====================================================
# CALCULATIONS
# =====================================================
emi_df, emi = generate_schedule(
    purchase, rate, tenure, fee_base, fee_tax
)

interest_total = emi_df["Interest"].sum()
tax_total = emi_df["GST on Interest"].sum() + fee_tax

full_total = purchase - cb_full
emi_total = emi_df["Total Payment"].sum() - cb_emi
nocost_total = purchase + tax_total + fee_base - cb_nc

avg_emi = emi_df["Total Payment"].mean()


# =====================================================
# COST SUMMARY (EMBEDDED)
# =====================================================
st.markdown("### 📌 Cost Summary")

selected = st.radio(
    "Compare",
    ["Full Payment", "Normal EMI", "No-Cost EMI"],
    horizontal=True
)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("**Full Payment**" if selected == "Full Payment" else "Full Payment")
    st.markdown(f"### ₹{full_total:,.0f}")
    mini_donut([purchase, 0, 0, 0], selected == "Full Payment")
    st.caption("One-time payment")

with c2:
    st.markdown("**Normal EMI**" if selected == "Normal EMI" else "Normal EMI")
    st.markdown(f"### ₹{emi_total:,.0f}")
    mini_donut(
        [purchase, interest_total, tax_total, fee_base],
        selected == "Normal EMI"
    )
    st.caption(
        f"~₹{avg_emi:,.0f}/month  \n"
        f"Principal ₹{purchase/tenure:,.0f} · "
        f"Interest ₹{interest_total/tenure:,.0f} · "
        f"Tax ₹{tax_total/tenure:,.0f}"
    )

with c3:
    st.markdown("**No-Cost EMI**" if selected == "No-Cost EMI" else "No-Cost EMI")
    st.markdown(f"### ₹{nocost_total:,.0f}")
    mini_donut(
        [purchase, 0, tax_total, fee_base],
        selected == "No-Cost EMI"
    )
    st.caption("Interest waived · Tax & fees apply")


# =====================================================
# PAYMENT SCHEDULE
# =====================================================
st.markdown("### 📅 Payment Schedule")

display_df = emi_df.copy()

if schedule_view == "Yearly":
    display_df = display_df.groupby((display_df.index // 12) + 1).sum()

if view_mode == "Simple (Recommended)":
    display_df = display_df[
        ["Month", "Total Payment", "Principal Remaining"]
    ]

st.dataframe(display_df.style.format("{:,.0f}"))


# =====================================================
# DISCLAIMER
# =====================================================
st.markdown("""
### ⚠️ Disclaimer
PayWise is for **educational purposes only**.  
Actual EMI terms depend on banks, card issuers, and merchant offers.
""")
