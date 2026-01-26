import pandas as pd

GST_RATE = 0.18


# -------------------------------------------------
# EMI formula (unchanged)
# -------------------------------------------------
def calculate_emi(principal, annual_rate, months):
    r = annual_rate / 12 / 100
    if r == 0:
        return principal / months
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)


# -------------------------------------------------
# Unified calculation engine
# -------------------------------------------------
def compute_paywise(
    purchase_amount: float,
    interest_rate: float,
    tenure: int,
    processing_fee_base: float,
    cashback_full: float,
    cashback_emi: float,
    cashback_nocost: float
) -> dict:

    emi = calculate_emi(purchase_amount, interest_rate, tenure)
    monthly_rate = interest_rate / 12 / 100

    balance = purchase_amount
    rows = []

    for month in range(1, tenure + 1):
        interest = balance * monthly_rate
        gst_interest = interest * GST_RATE

        principal_paid = emi - interest
        balance -= principal_paid

        processing_fee = processing_fee_base if month == 1 else 0
        gst_processing_fee = processing_fee * GST_RATE

        total_payment = (
            emi
            + gst_interest
            + processing_fee
            + gst_processing_fee
        )

        rows.append({
            "Month": month,
            "EMI": round(emi, 2),
            "Principal Paid": round(principal_paid, 2),
            "Interest": round(interest, 2),
            "GST on Interest (@18%)": round(gst_interest, 2),
            "Processing Fee": round(processing_fee, 2),
            "GST on Processing Fee (@18%)": round(gst_processing_fee, 2),
            "Total Payment": round(total_payment, 2),
            "Principal Remaining": round(max(balance, 0), 2),
        })

    emi_df = pd.DataFrame(rows)

    # -------------------------------------------------
    # Aggregates (NO CHANGE in meaning)
    # -------------------------------------------------
    total_interest = emi_df["Interest"].sum()
    total_gst_interest = emi_df["GST on Interest (@18%)"].sum()
    total_processing_fee = emi_df["Processing Fee"].sum()
    total_gst_fee = emi_df["GST on Processing Fee (@18%)"].sum()

    total_paid = emi_df["Total Payment"].sum()

    totals = {
        "purchase_amount": purchase_amount,
        "total_interest": round(total_interest, 2),
        "total_gst_interest": round(total_gst_interest, 2),
        "total_processing_fee": round(total_processing_fee, 2),
        "total_gst_processing_fee": round(total_gst_fee, 2),
        "total_paid": round(total_paid, 2),

        # Effective costs (UNCHANGED semantics)
        "effective_cost_full": round(
            purchase_amount
            + total_processing_fee
            + total_gst_fee
            - cashback_full, 2
        ),
        "effective_cost_emi": round(
            total_paid - cashback_emi, 2
        ),
        "effective_cost_nocost": round(
            purchase_amount
            + total_gst_interest
            + total_processing_fee
            + total_gst_fee
            - cashback_nocost, 2
        ),
    }

    averages = {
        "avg_monthly_outflow": round(total_paid / tenure, 2),
        "interest_percentage": round(
            (total_interest / purchase_amount) * 100, 2
        )
    }

    comparison = [
        {
            "Mode": "Full Payment",
            "Total Cost": totals["effective_cost_full"],
            "Interest Paid": 0,
            "Processing Fee": total_processing_fee + total_gst_fee
        },
        {
            "Mode": "Regular EMI",
            "Total Cost": totals["effective_cost_emi"],
            "Interest Paid": round(total_interest + total_gst_interest, 2),
            "Processing Fee": round(total_processing_fee + total_gst_fee, 2)
        },
        {
            "Mode": "No-Cost EMI",
            "Total Cost": totals["effective_cost_nocost"],
            "Interest Paid": 0,
            "Processing Fee": round(total_processing_fee + total_gst_fee, 2)
        }
    ]

    return {
        "emi_df": emi_df,
        "totals": totals,
        "averages": averages,
        "comparison": comparison
    }


# -------------------------------------------------
# Yearly view (UNCHANGED)
# -------------------------------------------------
def yearly_view(df):
    return (
        df.groupby((df.index // 12) + 1)
        .sum()
        .reset_index(drop=True)
    )



# -------------------------------------------------
# Backward compatibility wrapper
# (DO NOT REMOVE — used by existing views)
# -------------------------------------------------
def generate_emi_schedule(
    principal,
    annual_rate,
    months,
    processing_fee
):
    """
    Compatibility wrapper for older code paths.
    Internally uses compute_paywise.
    """

    data = compute_paywise(
        purchase_amount=principal,
        interest_rate=annual_rate,
        tenure=months,
        processing_fee_base=processing_fee,
        cashback_full=0,
        cashback_emi=0,
        cashback_nocost=0,
    )

    return data["emi_df"], data["emi_df"]["EMI"].iloc[0]
