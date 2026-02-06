from dataclasses import dataclass


@dataclass(frozen=True)
class PaywiseSummary:
    total_interest: float
    total_gst_interest: float
    total_fee_with_gst: float
    full_total: float
    normal_total: float
    no_cost_total: float
    avg_monthly: float
    avg_principal: float
    avg_interest: float
    avg_tax: float
    avg_fee: float


def build_paywise_summary(purchase_amount: float, tenure: int, data: dict) -> PaywiseSummary:
    totals = data["totals"]

    total_interest = totals["total_interest"]
    total_gst_interest = totals["total_gst_interest"]
    total_fee_with_gst = totals["total_processing_fee"] + totals["total_gst_processing_fee"]

    full_total = totals["effective_cost_full"]
    normal_total = totals["effective_cost_emi"]
    no_cost_total = totals["effective_cost_nocost"]

    avg_monthly = data["averages"]["avg_monthly_outflow"]
    avg_principal = purchase_amount / tenure
    avg_interest = total_interest / tenure
    avg_tax = total_gst_interest / tenure
    avg_fee = total_fee_with_gst / tenure

    return PaywiseSummary(
        total_interest=total_interest,
        total_gst_interest=total_gst_interest,
        total_fee_with_gst=total_fee_with_gst,
        full_total=full_total,
        normal_total=normal_total,
        no_cost_total=no_cost_total,
        avg_monthly=avg_monthly,
        avg_principal=avg_principal,
        avg_interest=avg_interest,
        avg_tax=avg_tax,
        avg_fee=avg_fee,
    )
