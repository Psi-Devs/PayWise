import streamlit as st

from _internal.dark import render_app as render_dark_app
from _internal.light import render_app as render_light_app


def detect_theme() -> str:
    # 1️⃣ Try Streamlit context (works locally sometimes)
    try:
        theme_info = getattr(st.context, "theme", None)
        if theme_info and theme_info.get("type") in ("light", "dark"):
            return theme_info["type"]
    except Exception:
        pass

    # 2️⃣ Try config option (works in some deployments)
    try:
        base = st.get_option("theme.base")
        if base in ("light", "dark"):
            return base
    except Exception:
        pass

    # 3️⃣ Fallback to stored value (important for Cloud)
    if "_active_theme" in st.session_state:
        return st.session_state["_active_theme"]

    # 4️⃣ Final safe default
    return "dark"


def _check_theme_and_rerun() -> None:
    detected = detect_theme()

    if "_active_theme" not in st.session_state:
        st.session_state["_active_theme"] = detected
        return

    if st.session_state["_active_theme"] != detected:
        st.session_state["_active_theme"] = detected
        st.rerun()


# 👇 This keeps watching for theme changes (locally)
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

    # 👇 Ensure theme is initialized ONCE (important for Cloud)
    if "_active_theme" not in st.session_state:
        st.session_state["_active_theme"] = detect_theme()

    watch_theme_changes()

    # ✅ Use cached theme instead of detecting again
    active_theme = st.session_state["_active_theme"]

    if active_theme == "light":
        render_light_app()
    else:
        render_dark_app()


if __name__ == "__main__":
    main()
