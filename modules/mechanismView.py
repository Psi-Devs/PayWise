import streamlit as st

def render_mechanism_view(data):
    st.subheader("📘 How EMI Works")

    st.markdown("""
    **EMI = Principal + Interest**

    - Interest is calculated on outstanding balance
    - Early EMIs are interest-heavy
    - No-Cost EMI usually hides cost in fees or cashback loss

    **Rule:**  
    Always compare **effective total cost**, not EMI size.
    """)

    st.info(
        f"In your case, total interest paid is ₹{data['totals']['total_interest']:,}."
    )
