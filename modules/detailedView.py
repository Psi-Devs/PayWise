import streamlit as st
from utils.charts import render_donut
from utils.calculations import yearly_view


def render_detailed_view(
    purchase_amount,
    full_total,
    normal_total,
    no_cost_total,
    avg_monthly,
    avg_principal,
    avg_interest,
    avg_tax,
    avg_fee,
    emi_df,
    schedule_view,
    fee_mode,
    breakdowns,
):
    st.markdown("### 📊 Detailed Dashboard")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Full Payment", f"{full_total:,.0f}")
        st.caption("One-time payment")

    with c2:
        st.metric("Normal EMI", f"{normal_total:,.0f}")
        st.caption(
            f"~₹{avg_monthly:,.0f}/month "
            f"(₹{avg_principal:,.0f} + ₹{avg_interest:,.0f} + "
            f"₹{avg_tax:,.0f} tax + ₹{avg_fee:,.0f} fees)"
        )

    with c3:
        st.metric("No-Cost EMI", f"{no_cost_total:,.0f}")
        st.caption("Interest waived, taxes & fees apply")

    st.divider()

    st.markdown("### 📊 Cost Breakdown")

    d1, _, d2, _, d3 = st.columns([1, 0.4, 1, 0.4, 1])

    with d1:
        full_net = breakdowns["full"]["net"]
        render_donut(
            full_net["principal"],
            full_net["interest"],
            full_net["tax"],
            full_net["fee"],
            "Full Payment",
        )

    with d2:
        emi_net = breakdowns["emi"]["net"]
        render_donut(
            emi_net["principal"],
            emi_net["interest"],
            emi_net["tax"],
            emi_net["fee"],
            "Normal EMI",
        )

    with d3:
        nocost_net = breakdowns["nocost"]["net"]
        render_donut(
            nocost_net["principal"],
            nocost_net["interest"],
            nocost_net["tax"],
            nocost_net["fee"],
            "No-Cost EMI",
        )

    st.divider()

    st.markdown("### 📅 Detailed Payment Schedule")

    display_df = emi_df if schedule_view == "Monthly" else yearly_view(emi_df)

    fee_mode_normalized = (
        "Percentage"
        if str(fee_mode).lower().startswith("p")
        else "Fixed"
    )

    detailed_columns = [
        "Month" if "Month" in display_df.columns else display_df.columns[0],
        "Principal Paid",
        "Interest",
        "GST on Interest (@18%)",
        "Processing Fee",
        "GST on Processing Fee (@18%)",
        "Total Payment",
        "Principal Remaining",
    ]

    if fee_mode_normalized == "Percentage":
        detailed_columns = [
            "Month" if "Month" in display_df.columns else display_df.columns[0],
            "Principal Paid",
            "Interest",
            "GST on Interest (@18%)",
            "Total Payment",
            "Principal Remaining",
        ]
        st.caption(
            "Processing fee is financed into principal for percentage fees, "
            "so it does not appear as an upfront line item."
        )

    st.dataframe(
        display_df[detailed_columns].style.format("{:,.2f}"),
        width="stretch",
    )
