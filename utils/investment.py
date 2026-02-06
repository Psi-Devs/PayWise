import pandas as pd


def calculate_stepup_sip_inflation_adjusted(
    monthly_sip,
    annual_stepup_percent,
    annual_return_percent,
    annual_inflation_percent,
    years,
    start_year,
):
    monthly_return = (annual_return_percent / 100) / 12
    monthly_inflation = (annual_inflation_percent / 100) / 12
    total_months = years * 12

    nominal = 0.0
    real = 0.0
    invested = 0.0
    start_date = pd.Timestamp(start_year, 1, 1)
    rows = []

    for m in range(1, total_months + 1):
        year_index = (m - 1) // 12
        sip = monthly_sip * ((1 + annual_stepup_percent / 100) ** year_index)

        nominal += sip
        real += sip
        invested += sip

        interest = nominal * monthly_return
        nominal += interest
        real = (real + interest) - (real * monthly_inflation)

        current_date = start_date + pd.DateOffset(months=m - 1)

        rows.append({
            "Year": current_date.year,
            "Month Index": m,
            "Total Invested": invested,
            "Nominal Amount": nominal,
            "Inflation Adjusted Amount": real,
        })

    return pd.DataFrame(rows)


def convert_monthly_to_yearly(df):
    return (
        df.groupby("Year")
        .agg({
            "Total Invested": "last",
            "Nominal Amount": "last",
            "Inflation Adjusted Amount": "last",
        })
        .reset_index()
    )
