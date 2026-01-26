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
    total_interest,
    total_tax,
    processing_fee,
    emi_df,
    schedule_view
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
            f"(₹{avg_principal:,.0f} + ₹{avg_interest:,.0f} + ₹{avg_tax:,.0f} tax (Includes interest, GST & processing fee))"
        )

    with c3:
        st.metric("No-Cost EMI", f"{no_cost_total:,.0f}")
        st.caption("Interest waived, taxes & fees apply")

    st.divider()

    st.markdown("### 📊 Cost Breakdown")

    d1, _, d2, _, d3 = st.columns([1, 0.4, 1, 0.4, 1])

    with d1:
        render_donut(purchase_amount, 0, 0, 0, "Full Payment")

    with d2:
        render_donut(purchase_amount, total_interest, total_tax, processing_fee, "Normal EMI")

    with d3:
        render_donut(purchase_amount, 0, total_tax, processing_fee, "No-Cost EMI")

    st.divider()

    st.markdown("### 📅 Detailed Payment Schedule")

    display_df = emi_df if schedule_view == "Monthly" else yearly_view(emi_df)

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

    st.dataframe(
        display_df[detailed_columns].style.format("{:,.2f}"),
        use_container_width=True,
    )
