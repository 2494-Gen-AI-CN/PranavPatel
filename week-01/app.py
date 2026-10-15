
# SECTION 1: Import the frontend library and our backend functions
from datetime import date

import pandas as pd
import streamlit as st

from backend import (
    PLATFORMS,
    add_delivery,
    calculate_earnings,
    load_deliveries,
    platform_deliveries,
    summarize_deliveries,
)


# SECTION 2: Page settings and data loading
st.set_page_config(
    page_title="DeliveryIQ | Earnings Analyzer",
    layout="wide",
)

st.title("DeliveryIQ")
st.caption("Analyze delivery offers, track completed trips, and compare platforms.")

with st.sidebar:
    st.header("Settings")
    cost_per_km = st.number_input(
        "Estimated vehicle cost (CAD/km)",
        min_value=0.0,
        value=0.25,
        step=0.05,
        format="%.2f",
    )
    st.caption("An editable assumption, not an actual fuel or tax calculation.")
    st.info("This app uses manually entered data. It is not connected to delivery accounts.")

try:
    deliveries = load_deliveries()
except ValueError as error:
    st.error(str(error))
    st.stop()

if "saved_message" in st.session_state:
    st.success(st.session_state.pop("saved_message"))


# SECTION 3: Navigation tabs
# Streamlit automatically draws the frontend: forms, charts, and buttons.
tab_dashboard, tab_analyze, tab_add, tab_history, tab_compare = st.tabs(
    ["Dashboard", "Offer Analyzer", "Add Delivery", "History", "Compare"]
)


# SECTION 4: Dashboard: totals and chart
with tab_dashboard:
    st.subheader("Earnings dashboard")
    st.write("Summary of the deliveries you've recorded.")

    today = date.today().isoformat()
    todays_deliveries = [d for d in deliveries if d["date"] == today]
    today_report = summarize_deliveries(todays_deliveries, cost_per_km)
    all_time_report = summarize_deliveries(deliveries, cost_per_km)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Today's gross", f"${today_report['gross']:.2f}")
    col2.metric("Today's after costs", f"${today_report['after_costs']:.2f}")
    col3.metric("Today's deliveries", today_report["count"])
    col4.metric("Today's distance", f"{today_report['distance']:.1f} km")

    st.divider()
    st.subheader("All-time performance")
    col1, col2, col3 = st.columns(3)
    col1.metric("Gross earned", f"${all_time_report['gross']:.2f}")
    col2.metric("Estimated after costs", f"${all_time_report['after_costs']:.2f}")
    col3.metric("Gross per delivery hour", f"${all_time_report['gross_per_hour']:.2f}")

    st.subheader("Gross earnings by platform")
    if deliveries:
        chart_rows = []
        for platform in PLATFORMS:
            platform_records = platform_deliveries(deliveries, platform)
            report = summarize_deliveries(platform_records, cost_per_km)
            chart_rows.append({"Platform": platform, "Gross earnings (CAD)": report["gross"]})

        chart_data = pd.DataFrame(chart_rows).set_index("Platform")
        st.bar_chart(chart_data)
    else:
        st.info("Add your first completed delivery to see the dashboard chart.")

    st.caption("Rates use recorded delivery minutes, not the time spent waiting for orders. Taxes are excluded.")


# SECTION 5: Offer Analyzer: inputs -> backend calculation -> results
with tab_analyze:
    st.subheader("Analyze a potential offer")
    st.write("Enter an offer to calculate estimated earnings. Nothing is saved here.")

    with st.form("offer_form"):
        offer_platform = st.selectbox("Platform", PLATFORMS, key="offer_platform")
        left, right = st.columns(2)
        with left:
            offer_payment = st.number_input("Offered payment (CAD)", min_value=0.0, value=12.50, step=0.50)
            offer_distance = st.number_input("Distance (km)", min_value=0.1, value=6.0, step=0.5)
        with right:
            offer_minutes = st.number_input("Estimated minutes", min_value=1, value=25, step=1)

        analyze_clicked = st.form_submit_button("Analyze offer", type="primary")

    if analyze_clicked:
        answer = calculate_earnings(
            offer_payment, offer_distance, offer_minutes, cost_per_km
        )
        st.subheader(f"{offer_platform} — estimated results")
        a, b, c, d = st.columns(4)
        a.metric("Gross per hour", f"${answer['gross_per_hour']:.2f}")
        b.metric("Gross per km", f"${answer['gross_per_km']:.2f}")
        c.metric("Vehicle expense", f"${answer['expenses']:.2f}")
        d.metric("After vehicle costs", f"${answer['after_costs']:.2f}")
        st.caption("Offer estimates assume the given time and distance are accurate.")


# SECTION 6: Completed deliveries form -> backend -> JSON file
with tab_add:
    st.subheader("Record a completed delivery")
    st.write("A completed delivery is saved and will appear in your reports.")

    with st.form("add_delivery_form", clear_on_submit=True):
        completed_platform = st.selectbox("Platform", PLATFORMS, key="completed_platform")
        completed_date = st.date_input("Delivery date", value=date.today())
        left, right = st.columns(2)
        with left:
            completed_payment = st.number_input("Earned amount (CAD)", min_value=0.0, value=10.0, step=0.50)
            completed_distance = st.number_input("Distance (km)", min_value=0.1, value=5.0, step=0.5)
        with right:
            completed_minutes = st.number_input("Delivery minutes", min_value=1, value=20, step=1)

        save_clicked = st.form_submit_button("Save completed delivery", type="primary")

    if save_clicked:
        try:
            add_delivery(
                deliveries, completed_platform, completed_payment,
                completed_distance, completed_minutes, completed_date
            )
        except (OSError, ValueError) as error:
            st.error(f"Could not save delivery: {error}")
        else:
            st.session_state["saved_message"] = "Delivery saved! Dashboard and history updated."
            st.rerun()


# SECTION 7: History: turn saved records into a readable table
with tab_history:
    st.subheader("Delivery history")

    if not deliveries:
        st.info("No completed deliveries have been recorded yet.")
    else:
        history_rows = []
        for delivery in deliveries:
            result = calculate_earnings(
                delivery["payment"], delivery["distance"],
                delivery["minutes"], cost_per_km
            )
            history_rows.append({
                "Date": delivery["date"],
                "Platform": delivery["platform"],
                "Gross (CAD)": round(delivery["payment"], 2),
                "Distance (km)": delivery["distance"],
                "Minutes": delivery["minutes"],
                "After costs (CAD)": round(result["after_costs"], 2),
            })

        history_rows.sort(key=lambda row: row["Date"], reverse=True)
        st.dataframe(pd.DataFrame(history_rows), hide_index=True, use_container_width=True)
        st.caption("After-cost amounts are recalculated using the current sidebar cost setting.")


# SECTION 8: Platform comparison: reuse the summary function twice
with tab_compare:
    st.subheader("Compare Uber Eats and DoorDash")
    left, right = st.columns(2)

    for column, platform in zip((left, right), PLATFORMS):
        report = summarize_deliveries(
            platform_deliveries(deliveries, platform), cost_per_km
        )
        with column:
            st.markdown(f"### {platform}")
            st.metric("Completed deliveries", report["count"])
            st.metric("Gross earnings", f"${report['gross']:.2f}")
            st.metric("Estimated after costs", f"${report['after_costs']:.2f}")
            st.metric("Gross per delivery hour", f"${report['gross_per_hour']:.2f}")

    st.caption("These comparisons reflect only the deliveries you entered, not guaranteed future earnings.")
