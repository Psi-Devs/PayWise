from utils.invest_pdf import generate_invest_pdf_bytes
from utils.investment import (
    calculate_stepup_sip_inflation_adjusted,
    convert_monthly_to_yearly,
)


def test_generate_invest_pdf_bytes_smoke():
    monthly_df = calculate_stepup_sip_inflation_adjusted(
        monthly_sip=1000,
        annual_stepup_percent=0,
        annual_return_percent=12,
        annual_inflation_percent=0,
        years=1,
        start_year=2024,
    )
    yearly_df = convert_monthly_to_yearly(monthly_df)

    pdf_buffer = generate_invest_pdf_bytes(
        monthly_df=monthly_df,
        yearly_df=yearly_df,
        monthly_sip=1000,
        stepup_percent=0,
        annual_return_percent=12,
        annual_inflation_percent=0,
        years=1,
        start_year=2024,
    )

    pdf_bytes = pdf_buffer.getvalue()
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000
