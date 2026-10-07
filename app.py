import os
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Smart Rehabilitation Dashboard",
    page_icon="👣",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    data_path = Path(__file__).resolve().parent / "rehabilitation_data.csv"

    if not data_path.exists():
        sample_rows = []
        start_date = pd.Timestamp("2024-01-01")

        for patient_id in ["P001", "P002", "P003"]:
            for offset in range(14):
                current_date = start_date + pd.Timedelta(days=offset)
                base_steps = 4500 + (patient_id[-1] == "1") * 1800 + offset * 80
                sample_rows.append({
                    "patient_id": patient_id,
                    "date": current_date.strftime("%Y-%m-%d"),
                    "steps": int(base_steps + (offset * 75) + (patient_id == "P002") * 500),
                    "distance_km": round((base_steps / 1400) + (patient_id == "P003") * 0.6, 2),
                    "gait_speed_mps": round(1.10 + (offset * 0.01) + (patient_id == "P001") * 0.09, 2),
                    "stride_length_cm": round(66 + (offset * 0.8) + (patient_id == "P002") * 8, 1),
                    "gait_asymmetry_percent": round(8.5 + (offset * 0.2) + (patient_id == "P003") * 2.5, 1),
                    "activity_minutes": int(36 + offset * 2 + (patient_id == "P002") * 8),
                    "energy_harvested_mj": round(14.5 + (offset * 0.7) + (patient_id == "P001") * 3.2, 1),
                })

        pd.DataFrame(sample_rows).to_csv(data_path, index=False)

    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date"])
    return df


df = load_data()

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("👣 Smart Rehabilitation Analytics Dashboard")
st.caption("IoT-Based Patient Rehabilitation Monitoring")

st.divider()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("Dashboard Controls")

patients = df["patient_id"].unique()

selected_patient = st.sidebar.selectbox(
    "Select Patient",
    patients
)

patient_data = df[
    df["patient_id"] == selected_patient
].sort_values("date")

# Date range
min_date = patient_data["date"].min().date()
max_date = patient_data["date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Handle date selection
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:

    start_date = pd.Timestamp(selected_dates[0])
    end_date = pd.Timestamp(selected_dates[1])

    filtered_data = patient_data[
        (patient_data["date"] >= start_date) &
        (patient_data["date"] <= end_date)
    ]

else:
    filtered_data = patient_data


# --------------------------------------------------
# SELECT LATEST DAY
# --------------------------------------------------

latest_data = filtered_data.iloc[-1]

st.subheader(
    f"Patient {selected_patient} — Latest Available Data"
)

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "👣 Steps",
        f"{latest_data['steps']:,}"
    )

with col2:
    st.metric(
        "📏 Distance",
        f"{latest_data['distance_km']:.1f} km"
    )

with col3:
    st.metric(
        "🚶 Gait Speed",
        f"{latest_data['gait_speed_mps']:.2f} m/s"
    )

with col4:
    st.metric(
        "📐 Stride Length",
        f"{latest_data['stride_length_cm']:.0f} cm"
    )


col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric(
        "⚖️ Gait Asymmetry",
        f"{latest_data['gait_asymmetry_percent']:.1f}%"
    )

with col6:
    st.metric(
        "⏱️ Activity",
        f"{latest_data['activity_minutes']} min"
    )

with col7:
    st.metric(
        "⚡ Energy Harvested",
        f"{latest_data['energy_harvested_mj']:.1f} mJ"
    )

with col8:
    st.metric(
        "📅 Date",
        latest_data["date"].strftime("%d %b %Y")
    )

st.divider()

# --------------------------------------------------
# GAIT ANALYSIS
# --------------------------------------------------

st.header("📊 Gait Analysis")

col1, col2 = st.columns(2)

with col1:

    fig_steps = px.line(
        filtered_data,
        x="date",
        y="steps",
        markers=True,
        title="Daily Step Count"
    )

    fig_steps.update_layout(
        xaxis_title="Date",
        yaxis_title="Steps"
    )

    st.plotly_chart(
        fig_steps,
        width="stretch"
    )


