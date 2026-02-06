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
    avg_fee,
    emi_df,
    schedule_view,
    yearly_view,
    breakdowns,
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
            f"(₹{avg_principal:,.0f} + ₹{avg_interest:,.0f} + "
            f"₹{avg_tax:,.0f} tax + ₹{avg_fee:,.0f} fees)"
        )

    with c3:
        st.metric("No-Cost EMI", f"{no_cost_total:,.0f}")
        st.caption("Interest discounted, taxes & fees apply")

    st.divider()

    st.markdown("### 📊 Cost Breakdown")

    # donut | gap | donut | gap | donut
    c1, _, c2, _, c3 = st.columns([1, 0.4, 1, 0.4, 1])

    with c1:
        full_net = breakdowns["full"]["net"]
        render_donut(
            full_net["principal"],
            full_net["interest"],
            full_net["tax"],
            full_net["fee"],
        )

    with c2:
        emi_net = breakdowns["emi"]["net"]
        render_donut(
            emi_net["principal"],
            emi_net["interest"],
            emi_net["tax"],
            emi_net["fee"],
        )

    with c3:
        nocost_net = breakdowns["nocost"]["net"]
        render_donut(
            nocost_net["principal"],
            nocost_net["interest"],
            nocost_net["tax"],
            nocost_net["fee"],
        )

    st.markdown("### 📅 Payment Schedule")

    display_df = emi_df if schedule_view == "Monthly" else yearly_view(emi_df)

    display_df = display_df[
        ["Month", "Total Payment", "Principal Remaining"]
    ]

    st.dataframe(display_df.style.format("{:,.0f}"), width="stretch")
