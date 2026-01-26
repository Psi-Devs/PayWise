import streamlit as st
import pandas as pd
from utils.charts import cost_comparison_bar

def render_comparison_view(data):
    st.subheader("🔍 Payment Mode Comparison")

    df = pd.DataFrame(data["comparison"])
    st.dataframe(df, use_container_width=True)

    fig = cost_comparison_bar(data["comparison"])
    st.pyplot(fig)
