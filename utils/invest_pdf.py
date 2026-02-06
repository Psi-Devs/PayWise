import io
from datetime import date

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


def generate_invest_pdf_bytes(
    monthly_df,
    yearly_df,
    monthly_sip,
    stepup_percent,
    annual_return_percent,
    annual_inflation_percent,
    years,
    start_year,
):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, margin=36)
    styles = getSampleStyleSheet()
    elements = []

    last = monthly_df.iloc[-1]

    elements.append(Paragraph("<b>Step-Up SIP Investment Report</b>", styles["Title"]))
    elements.append(Spacer(1, 10))
    elements.append(
        Paragraph(f"Generated on {date.today().strftime('%d %b %Y')}", styles["Normal"])
    )
    elements.append(Spacer(1, 16))

    # ---- Executive Summary ----
    elements.append(Paragraph("<b>Executive Summary</b>", styles["Heading2"]))
    elements.append(Spacer(1, 6))

    summary_table = Table(
        [
            ["Metric", "Value"],
            ["Monthly SIP", f"{monthly_sip:,.0f}"],
            ["Annual Step-Up", f"{stepup_percent}%"],
            ["Expected Return", f"{annual_return_percent}%"],
            ["Inflation", f"{annual_inflation_percent}%"],
            ["Duration", f"{years} years"],
            ["Total Invested", f"{last['Total Invested']:,.0f}"],
            ["Final Nominal Value", f"{last['Nominal Amount']:,.0f}"],
            ["Final Inflation Adjusted Value", f"{last['Inflation Adjusted Amount']:,.0f}"],
            ["Real Gain / Loss", f"{last['Inflation Adjusted Amount'] - last['Total Invested']:,.0f}"],
        ],
        colWidths=[190, 190],
    )

    summary_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )

    elements.append(summary_table)
    elements.append(Spacer(1, 16))

    # ---- 5-Year Milestones ----
    elements.append(Paragraph("<b>5-Year Growth Milestones</b>", styles["Heading2"]))
    elements.append(Spacer(1, 6))

    milestones = yearly_df[yearly_df["Year"].sub(start_year).mod(5) == 4]
    milestone_data = [["Years Completed", "Total Invested", "Nominal", "Real"]]

    for _, r in milestones.iterrows():
        milestone_data.append([
            r["Year"] - start_year + 1,
            f"{r['Total Invested']:,.0f}",
            f"{r['Nominal Amount']:,.0f}",
            f"{r['Inflation Adjusted Amount']:,.0f}",
        ])

    milestone_table = Table(milestone_data, repeatRows=1)
    milestone_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )

    elements.append(milestone_table)
    elements.append(Spacer(1, 20))

    # ---- Detailed Monthly Schedule ----
    elements.append(PageBreak())
    elements.append(Paragraph("<b>Detailed Monthly Schedule</b>", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    schedule_df = monthly_df.copy().round(2)
    table_data = [schedule_df.columns.tolist()] + schedule_df.values.tolist()

    schedule_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[50, 65, 120, 120, 140],
    )

    schedule_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                ("ALIGN", (0, 1), (1, -1), "CENTER"),
            ]
        )
    )

    elements.append(schedule_table)

    # ---- Definitions & Acronyms ----
    elements.append(PageBreak())
    elements.append(Paragraph("<b>Definitions and Acronyms</b>", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    glossary_lines = [
        "<b>SIP:</b> Systematic Investment Plan. A fixed periodic investment.",
        "<b>Step-Up:</b> A yearly increase in SIP amount by a fixed percentage.",
        "<b>Nominal Value:</b> Portfolio value without inflation adjustment.",
        "<b>Real Value:</b> Inflation-adjusted portfolio value.",
        "<b>Inflation Rate:</b> Estimated annual loss of purchasing power.",
        "<b>Expected Return:</b> Estimated annual growth rate of investments.",
        "<b>Total Invested:</b> Sum of all SIP contributions.",
        "<b>Monthly Return:</b> Annual return divided by 12 and 100.",
        "<b>Monthly Inflation:</b> Annual inflation divided by 12 and 100.",
    ]

    for line in glossary_lines:
        elements.append(Paragraph(line, styles["BodyText"]))
        elements.append(Spacer(1, 4))

    elements.append(Spacer(1, 8))
    elements.append(Paragraph("<b>Model Notes</b>", styles["Heading3"]))
    elements.append(Spacer(1, 4))
    elements.append(
        Paragraph(
            "Each month, the SIP contribution is added, then the portfolio grows "
            "by the monthly return. The real value is reduced by monthly inflation "
            "to estimate purchasing power.",
            styles["BodyText"],
        )
    )
    elements.append(Spacer(1, 6))
    elements.append(
        Paragraph(
            "This report is for educational purposes only and does not guarantee "
            "future returns.",
            styles["BodyText"],
        )
    )

    elements.append(
        Paragraph(
            "<i>This report is for educational purposes only. Not financial advice.</i>",
            styles["Italic"],
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer
