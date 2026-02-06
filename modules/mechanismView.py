import pandas as pd
import streamlit as st

from utils.calculations import compute_paywise, GST_RATE


def render_mechanism_view(
    purchase_amount,
    interest_rate,
    tenure,
    processing_fee_base,
    fee_mode,
    cashback_full,
    cashback_emi,
    cashback_nocost,
    data,
):
    st.subheader("📘 How EMI Works")

    emi_df = data["emi_df"]
    totals = data["totals"]
    monthly_rate = interest_rate / 12 / 100
    emi_value = float(emi_df["EMI"].iloc[0]) if len(emi_df) else 0.0

    st.markdown("**Core EMI Formula**")
    st.latex(r"\text{EMI} = \frac{P \cdot r \cdot (1+r)^n}{(1+r)^n - 1}")
    st.caption(
        f"P = ₹{purchase_amount:,.0f} | "
        f"r = {monthly_rate:.6f} (monthly) | "
        f"n = {tenure} months | "
        f"EMI ≈ ₹{emi_value:,.0f}"
    )

    st.markdown("**Month 1 Breakdown (from the schedule)**")
    if len(emi_df):
        first = emi_df.iloc[0]
        month1_rows = [
            ["Opening Balance", purchase_amount],
            ["Interest", first["Interest"]],
            ["GST on Interest", first["GST on Interest (@18%)"]],
            ["Processing Fee", first["Processing Fee"]],
            ["GST on Processing Fee", first["GST on Processing Fee (@18%)"]],
            ["EMI", first["EMI"]],
            ["Total Payment (Month 1)", first["Total Payment"]],
        ]
        month1_df = pd.DataFrame(month1_rows, columns=["Item", "Amount (₹)"])
        st.dataframe(
            month1_df.style.format({"Amount (₹)": "{:,.2f}"}),
            width="stretch",
        )

    st.markdown("**Total Cost Formulas Used**")
    st.markdown(
        f"Full Payment = Purchase Amount - Cashback = "
        f"₹{purchase_amount:,.0f} - ₹{cashback_full:,.0f} = "
        f"₹{totals['effective_cost_full']:,.0f}"
    )
    st.markdown(
        f"Normal EMI = Sum(All Monthly Payments) - Cashback = "
        f"₹{totals['total_paid']:,.0f} - ₹{cashback_emi:,.0f} = "
        f"₹{totals['effective_cost_emi']:,.0f}"
    )
    st.markdown(
        "No-Cost EMI = Purchase Amount + GST on Interest + Fees (incl. GST) - Cashback"
    )
    st.markdown(
        f"= ₹{purchase_amount:,.0f} + "
        f"₹{totals['total_gst_interest']:,.0f} + "
        f"₹{totals['total_processing_fee'] + totals['total_gst_processing_fee']:,.0f} - "
        f"₹{cashback_nocost:,.0f} = "
        f"₹{totals['effective_cost_nocost']:,.0f}"
    )

    st.caption(
        f"GST rate used: {GST_RATE * 100:.0f}% | "
        "Processing fee handling depends on the fee type."
    )

    if fee_mode == "Percentage":
        st.info(
            "Percentage-based fee is financed: fee + GST are added to the principal "
            "and repaid within EMIs (no separate upfront fee line in the schedule)."
        )
    else:
        st.info(
            "Fixed fee is charged upfront in month 1, with GST added in that month."
        )

    st.markdown("**How Small Changes Affect Cost (What-Ifs)**")

    base = data
    scenarios = [
        ("Interest rate +0.5%", {"interest_rate": interest_rate + 0.5}),
        ("Tenure +1 month", {"tenure": tenure + 1}),
        ("Processing fee +₹100", {"processing_fee_base": processing_fee_base + 100}),
        ("EMI cashback +₹500", {"cashback_emi": cashback_emi + 500}),
    ]

    rows = []
    for label, overrides in scenarios:
        variant = compute_paywise(
            purchase_amount=purchase_amount,
            interest_rate=overrides.get("interest_rate", interest_rate),
            tenure=overrides.get("tenure", tenure),
            processing_fee_base=overrides.get("processing_fee_base", processing_fee_base),
            fee_mode=overrides.get("fee_mode", fee_mode),
            cashback_full=overrides.get("cashback_full", cashback_full),
            cashback_emi=overrides.get("cashback_emi", cashback_emi),
            cashback_nocost=overrides.get("cashback_nocost", cashback_nocost),
        )

        rows.append({
            "Change": label,
            "Normal EMI Total Δ": (
                variant["totals"]["effective_cost_emi"]
                - base["totals"]["effective_cost_emi"]
            ),
            "Normal EMI / month Δ": (
                variant["averages"]["avg_monthly_outflow"]
                - base["averages"]["avg_monthly_outflow"]
            ),
            "No-Cost Total Δ": (
                variant["totals"]["effective_cost_nocost"]
                - base["totals"]["effective_cost_nocost"]
            ),
            "Full Payment Total Δ": (
                variant["totals"]["effective_cost_full"]
                - base["totals"]["effective_cost_full"]
            ),
        })

    delta_df = pd.DataFrame(rows)
    st.dataframe(
        delta_df.style.format({
            "Normal EMI Total Δ": "{:+,.0f}",
            "Normal EMI / month Δ": "{:+,.0f}",
            "No-Cost Total Δ": "{:+,.0f}",
            "Full Payment Total Δ": "{:+,.0f}",
        }),
        width="stretch",
    )

    st.info(
        "Tip: Use this view to understand which lever changes total cost the most. "
        "Rate and tenure shifts usually dominate."
    )
