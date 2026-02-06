import time
import matplotlib.pyplot as plt
import streamlit as st


THOUSAND_DIVISOR = 1_000


def render_invest_header():
    st.markdown("## 📈 Invest Mode")
    st.markdown("### *Build wealth with step-up SIPs.*")


def render_invest_summary(final):
    st.markdown("### 📌 Executive Summary")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Invested", f"{final['Total Invested']:,.0f}")
    with c2:
        st.metric("Final Nominal Value", f"{final['Nominal Amount']:,.0f}")
    with c3:
        st.metric("Final Real Value", f"{final['Inflation Adjusted Amount']:,.0f}")


def render_invest_donut(invested, real_value):
    gain = real_value - invested
    gain_label = "Real Gain" if gain >= 0 else "Real Loss"
    gain_value = abs(gain)

    values = [invested, gain_value]
    labels = ["Total Invested", gain_label]
    colors = ["#4c72b0", "#55a868" if gain >= 0 else "#c44e52"]

    fig, ax = plt.subplots(figsize=(3.1, 3.1), facecolor="none")
    ax.set_facecolor("none")
    pie_result = ax.pie(
        values,
        startangle=90,
        radius=1.0,
        wedgeprops=dict(width=0.35),
        colors=colors,
    )
    wedges = pie_result[0]

    ax.text(
        0,
        0,
        f"{real_value:,.0f}",
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
        color="white",
    )
    ax.axis("off")
    ax.legend(
        wedges,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.08),
        ncol=2,
        frameon=False,
        fontsize=9,
        labelcolor="white",
    )
    plt.tight_layout()
    st.pyplot(fig, clear_figure=True)


def render_growth_chart(monthly_df, animate=True):
    chart_slot = st.empty()
    total = len(monthly_df)

    def ease_in_out(t):
        return t * t * (3 - 2 * t)

    def draw_chart(subset):
        fig, ax = plt.subplots(figsize=(6.0, 3.0), facecolor="none")
        ax.set_facecolor("#0c1216")
        ax.plot(
            subset["Month Index"],
            subset["Nominal Amount"] / THOUSAND_DIVISOR,
            label="Nominal",
            color="#4c72b0",
            linewidth=2,
        )
        ax.plot(
            subset["Month Index"],
            subset["Inflation Adjusted Amount"] / THOUSAND_DIVISOR,
            label="Real",
            color="#55a868",
            linewidth=2,
        )
        ax.fill_between(
            subset["Month Index"],
            subset["Inflation Adjusted Amount"] / THOUSAND_DIVISOR,
            color="#55a868",
            alpha=0.08,
        )
        ax.set_title("Growth Trend (Thousands)", color="#e9eef4")
        ax.legend(loc="upper left", frameon=False, labelcolor="#e9eef4")
        ax.grid(True, alpha=0.18, color="#cdd6df")
        ax.tick_params(colors="#d7dde4")
        for spine in ax.spines.values():
            spine.set_color("#3a4149")
        chart_slot.pyplot(fig, clear_figure=True)

    if not animate:
        draw_chart(monthly_df)
        return

    frames = 10
    for i in range(1, frames + 1):
        t = i / frames
        eased = ease_in_out(t)
        end = max(1, int(eased * total))
        subset = monthly_df.iloc[:end]
        draw_chart(subset)
        time.sleep(0.01)


def render_invest_overview(final, monthly_df, animate=True):
    st.markdown("### 📊 Investment Overview")

    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        render_invest_donut(final["Total Invested"], final["Inflation Adjusted Amount"])
    with col2:
        render_growth_chart(monthly_df, animate=animate)


def render_invest_milestones(yearly_df, start_year):
    st.markdown("### ⏱️ Growth at 5-Year Milestones")

    milestones = yearly_df[yearly_df["Year"].sub(start_year).mod(5) == 4].copy()
    milestones["Years Completed"] = milestones["Year"] - start_year + 1

    st.dataframe(
        milestones[
            [
                "Years Completed",
                "Total Invested",
                "Nominal Amount",
                "Inflation Adjusted Amount",
            ]
        ].style.format({
            "Years Completed": "{:.0f}",
            "Total Invested": "{:,.0f}",
            "Nominal Amount": "{:,.0f}",
            "Inflation Adjusted Amount": "{:,.0f}",
        }),
        width="stretch",
    )


def render_invest_report(display_df):
    st.markdown("### 📊 Detailed Report")
    st.dataframe(display_df, width="stretch")


def render_invest_disclaimer():
    st.markdown("""
### 📘 Inflation & SIP Explained

Inflation reduces purchasing power over time.  
A return of 12% with 6% inflation means a real return of ~6%.

### ⚠️ Disclaimer
This tool is for educational purposes only. It is not financial advice.
""")
