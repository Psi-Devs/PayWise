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
# EMI LOGIC
# =====================================================
def calculate_emi(p, r, n):
    r = r / 12 / 100
    if r == 0:
        return p / n
    return p * r * (1 + r)**n / ((1 + r)**n - 1)


def emi_schedule(p, r, n, fee):
    emi = calculate_emi(p, r, n)
    bal = p
    rows = []

    for i in range(1, n + 1):
        interest = bal * (r / 12 / 100)
        gst = interest * GST
        principal = emi - interest
        bal -= principal

        rows.append({
            "Month": i,
            "Principal Paid": principal,
            "Interest": interest,
            "GST on Interest": gst,
            "Total Payment": emi + gst,
            "Principal Remaining": max(bal, 0),
            "Remarks": "Processing Fee" if i == 1 and fee > 0 else ""
        })

    df = pd.DataFrame(rows)
    df.loc[0, "Total Payment"] += fee
    return df, emi


def yearly_view(df):
    return (
        df.groupby((df.index // 12) + 1)
        .sum()
        .reset_index(drop=True)
    )


# =====================================================
# PDF EXPORT
# =====================================================
def export_pdf(name, summary, schedule):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, margin=36)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph(f"<b>PayWise – EMI Scenario: {name}</b>", styles["Title"])
    )
    elements.append(
        Paragraph("Make smarter payment decisions", styles["Italic"])
    )
    elements.append(Spacer(1, 12))

    table = Table([["Metric", "Value"]] + summary)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("<b>Payment Schedule</b>", styles["Heading2"]))
    table = Table(
        [schedule.columns.tolist()] + schedule.round(2).values.tolist(),
        repeatRows=1
    )
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
    ]))
    elements.append(table)

    elements.append(Spacer(1, 20))
    elements.append(
        Paragraph(
            "<i>This report is for educational purposes only.</i>",
            styles["Italic"]
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer


# =====================================================
# SESSION STATE
# =====================================================
if "scenarios" not in st.session_state:
    st.session_state.scenarios = {}


# =====================================================
# TOP INTRO (PAYWISE)
# =====================================================
st.markdown("""
## 💳 PayWise  
### *Make smarter payment decisions.*

Compare **Full Payment**, **Normal EMI**, and **No-Cost EMI**  
with **GST, processing fees, cashback, and full transparency**.
""")


# =====================================================
# INPUTS
# =====================================================
with st.sidebar:
    st.header("Purchase Details")

    amount = st.number_input(
        "Purchase Amount (₹)",
        1_000, 50_00_000, 50_000, step=1_000
    )
    rate = st.number_input(
        "Interest Rate (% p.a.)",
        0.0, 40.0, 15.0, step=0.25
    )
    tenure = st.selectbox(
        "Tenure (months)",
        [3, 6, 9, 12, 18, 24, 36]
    )

    fee = st.number_input(
        "Processing Fee (₹)",
        0, 5000, 199
    ) * (1 + GST)

    cashback = st.number_input(
        "Cashback (Full Payment)",
        0, 50000, 0
    )

    view = st.radio(
        "Schedule View",
        ["Monthly", "Yearly"]
    )


# =====================================================
# CALCULATIONS
# =====================================================
emi_df, emi = emi_schedule(amount, rate, tenure, fee)

interest = emi_df["Interest"].sum()
gst = emi_df["GST on Interest"].sum()

normal_total = emi_df["Total Payment"].sum()
no_cost_total = amount + gst + fee
full_total = amount + fee - cashback


# =====================================================
# SUMMARY
# =====================================================
st.markdown("### 📌 Cost Summary")

c1, c2, c3 = st.columns(3)

c1.metric("Full Payment", f"{full_total:,.0f}")
c2.metric("Normal EMI", f"{normal_total:,.0f}")
c3.metric("No-Cost EMI", f"{no_cost_total:,.0f}")

st.caption(
    "ℹ️ No-Cost EMI assumes interest is discounted by the merchant. "
    "GST and processing fees still apply."
)


# =====================================================
# SCHEDULE
# =====================================================
st.markdown("### 📅 Payment Schedule")

display_df = emi_df if view == "Monthly" else yearly_view(emi_df)

st.dataframe(
    display_df.style.format({
        "Principal Paid": "{:,.0f}",
        "Interest": "{:,.0f}",
        "GST on Interest": "{:,.0f}",
        "Total Payment": "{:,.0f}",
        "Principal Remaining": "{:,.0f}",
    })
)


# =====================================================
# SAVE SCENARIO
# =====================================================
st.markdown("### 💾 Save Scenario")

name = st.text_input("Scenario Name")

if st.button("Save Scenario") and name:
    st.session_state.scenarios[name] = {
        "amount": amount,
        "rate": rate,
        "tenure": tenure,
        "fee": fee,
        "cashback": cashback,
        "summary": [
            ["Full Payment", f"{full_total:,.0f}"],
            ["Normal EMI", f"{normal_total:,.0f}"],
            ["No-Cost EMI", f"{no_cost_total:,.0f}"],
        ],
        "schedule": display_df,
    }
    st.success("Scenario saved successfully")


# =====================================================
# EXPORT SAVED SCENARIO
# =====================================================
if st.session_state.scenarios:
    st.markdown("### 📄 Export Scenario to PDF")

    sel = st.selectbox(
        "Select Scenario",
        list(st.session_state.scenarios.keys())
    )

    scenario = st.session_state.scenarios[sel]

    pdf = export_pdf(
        sel,
        scenario["summary"],
        scenario["schedule"]
    )

    st.download_button(
        "Download PDF",
        pdf,
        f"{sel}.pdf",
        "application/pdf"
    )


# =====================================================
# COMPARE TWO SCENARIOS
# =====================================================
if len(st.session_state.scenarios) >= 2:
    st.markdown("### 🔍 Compare Two Scenarios")

    selected = st.multiselect(
        "Select two scenarios",
        list(st.session_state.scenarios.keys()),
        max_selections=2
    )

    if len(selected) == 2:
        a = st.session_state.scenarios[selected[0]]
        b = st.session_state.scenarios[selected[1]]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(selected[0])
            st.table(a["summary"])

        with col2:
            st.subheader(selected[1])
            st.table(b["summary"])


# =====================================================
# DISCLAIMER
# =====================================================
st.markdown("""
### ⚠️ Disclaimer

PayWise is for **educational purposes only**.  
Actual EMI terms depend on banks, card issuers, and merchant offers.
""")