with col2:

    fig_distance = px.line(
        filtered_data,
        x="date",
        y="distance_km",
        markers=True,
        title="Daily Walking Distance"
    )

    fig_distance.update_layout(
        xaxis_title="Date",
        yaxis_title="Distance (km)"
    )

    st.plotly_chart(
        fig_distance,
        width="stretch"
    )


col3, col4 = st.columns(2)

with col3:

    fig_speed = px.line(
        filtered_data,
        x="date",
        y="gait_speed_mps",
        markers=True,
        title="Gait Speed Trend"
    )

    fig_speed.update_layout(
        xaxis_title="Date",
        yaxis_title="Speed (m/s)"
    )

    st.plotly_chart(
        fig_speed,
        width="stretch"
    )


with col4:

    fig_stride = px.line(
        filtered_data,
        x="date",
        y="stride_length_cm",
        markers=True,
        title="Stride Length Trend"
    )

    fig_stride.update_layout(
        xaxis_title="Date",
        yaxis_title="Stride Length (cm)"
    )

    st.plotly_chart(
        fig_stride,
        width="stretch"
    )

# --------------------------------------------------
# GAIT ASYMMETRY
# --------------------------------------------------

st.header("⚖️ Gait Asymmetry")

fig_asymmetry = px.line(
    filtered_data,
    x="date",
    y="gait_asymmetry_percent",
    markers=True,
    title="Daily Gait Asymmetry"
)

fig_asymmetry.update_layout(
    xaxis_title="Date",
    yaxis_title="Asymmetry (%)"
)

st.plotly_chart(
    fig_asymmetry,
    width="stretch"
)

# --------------------------------------------------
# ENERGY ANALYSIS
# --------------------------------------------------

st.header("⚡ Energy Harvesting Analysis")

col1, col2 = st.columns(2)

with col1:

    fig_energy = px.bar(
        filtered_data,
        x="date",
        y="energy_harvested_mj",
        title="Daily Energy Harvested"
    )

    fig_energy.update_layout(
        xaxis_title="Date",
        yaxis_title="Energy (mJ)"
    )

    st.plotly_chart(
        fig_energy,
        width="stretch"
    )


with col2:

    fig_activity = px.line(
        filtered_data,
        x="date",
        y="activity_minutes",
        markers=True,
        title="Daily Activity Duration"
    )

    fig_activity.update_layout(
        xaxis_title="Date",
        yaxis_title="Activity (minutes)"
    )

    st.plotly_chart(
        fig_activity,
        width="stretch"
    )

# --------------------------------------------------
# DATA TABLE
# --------------------------------------------------

st.header("📋 Daily Rehabilitation Data")

display_data = filtered_data.copy()

display_data["date"] = display_data["date"].dt.strftime(
    "%Y-%m-%d"
)

st.dataframe(
    display_data,
    width="stretch",
    hide_index=True
)

# --------------------------------------------------
# SIMPLE SUMMARY
# --------------------------------------------------

st.header("📝 Daily Analytics Summary")

avg_steps = filtered_data["steps"].mean()
avg_distance = filtered_data["distance_km"].mean()
avg_speed = filtered_data["gait_speed_mps"].mean()
avg_stride = filtered_data["stride_length_cm"].mean()
avg_asymmetry = filtered_data["gait_asymmetry_percent"].mean()
avg_energy = filtered_data["energy_harvested_mj"].mean()

st.write(
    f"""
    **Patient:** {selected_patient}

    **Average steps:** {avg_steps:,.0f} steps/day

    **Average walking distance:** {avg_distance:.2f} km/day

    **Average gait speed:** {avg_speed:.2f} m/s

    **Average stride length:** {avg_stride:.1f} cm

    **Average gait asymmetry:** {avg_asymmetry:.1f}%

    **Average energy harvested:** {avg_energy:.1f} mJ/day
    """
)

st.divider()

st.caption(
    "Prototype dashboard — sample data only. "
    "Not intended for clinical diagnosis."
)