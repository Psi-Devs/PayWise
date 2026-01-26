import streamlit as st


def init_scenarios():
    if "scenarios" not in st.session_state:
        st.session_state.scenarios = {}


def save_scenario(name, full, emi, nocost):
    st.session_state.scenarios[name] = {
        "summary": {
            "Full Payment": full,
            "Normal EMI": emi,
            "No-Cost EMI": nocost
        }
    }
