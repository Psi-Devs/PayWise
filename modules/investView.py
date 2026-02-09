import streamlit as st

from utils.investment import (
    calculate_stepup_sip_inflation_adjusted,
    convert_monthly_to_yearly,
)
from utils.invest_pdf import generate_invest_pdf_bytes
from modules.invest_sections import (
    render_invest_header,
    render_invest_summary,
    render_invest_overview,
    render_invest_milestones,
    render_invest_report,
    render_invest_disclaimer,
)


def render_invest_view(animate=True):
    render_invest_header()

    with st.sidebar:
        st.header("Investment Inputs")

        st.markdown("### Contribution")
        monthly_sip = st.number_input(
            "Monthly SIP (₹)",
            min_value=500,
            max_value=200_000,
            value=8_000,
            step=500,
        )
        stepup = st.number_input(
            "Annual Step-Up (%)",
            min_value=0.0,
            max_value=25.0,
            value=0.0,
            step=0.5,
        )

        st.markdown("### Market Assumptions")
        returns = st.number_input(
            "Expected Return (%)",
            min_value= -5.0,
            max_value=155.0,
            value=12.0,
            step=0.25,
        )
        inflation = st.number_input(
            "Inflation (%)",
            min_value=-2.0,
            max_value=15.0,
            value=6.0,
            step=0.25,
        )

        st.markdown("### Timeline")
        years = st.number_input(
            "Investment Duration (Years)",
            min_value=1,
            max_value=100,
            value=15,
            step=1,
        )
        start_year = st.number_input(
            "Start Year",
            min_value=1960,
            max_value=2060,
            value=2026,
            step=1,
        )
        view = st.radio("View Type", ["Yearly", "Monthly"], horizontal=True)

    monthly_df = calculate_stepup_sip_inflation_adjusted(
        monthly_sip, stepup, returns, inflation, years, start_year
    )
    yearly_df = convert_monthly_to_yearly(monthly_df)
    final = monthly_df.iloc[-1]

    render_invest_summary(final)
    st.divider()

    render_invest_overview(final, monthly_df, animate=animate)
    st.divider()

    render_invest_milestones(yearly_df, start_year)
    st.divider()

    display_df = yearly_df if view == "Yearly" else monthly_df
    render_invest_report(display_df)
    st.divider()

    st.markdown("### 📄 Download Report")

    pdf_bytes = generate_invest_pdf_bytes(
        monthly_df,
        yearly_df,
        monthly_sip,
        stepup,
        returns,
        inflation,
        years,
        start_year,
    )

    st.download_button(
        "Download Investment PDF",
        data=pdf_bytes,
        file_name="stepup_sip_investment_report.pdf",
        mime="application/pdf",
    )

    render_invest_disclaimer()
