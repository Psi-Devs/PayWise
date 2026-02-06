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
# Cashback distribution for charts/tables
# -------------------------------------------------
def apply_cashback_to_components(components: dict, cashback: float) -> dict:
    """
    Reduce components by cashback to produce a net breakdown.
    Order: principal -> interest -> tax -> fee.
    """
    remaining = max(float(cashback), 0.0)
    adjusted = {
        "principal": float(components.get("principal", 0)),
        "interest": float(components.get("interest", 0)),
        "tax": float(components.get("tax", 0)),
        "fee": float(components.get("fee", 0)),
    }

    for key in ["principal", "interest", "tax", "fee"]:
        if remaining <= 0:
            break
        available = adjusted[key]
        if available <= 0:
            continue
        reduction = min(available, remaining)
        adjusted[key] = available - reduction
        remaining -= reduction

    for key in adjusted:
        if adjusted[key] < 1e-9:
            adjusted[key] = 0.0

    return adjusted


# -------------------------------------------------
# Unified calculation engine
# -------------------------------------------------
def compute_paywise(
    purchase_amount: float,
    interest_rate: float,
    tenure: int,
    processing_fee_base: float,
    fee_mode: str,
    cashback_full: float,
    cashback_emi: float,
    cashback_nocost: float
) -> dict:

    processing_fee_base = max(float(processing_fee_base), 0.0)
    processing_fee_gst = processing_fee_base * GST_RATE
    fee_mode = "Percentage" if str(fee_mode).lower().startswith("p") else "Fixed"

    if fee_mode == "Percentage":
        principal_for_emi = purchase_amount + processing_fee_base + processing_fee_gst
        upfront_processing_fee = 0.0
        upfront_processing_gst = 0.0
    else:
        principal_for_emi = purchase_amount
        upfront_processing_fee = processing_fee_base
        upfront_processing_gst = processing_fee_gst

    if fee_mode is None:
    fee_mode = "Fixed"

    emi = calculate_emi(principal_for_emi, interest_rate, tenure)
    monthly_rate = interest_rate / 12 / 100

    balance = principal_for_emi
    rows = []

    for month in range(1, tenure + 1):
        interest = balance * monthly_rate
        gst_interest = interest * GST_RATE

        principal_paid = emi - interest
        balance -= principal_paid

        processing_fee = upfront_processing_fee if month == 1 else 0
        gst_processing_fee = upfront_processing_gst if month == 1 else 0

        total_payment = (
            emi
            + gst_interest
            + processing_fee
            + gst_processing_fee
        )

        rows.append({
            "Month": month,
            "EMI": emi,
            "Principal Paid": principal_paid,
            "Interest": interest,
            "GST on Interest (@18%)": gst_interest,
            "Processing Fee": processing_fee,
            "GST on Processing Fee (@18%)": gst_processing_fee,
            "Total Payment": total_payment,
            "Principal Remaining": max(balance, 0),
        })

    emi_df = pd.DataFrame(rows)

    # -------------------------------------------------
    # Aggregates (NO CHANGE in meaning)
    # -------------------------------------------------
    total_interest = emi_df["Interest"].sum()
    total_gst_interest = emi_df["GST on Interest (@18%)"].sum()
    total_processing_fee = processing_fee_base
    total_gst_fee = processing_fee_gst

    total_paid = emi_df["Total Payment"].sum()
    total_fee_with_gst = total_processing_fee + total_gst_fee

    totals = {
        "purchase_amount": purchase_amount,
        "total_interest": total_interest,
        "total_gst_interest": total_gst_interest,
        "total_processing_fee": total_processing_fee,
        "total_gst_processing_fee": total_gst_fee,
        "total_paid": total_paid,

        # Effective costs (UNCHANGED semantics)
        "effective_cost_full": (
            purchase_amount
            - cashback_full
        ),
        "effective_cost_emi": (
            total_paid - cashback_emi
        ),
        "effective_cost_nocost": (
            purchase_amount
            + total_gst_interest
            + total_processing_fee
            + total_gst_fee
            - cashback_nocost
        ),
    }

    averages = {
        "avg_monthly_outflow": total_paid / tenure,
        "avg_fee": total_fee_with_gst / tenure,
        "interest_percentage": (total_interest / purchase_amount) * 100,
    }

    comparison = [
        {
            "Mode": "Full Payment",
            "Total Cost": totals["effective_cost_full"],
            "Interest Paid": 0,
            "Processing Fee": 0
        },
        {
            "Mode": "Regular EMI",
            "Total Cost": totals["effective_cost_emi"],
            "Interest Paid": total_interest + total_gst_interest,
            "Processing Fee": total_processing_fee + total_gst_fee,
        },
        {
            "Mode": "No-Cost EMI",
            "Total Cost": totals["effective_cost_nocost"],
            "Interest Paid": 0,
            "Processing Fee": total_processing_fee + total_gst_fee,
        }
    ]

    # -------------------------------------------------
    # Breakdown blocks (gross + net for charts)
    # -------------------------------------------------
    gross_full = {
        "principal": purchase_amount,
        "interest": 0.0,
        "tax": 0.0,
        "fee": 0.0,
    }
    gross_emi = {
        "principal": purchase_amount,
        "interest": total_interest,
        "tax": total_gst_interest,
        "fee": total_fee_with_gst,
    }
    gross_nocost = {
        "principal": purchase_amount,
        "interest": 0.0,
        "tax": total_gst_interest,
        "fee": total_fee_with_gst,
    }

    net_full = apply_cashback_to_components(gross_full, cashback_full)
    net_emi = apply_cashback_to_components(gross_emi, cashback_emi)
    net_nocost = apply_cashback_to_components(gross_nocost, cashback_nocost)

    breakdowns = {
        "full": {
            "gross": gross_full,
            "net": net_full,
            "cashback": cashback_full,
            "net_total": sum(net_full.values()),
        },
        "emi": {
            "gross": gross_emi,
            "net": net_emi,
            "cashback": cashback_emi,
            "net_total": sum(net_emi.values()),
        },
        "nocost": {
            "gross": gross_nocost,
            "net": net_nocost,
            "cashback": cashback_nocost,
            "net_total": sum(net_nocost.values()),
        },
    }

    return {
        "emi_df": emi_df,
        "totals": totals,
        "averages": averages,
        "comparison": comparison,
        "breakdowns": breakdowns
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
    processing_fee,
    fee_mode="Fixed",
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
        fee_mode=fee_mode,
        cashback_full=0,
        cashback_emi=0,
        cashback_nocost=0,
    )

    return data["emi_df"], data["emi_df"]["EMI"].iloc[0]
