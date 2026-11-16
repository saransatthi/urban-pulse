import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Urban Pulse",
    page_icon="🏙️",
    layout="wide"
)

st.title("🏙️ Urban Pulse")
st.caption("Urban Waste Management Dashboard")

# Load ZIP dataset
@st.cache_data
def load_data():
    df = pd.read_csv(
        "urban_pulse_cleaned1.zip",
        compression="zip"
    )

    df["created_date"] = pd.to_datetime(
        df["created_date"], errors="coerce"
    )

    df["resolution_hours"] = pd.to_numeric(
        df["resolution_hours"], errors="coerce"
    )

    df["latitude"] = pd.to_numeric(
        df["latitude"], errors="coerce"
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"], errors="coerce"
    )

    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Dataset loading failed: {e}")
    st.stop()

st.success(f"Dataset Loaded Successfully! Total Records: {len(df):,}")

# KPI Metrics
total_requests = len(df)

closed_count = (df["status"] == "Closed").sum()
closure_percentage = (
    closed_count / total_requests * 100
    if total_requests else 0
)

open_requests = (df["status"] == "Open").sum()

valid_resolution = df.loc[
    df["resolution_hours"] >= 0, "resolution_hours"
]

median_resolution = (
    valid_resolution.median()
    if not valid_resolution.empty else 0
)

over_72_percentage = (
    (valid_resolution > 72).sum() / len(valid_resolution) * 100
    if len(valid_resolution) else 0
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Requests", f"{total_requests:,}")
c2.metric("Recorded Closure %", f"{closure_percentage:.2f}%")
c3.metric("Open Requests", f"{open_requests:,}")
c4.metric("Median Resolution Hours", f"{median_resolution:.2f} hrs")
c5.metric("Over 72 Hours %", f"{over_72_percentage:.2f}%")

# Complaint Type Analysis
st.subheader("Complaint Type Analysis")

df_complaints = (
    df["complaint_type"]
    .value_counts()
    .head(10)
)

st.bar_chart(df_complaints)

# Agency Workload Analysis
st.subheader("Agency Workload Analysis")

df_agency = (
    df["agency"]
    .value_counts()
)

st.bar_chart(df_agency)

# Borough-wise Analysis
st.subheader("Borough-wise Requests Analysis")

df_borough = (
    df["borough"]
    .value_counts()
)

st.bar_chart(df_borough)

# Monthly Complaint Trend
st.subheader("Monthly Complaint Trend")

df_monthly = (
    df.dropna(subset=["created_date"])
    .assign(complaint_month=lambda x: x["created_date"].dt.to_period("M").astype(str))
    .groupby("complaint_month")
    .size()
)

st.line_chart(df_monthly)

# Weekday and Hour Analysis
st.subheader("Weekday & Hour Analysis")

df_time = (
    df.groupby(["weekday", "hour"])
    .size()
    .reset_index(name="complaint_count")
)

st.dataframe(df_time, use_container_width=True)

# Resolution Analysis
st.subheader("Resolution Analysis")

df_resolution = pd.DataFrame({
    "Average Hours": [valid_resolution.mean()],
    "Minimum Hours": [valid_resolution.min()],
    "Maximum Hours": [valid_resolution.max()]
})

st.dataframe(df_resolution, use_container_width=True)

# Interactive Filters
st.subheader("Interactive Filters")

col1, col2, col3 = st.columns(3)

with col1:
    borough_options = sorted(df["borough"].dropna().unique().tolist())
    selected_borough = st.selectbox(
        "Select Borough", ["All"] + borough_options
    )

with col2:
    complaint_options = sorted(df["complaint_type"].dropna().unique().tolist())
    selected_complaint = st.selectbox(
        "Select Complaint Type", ["All"] + complaint_options
    )

with col3:
    status_options = sorted(df["status"].dropna().unique().tolist())
    selected_status = st.selectbox(
        "Select Status", ["All"] + status_options
    )

df_filtered = df.copy()

if selected_borough != "All":
    df_filtered = df_filtered[
        df_filtered["borough"] == selected_borough
    ]

if selected_complaint != "All":
    df_filtered = df_filtered[
        df_filtered["complaint_type"] == selected_complaint
    ]

if selected_status != "All":
    df_filtered = df_filtered[
        df_filtered["status"] == selected_status
    ]

# Filtered Records
st.subheader("Filtered Complaint Records")

st.write("Total Filtered Records:", f"{len(df_filtered):,}")

st.dataframe(df_filtered, use_container_width=True)

# Geographic Complaint Concentration
st.subheader("Geographic Complaint Concentration")

df_map = df_filtered[
    ["latitude", "longitude"]
].dropna().copy()

st.map(
    df_map,
    latitude="latitude",
    longitude="longitude"
)
