import pytest

from utils.calculations import compute_paywise, GST_RATE


def test_zero_interest_fixed_fee():
    purchase = 12000
    tenure = 12
    fee = 300

    data = compute_paywise(
        purchase_amount=purchase,
        interest_rate=0.0,
        tenure=tenure,
        processing_fee_base=fee,
        fee_mode="Fixed",
        cashback_full=0,
        cashback_emi=0,
        cashback_nocost=0,
    )

    emi_df = data["emi_df"]
    totals = data["totals"]

    assert emi_df["EMI"].iloc[0] == pytest.approx(purchase / tenure, abs=1e-9)
    assert totals["total_interest"] == pytest.approx(0.0, abs=1e-9)
    assert totals["total_gst_interest"] == pytest.approx(0.0, abs=1e-9)

    assert emi_df["Processing Fee"].sum() == pytest.approx(fee, abs=1e-9)
    assert emi_df["GST on Processing Fee (@18%)"].sum() == pytest.approx(
        fee * GST_RATE, abs=1e-9
    )

    expected_total = purchase + fee + (fee * GST_RATE)
    assert totals["total_paid"] == pytest.approx(expected_total, abs=1e-9)
    assert totals["effective_cost_emi"] == pytest.approx(expected_total, abs=1e-9)
    assert totals["effective_cost_full"] == pytest.approx(purchase, abs=1e-9)


def test_zero_interest_percentage_fee_financed():
    purchase = 100000
    tenure = 10
    fee = 1000
    fee_gst = fee * GST_RATE
    principal_for_emi = purchase + fee + fee_gst

    data = compute_paywise(
        purchase_amount=purchase,
        interest_rate=0.0,
        tenure=tenure,
        processing_fee_base=fee,
        fee_mode="Percentage",
        cashback_full=0,
        cashback_emi=0,
        cashback_nocost=0,
    )

    emi_df = data["emi_df"]
    totals = data["totals"]

    assert emi_df["EMI"].iloc[0] == pytest.approx(
        principal_for_emi / tenure, abs=1e-9
    )
    assert emi_df["Processing Fee"].sum() == pytest.approx(0.0, abs=1e-9)
    assert emi_df["GST on Processing Fee (@18%)"].sum() == pytest.approx(0.0, abs=1e-9)

    assert totals["total_processing_fee"] == pytest.approx(fee, abs=1e-9)
    assert totals["total_gst_processing_fee"] == pytest.approx(fee_gst, abs=1e-9)
    assert totals["total_paid"] == pytest.approx(principal_for_emi, abs=1e-9)
    assert totals["effective_cost_emi"] == pytest.approx(principal_for_emi, abs=1e-9)

    net_total = data["breakdowns"]["emi"]["net_total"]
    assert net_total == pytest.approx(totals["effective_cost_emi"], abs=1e-6)


def test_cashback_applies_to_breakdown():
    cashback = 1000
    data = compute_paywise(
        purchase_amount=50000,
        interest_rate=12.0,
        tenure=12,
        processing_fee_base=200,
        fee_mode="Fixed",
        cashback_full=0,
        cashback_emi=cashback,
        cashback_nocost=0,
    )

    gross_total = sum(data["breakdowns"]["emi"]["gross"].values())
    net_total = sum(data["breakdowns"]["emi"]["net"].values())

    assert net_total == pytest.approx(gross_total - cashback, abs=0.01)
    assert net_total == pytest.approx(data["totals"]["effective_cost_emi"], abs=0.01)
    assert net_total <= gross_total
