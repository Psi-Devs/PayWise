import matplotlib.pyplot as plt
import streamlit as st


def render_donut(principal, interest, tax, fee, title=None):
    # ----------------------------------
    # Prepare data (filter zeros)
    # ----------------------------------
    components = [
        ("Principal", principal),
        ("Interest", interest),
        ("GST", tax),
        ("Fees", fee),
    ]

    labels = [k for k, v in components if v > 1]
    values = [v for _, v in components if v > 1]

    total = sum(values)

    # ----------------------------------
    # Transparent figure (CRITICAL)
    # ----------------------------------
    fig, ax = plt.subplots(
        figsize=(3.2, 3.2),          # large donut
        facecolor="none"             # 👈 remove white background
    )
    ax.set_facecolor("none")

    # ----------------------------------
    # Donut
    # ----------------------------------
    wedges, _ = ax.pie(
        values,
        startangle=90,
        radius=1.0,                  # full-size donut
        wedgeprops=dict(width=0.35),
    )

    # ----------------------------------
    # Center value (main focus)
    # ----------------------------------
    ax.text(
        0,
        0,
        f"{total:,.0f}",
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
        color="white",               # 👈 works on dark bg
    )

    ax.set_aspect("equal")
    ax.axis("off")                  # 👈 remove axes completely

    # ----------------------------------
    # Minimal legend — corner placement
    # ----------------------------------
    ax.legend(
        wedges,
        labels,
        loc="upper right",
        bbox_to_anchor=(1.25, 1.05), # 👈 push to corner
        frameon=False,
        fontsize=9,
        labelcolor="white",
    )

    # ----------------------------------
    # Tight layout, no padding box
    # ----------------------------------
    plt.tight_layout(pad=0)

    st.pyplot(fig, clear_figure=True)
