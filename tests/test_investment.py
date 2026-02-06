import pytest

from utils.investment import (
    calculate_stepup_sip_inflation_adjusted,
    convert_monthly_to_yearly,
)


def test_stepup_sip_basic_growth_no_inflation():
    df = calculate_stepup_sip_inflation_adjusted(
        monthly_sip=1000,
        annual_stepup_percent=0,
        annual_return_percent=12,
        annual_inflation_percent=0,
        years=1,
        start_year=2024,
    )

    assert len(df) == 12
    first = df.iloc[0]
    assert first["Year"] == 2024
    assert first["Month Index"] == 1
    assert first["Total Invested"] == pytest.approx(1000)
    assert first["Nominal Amount"] == pytest.approx(1010)
    assert first["Inflation Adjusted Amount"] == pytest.approx(1010)

    second = df.iloc[1]
    assert second["Total Invested"] == pytest.approx(2000)
    assert second["Nominal Amount"] == pytest.approx(2030.1)


def test_stepup_applies_after_one_year():
    df = calculate_stepup_sip_inflation_adjusted(
        monthly_sip=1000,
        annual_stepup_percent=10,
        annual_return_percent=10,
        annual_inflation_percent=0,
        years=2,
        start_year=2024,
    )

    invested_month_12 = df.iloc[11]["Total Invested"]
    invested_month_13 = df.iloc[12]["Total Invested"]

    assert invested_month_13 - invested_month_12 == pytest.approx(1100)


def test_convert_monthly_to_yearly_uses_last_row_per_year():
    df = calculate_stepup_sip_inflation_adjusted(
        monthly_sip=500,
        annual_stepup_percent=0,
        annual_return_percent=8,
        annual_inflation_percent=0,
        years=2,
        start_year=2024,
    )
    yearly = convert_monthly_to_yearly(df)

    assert len(yearly) == 2
    assert yearly.iloc[0]["Year"] == 2024
    assert yearly.iloc[1]["Year"] == 2025

    last_2024 = df[df["Year"] == 2024].iloc[-1]
    assert yearly.iloc[0]["Total Invested"] == pytest.approx(last_2024["Total Invested"])
    assert yearly.iloc[0]["Nominal Amount"] == pytest.approx(last_2024["Nominal Amount"])
    assert yearly.iloc[0]["Inflation Adjusted Amount"] == pytest.approx(
        last_2024["Inflation Adjusted Amount"]
    )
