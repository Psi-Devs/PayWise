import streamlit as st

from _internal.dark import render_app as render_dark_app
from _internal.light import render_app as render_light_app


def detect_theme() -> str:
    theme_info = getattr(st.context, "theme", {}) or {}
    theme_type = theme_info.get("type")
    if theme_type in {"light", "dark"}:
        return theme_type

    base = st.get_option("theme.base")
    if base in {"light", "dark"}:
        return base

    return "dark"


def _check_theme_and_rerun() -> None:
    current = detect_theme()
    previous = st.session_state.get("_active_theme")

    if previous is None:
        st.session_state["_active_theme"] = current
        return

    if previous != current:
        st.session_state["_active_theme"] = current
        st.rerun()


if hasattr(st, "fragment"):

    @st.fragment(run_every="1s")
    def watch_theme_changes() -> None:
        _check_theme_and_rerun()

else:

    def watch_theme_changes() -> None:
        _check_theme_and_rerun()


def main() -> None:
    st.set_page_config(
        page_title="PayWise – Smart EMI Comparison",
        layout="wide",
        page_icon="assets/favicon.png",
    )

    watch_theme_changes()

    if detect_theme() == "light":
        render_light_app()
    else:
        render_dark_app()


if __name__ == "__main__":
    main()
