import io
import matplotlib.pyplot as plt

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


# -------------------------------------------------
# Donut chart → image buffer
# -------------------------------------------------
def generate_donut_image(principal, interest, gst, fee):
    fig, ax = plt.subplots(figsize=(3, 3))

    values = []
    labels = []
    colors_map = []

    if principal > 0:
        values.append(principal)
        labels.append("Principal")
        colors_map.append("#1f77b4")
    if interest > 0:
        values.append(interest)
        labels.append("Interest")
        colors_map.append("#ff7f0e")
    if gst > 0:
        values.append(gst)
        labels.append("GST")
        colors_map.append("#2ca02c")
    if fee > 0:
        values.append(fee)
        labels.append("Fees")
        colors_map.append("#d62728")

    ax.pie(
        values,
        startangle=90,
        colors=colors_map,
        wedgeprops=dict(width=0.35),
    )
    ax.axis("equal")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


# -------------------------------------------------
# Main PDF generator
# -------------------------------------------------
def generate_pdf_report(
    purchase_amount,
    full_total,
    normal_total,
    no_cost_total,
    total_interest,
    total_gst_interest,
    total_fee_with_gst,
    emi_df,
    breakdowns,
    fee_mode,
):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # ---------------- Title ----------------
    elements.append(Paragraph("<b>PayWise — EMI Summary Report</b>", styles["Title"]))
    elements.append(Spacer(1, 14))

    # ---------------- Summary Table ----------------
    summary_table = Table(
        [
            ["Mode", "Total Cost (₹)"],
            ["Full Payment", f"{full_total:,.0f}"],
            ["Normal EMI", f"{normal_total:,.0f}"],
            ["No-Cost EMI", f"{no_cost_total:,.0f}"],
        ],
        colWidths=[200, 120],
    )

    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )

    elements.append(summary_table)
    elements.append(Spacer(1, 18))

    # ---------------- Total Payout Breakdown ----------------
    cashback_emi = breakdowns["emi"]["cashback"]
    fee_mode_normalized = (
        "Percentage" if str(fee_mode).lower().startswith("p") else "Fixed"
    )

    totals_rows = [
        ["Component", "Amount (₹)"],
        ["Principal", f"{purchase_amount:,.0f}"],
        ["Interest", f"{total_interest:,.0f}"],
        ["GST", f"{total_gst_interest:,.0f}"],
        ["Processing Fee (incl. GST)", f"{total_fee_with_gst:,.0f}"],
    ]

    if cashback_emi > 0:
        totals_rows.append(["Cashback (discount)", f"-{cashback_emi:,.0f}"])

    totals_rows.append(["Net Total (EMI)", f"{normal_total:,.0f}"])

    totals_table = Table(
        totals_rows,
        colWidths=[220, 140],
    )

    totals_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )

    elements.append(Paragraph("<b>Total Payout Breakdown</b>", styles["Heading2"]))
    elements.append(Spacer(1, 8))
    elements.append(totals_table)
    elements.append(
        Paragraph(
            f"<i>Processing fee mode:</i> {fee_mode_normalized}. "
            "Fixed fees are charged in month 1. "
            "Percentage fees are financed into the EMI principal.",
            styles["BodyText"],
        )
    )
    elements.append(Spacer(1, 18))

    # ---------------- Charts (ONE ROW) ----------------
    elements.append(Paragraph("<b>Cost Breakdown</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    full_net = breakdowns["full"]["net"]
    emi_net = breakdowns["emi"]["net"]
    nocost_net = breakdowns["nocost"]["net"]

    img_full = Image(
        generate_donut_image(
            full_net["principal"],
            full_net["interest"],
            full_net["tax"],
            full_net["fee"],
        ),
        width=140,
        height=140,
    )
    img_emi = Image(
        generate_donut_image(
            emi_net["principal"],
            emi_net["interest"],
            emi_net["tax"],
            emi_net["fee"],
        ),
        width=140,
        height=140,
    )
    img_nocost = Image(
        generate_donut_image(
            nocost_net["principal"],
            nocost_net["interest"],
            nocost_net["tax"],
            nocost_net["fee"],
        ),
        width=140,
        height=140,
    )

    charts_table = Table(
        [[img_full, img_emi, img_nocost]],
        colWidths=[180, 180, 180],
    )

    charts_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    elements.append(charts_table)

    # ---------------- New Page ----------------
    elements.append(PageBreak())

    # ---------------- Detailed Schedule ----------------
    elements.append(Paragraph("<b>Detailed Payment Schedule</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    schedule_df = emi_df.copy()
    schedule_columns = schedule_df.columns.tolist()

    if fee_mode_normalized == "Percentage":
        drop_cols = [
            "Processing Fee",
            "GST on Processing Fee (@18%)",
        ]
        schedule_df = schedule_df.drop(columns=drop_cols, errors="ignore")
        schedule_columns = schedule_df.columns.tolist()

    table_data = [schedule_columns] + schedule_df.round(2).values.tolist()

    schedule_table = Table(table_data, repeatRows=1)

    schedule_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )

    elements.append(schedule_table)

    # ---------------- Glossary ----------------
    elements.append(PageBreak())
    elements.append(Paragraph("<b>Definitions and Acronyms</b>", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    glossary_lines = [
        "<b>EMI:</b> Equated Monthly Installment. The fixed monthly payment.",
        "<b>Principal (P):</b> The amount financed.",
        "<b>Interest:</b> Cost charged by the lender on the outstanding balance.",
        "<b>GST:</b> Goods and Services Tax (applied to interest and fees).",
        "<b>Processing Fee:</b> One-time fee charged by the lender or bank.",
        "<b>No-Cost EMI:</b> Interest is discounted by the merchant; taxes and fees may still apply.",
        "<b>Cashback:</b> Discount applied to the total cost.",
        "<b>Tenure (n):</b> Total number of months.",
        "<b>Monthly Rate (r):</b> Annual rate divided by 12 and 100.",
    ]

    for line in glossary_lines:
        elements.append(Paragraph(line, styles["BodyText"]))
        elements.append(Spacer(1, 4))

    elements.append(Spacer(1, 8))
    elements.append(Paragraph("<b>EMI Formula</b>", styles["Heading3"]))
    elements.append(Spacer(1, 4))
    elements.append(
        Paragraph(
            "EMI = (P * r * (1 + r)^n) / ((1 + r)^n - 1)",
            styles["BodyText"],
        )
    )
    elements.append(Spacer(1, 6))
    elements.append(
        Paragraph(
            "Note: For percentage-based processing fees, the fee and GST are added "
            "to the principal and repaid within the EMI.",
            styles["BodyText"],
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer
