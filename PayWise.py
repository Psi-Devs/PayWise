# =====================================================
# IMPORTS
# =====================================================
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

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
# SESSION STATE
# =====================================================
if "scenarios" not in st.session_state:
    st.session_state.scenarios = {}


# =====================================================
# EMI CORE LOGIC
# =====================================================
def calculate_emi(principal, annual_rate, months):
    r = annual_rate / 12 / 100
    if r == 0:
        return principal / months
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)


def generate_emi_schedule(principal, annual_rate, months,
                          fee_base, fee_tax):
    emi = calculate_emi(principal, annual_rate, months)
    balance = principal
    rows = []

    for m in range(1, months + 1):
        interest = balance * (annual_rate / 12 / 100)
        gst_interest = interest * GST
        principal_paid = emi - interest
        balance -= principal_paid

        rows.append({
            "Month": m,
            "Principal Paid": principal_paid,
            "Interest": interest,
            "GST on Interest (@18%)": gst_interest,
            "Processing Fee": fee_base if m == 1 else 0,
            "GST on Fee": fee_tax if m == 1 else 0,
            "Total Payment": emi + gst_interest +
                             (fee_base + fee_tax if m == 1 else 0),
            "Principal Remaining": max(balance, 0)
        })

    return pd.DataFrame(rows), emi


def yearly_view(df):
    return (
        df.groupby((df.index // 12) + 1)
        .sum()
        .reset_index(drop=True)
    )


# =====================================================
# DONUT
# =====================================================
def render_donut(principal, interest, tax, fee, selected):
    fig, ax = plt.subplots(figsize=(2.8, 2.8))

    ax.pie(
        [principal, interest, tax, fee],
        labels=["Principal", "Interest", "Tax", "Fees"],
        startangle=90,
        colors=["#4c72b0", "#dd8452", "#c44e52", "#8172b2"]
    )

    ax.add_artist(plt.Circle((0, 0), 0.65, color="white"))
    ax.text(0, 0, f"{principal+interest+tax+fee:,.0f}",
            ha="center", va="center", fontsize=10, weight="bold")

    if selected:
        ax.patch.set_edgecolor("#4c72b0")
        ax.patch.set_linewidth(2)
    else:
        ax.patch.set_alpha(0.4)

    ax.set_title("")
    st.pyplot(fig)


# =====================================================
# PDF EXPORT
# =====================================================
def export_pdf(name, summary, df):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"<b>PayWise Report – {name}</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    table = Table([["Metric", "Value"]] + summary)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONT", (0,0), (-1,0), "Helvetica-Bold")
    ]))

    elements.append(table)
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("<b>Payment Schedule</b>", styles["Heading2"]))
    elements.append(
        Table([df.columns.tolist()] + df.round(2).values.tolist(),
              repeatRows=1)
    )

    doc.build(elements)
    buf.seek(0)
    return buf


# =====================================================
# UI – HEADER
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
    view_mode = st.radio("View Mode",
        ["Simple (Recommended)", "Detailed Breakdown"])

    purchase = st.number_input("Purchase Amount (₹)",
        1_000, 50_00_000, 50_000, step=1_000)

    rate = st.number_input("Interest Rate (% p.a.)",
        0.0, 40.0, 15.0, step=0.25)

    tenure = st.selectbox("Tenure (months)",
        [3,6,9,12,18,24,36])

    fee_base = st.number_input("Processing Fee (₹)",
        0, 5000, 199)

    fee_tax = fee_base * GST

    if view_mode == "Detailed Breakdown":
        cb_full = st.number_input("Cashback – Full Pay", 0, 50000, 0)
        cb_emi = st.number_input("Cashback – EMI", 0, 50000, 0)
        cb_nc = st.number_input("Cashback – No-Cost", 0, 50000, 0)
    else:
        cb_full = cb_emi = cb_nc = 0

    schedule_view = st.radio("Schedule View",
        ["Monthly", "Yearly"])


# =====================================================
# CALCULATIONS
# =====================================================
emi_df, emi = generate_emi_schedule(
    purchase, rate, tenure, fee_base, fee_tax)

interest = emi_df["Interest"].sum()
tax = emi_df["GST on Interest (@18%)"].sum() + fee_tax

full_total = purchase - cb_full
emi_total = emi_df["Total Payment"].sum() - cb_emi
nc_total = purchase + tax + fee_base - cb_nc


# =====================================================
# COST SUMMARY
# =====================================================
st.markdown("### 📌 Cost Summary")

c1, c2, c3 = st.columns(3)
c1.metric("Full Payment", f"{full_total:,.0f}")
c2.metric("Normal EMI", f"{emi_total:,.0f}")
c3.metric("No-Cost EMI", f"{nc_total:,.0f}")


# =====================================================
# DONUTS
# =====================================================
st.markdown("### 📊 Cost Breakdown")

choice = st.radio("Select option",
    ["Full Payment", "Normal EMI", "No-Cost EMI"], horizontal=True)

d1, d2, d3 = st.columns(3)
with d1:
    render_donut(purchase, 0, 0, 0, choice=="Full Payment")
with d2:
    render_donut(purchase, interest, tax, fee_base, choice=="Normal EMI")
with d3:
    render_donut(purchase, 0, tax, fee_base, choice=="No-Cost EMI")


# =====================================================
# SCHEDULE
# =====================================================
st.markdown("### 📅 Payment Schedule")

df = emi_df if schedule_view=="Monthly" else yearly_view(emi_df)
if view_mode=="Simple (Recommended)":
    df = df[["Month","Total Payment","Principal Remaining"]]

st.dataframe(df.style.format("{:,.0f}"))


# =====================================================
# SAVE + EXPORT
# =====================================================
st.markdown("### 💾 Save Scenario")

name = st.text_input("Scenario name")
if st.button("Save") and name:
    st.session_state.scenarios[name] = {
        "summary": [
            ["Full Payment", full_total],
            ["Normal EMI", emi_total],
            ["No-Cost EMI", nc_total]
        ],
        "schedule": df
    }
    st.success("Saved")

if st.session_state.scenarios:
    sel = st.selectbox("Export scenario",
        list(st.session_state.scenarios.keys()))
    sc = st.session_state.scenarios[sel]
    pdf = export_pdf(sel, sc["summary"], sc["schedule"])
    st.download_button("Download PDF", pdf, f"{sel}.pdf")


# =====================================================
# DISCLAIMER
# =====================================================
st.markdown("""
### ⚠️ Disclaimer  
PayWise is for educational purposes only.  
Actual EMI terms depend on banks, card issuers, and merchant offers.
""")
