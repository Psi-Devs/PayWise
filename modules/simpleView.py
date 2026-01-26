import streamlit as st
from utils.charts import render_donut


def render_simple_view(
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
):

    st.markdown("### 📌 Cost Summary")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Full Payment", f"{full_total:,.0f}")
        st.caption("One-time payment")

    with c2:
        st.metric("Normal EMI", f"{normal_total:,.0f}")
        st.caption(
            f"~₹{avg_monthly:,.0f}/month "
            f"(₹{avg_principal:,.0f} + ₹{avg_interest:,.0f} + ₹{avg_tax:,.0f} tax)"
        )

    with c3:
        st.metric("No-Cost EMI", f"{no_cost_total:,.0f}")
        st.caption("Interest discounted, taxes & fees apply")

    st.divider()

    st.markdown("### 📊 Cost Breakdown")

    # donut | gap | donut | gap | donut
    c1, _, c2, _, c3 = st.columns([1, 0.4, 1, 0.4, 1])

    with c1:
        render_donut(purchase_amount, 0, 0, 0)

    with c2:
        render_donut(
            purchase_amount,
            total_interest,
            total_gst_interest,
            total_fee_with_gst,
        )

    with c3:
        render_donut(
            purchase_amount,
            0,
            total_gst_interest,
            total_fee_with_gst,
        )

    st.markdown("### 📅 Payment Schedule")

    display_df = emi_df if schedule_view == "Monthly" else yearly_view(emi_df)

    display_df = display_df[
        ["Month", "Total Payment", "Principal Remaining"]
    ]

    st.dataframe(display_df.style.format("{:,.0f}"), use_container_width=True)
