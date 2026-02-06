# 💳 PayWise v2

**PayWise** is a Streamlit app for transparent **EMI comparison** and a **Step-Up SIP investment** view.

## Modes
- **PayWise**: Compare Full Payment, Regular EMI, and No-Cost EMI with GST, fees, and cashback.
- **Invest**: Step-Up SIP growth with inflation-adjusted views and a PDF report.

## PayWise Features
- Honest No-Cost EMI calculation
- Full payment vs EMI comparison
- GST and processing fee included
- Cashback support
- Monthly and yearly schedules
- Simple, Detailed, and Mechanism views
- PDF export with breakdowns

## Invest Features
- Step-Up SIP projection with expected returns
- Inflation-adjusted (real) value tracking
- Growth chart and donut summary
- 5-year milestones table
- Monthly or yearly report view
- PDF export with glossary

## Project Structure
- `PayWise.py` main Streamlit app and mode toggle
- `modules/` UI views and Invest sections
- `utils/calculations.py` EMI calculation engine
- `utils/paywise_summary.py` PayWise summary builder for UI views
- `utils/investment.py` SIP calculations
- `utils/pdf_export.py` PayWise PDF report
- `utils/invest_pdf.py` Invest PDF report
- `tests/` unit tests for PayWise and Invest calculations/PDFs
- `prototypes/PayWiseV2.py` legacy prototype snapshot

## Notes
- Scenario saving/history is intentionally removed in this version.
- Percentage-based processing fees are financed into the EMI principal.
- Fixed processing fees are charged upfront in month 1.
- This tool is for educational purposes only. Not financial advice.

## 🌐 Run Locally
```bash
pip install -r requirements.txt
python -m streamlit run PayWise.py
```

## 🧪 Tests
```bash
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest
```

## 🧹 Lint / Format
```bash
pip install -r requirements-dev.txt
python -m ruff check .
python -m ruff format .
```
