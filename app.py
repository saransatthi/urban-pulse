import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Urban Pulse",
    page_icon="🏙️",
    layout="wide"
)

from pathlib import Path

DATA_FILE = Path(_file_).resolve().parent / "urban_pulse_cleaned1.zip"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE, compression="zip")
    df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
    df["closed_date"] = pd.to_datetime(df["closed_date"], errors="coerce")
    df["resolution_hours"] = pd.to_numeric(df["resolution_hours"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Dataset loading failed: {e}")
    st.info("Check that Urban_pulse_cleaned1.zip is in the same GitHub folder as app.py.")
    st.stop()

st.sidebar.title("🏙️ Urban Pulse")
st.sidebar.caption("Urban Waste Management")
pages = [
    "Main Dashboard",
    "1. Total Requests",
    "2. Top 10 Complaint Types",
    "3. Agency Workload",
    "4. Request Volume by Borough",
    "5. Complaint Status",
    "6. Borough-wise Status",
    "7. Average Resolution by Borough",
    "8. Minimum & Maximum Resolution",
    "9. Monthly Complaint Trend",
    "10. Hour-wise Complaint Analysis",
    "11. Weekday-wise Complaint Analysis",
    "12. Open Complaints by Borough",
    "13. Top 10 Agencies",
    "14. Complaints Over 72 Hours",
    "15. Overall Average Resolution Time",
]
selected_page = st.sidebar.radio("Navigate", pages)
st.sidebar.divider()
st.sidebar.caption(f"Dataset records: {len(df):,}")

valid_resolution = df.loc[df["resolution_hours"] >= 0, "resolution_hours"].dropna()

def show_sql(sql):
    with st.expander("View SQL Query"):
        st.code(sql.strip(), language="sql")

def show_result(data, chart_type=None, x=None, y=None):
    st.dataframe(data, use_container_width=True)
    if chart_type == "bar" and not data.empty:
        st.bar_chart(data.set_index(x)[y])
    elif chart_type == "line" and not data.empty:
        st.line_chart(data.set_index(x)[y])

def main_dashboard():
    st.title("🏙️ Urban Pulse")
    st.caption("Urban Waste Management Dashboard")

    total_requests = df["unique_key"].nunique()
    closed_count = (df["status"].astype(str).str.lower() == "closed").sum()
    open_count = (df["status"].astype(str).str.lower() == "open").sum()
    closure_pct = closed_count / len(df) * 100 if len(df) else 0
    median_hours = valid_resolution.median() if not valid_resolution.empty else 0
    over72_pct = (valid_resolution > 72).mean() * 100 if not valid_resolution.empty else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Requests", f"{total_requests:,}")
    c2.metric("Recorded Closure %", f"{closure_pct:.2f}%")
    c3.metric("Open Requests", f"{open_count:,}")
    c4.metric("Median Resolution Hours", f"{median_hours:.2f} hrs")
    c5.metric("Over 72 Hours %", f"{over72_pct:.2f}%")

    st.subheader("Complaint Type Analysis")
    complaint_counts = df["complaint_type"].value_counts().head(10)
    st.bar_chart(complaint_counts)

    st.subheader("Agency Workload Analysis")
    st.bar_chart(df["agency"].value_counts())

    st.subheader("Borough-wise Requests Analysis")
    st.bar_chart(df["borough"].value_counts())

    st.subheader("Monthly Complaint Trend")
    monthly = (
        df.dropna(subset=["created_date"])
          .assign(complaint_month=lambda x: x["created_date"].dt.to_period("M").astype(str))
          .groupby("complaint_month").size()
          .rename("complaint_count")
    )
    st.line_chart(monthly)

    st.subheader("Weekday & Hour Analysis")
    time_data = df.groupby(["weekday", "hour"]).size().reset_index(name="complaint_count")
    st.dataframe(time_data, use_container_width=True)

    st.subheader("Resolution Analysis")
    resolution_summary = pd.DataFrame({
        "Average Hours": [valid_resolution.mean()],
        "Minimum Hours": [valid_resolution.min()],
        "Maximum Hours": [valid_resolution.max()]
    })
    st.dataframe(resolution_summary, use_container_width=True)

    st.subheader("Interactive Filters")
    f1, f2, f3 = st.columns(3)
    with f1:
        boroughs = sorted(df["borough"].dropna().unique().tolist())
        borough = st.selectbox("Select Borough", ["All"] + boroughs)
    with f2:
        types = sorted(df["complaint_type"].dropna().unique().tolist())
        complaint = st.selectbox("Select Complaint Type", ["All"] + types)
    with f3:
        statuses = sorted(df["status"].dropna().unique().tolist())
        status = st.selectbox("Select Status", ["All"] + statuses)

    filtered = df.copy()
    if borough != "All":
        filtered = filtered[filtered["borough"] == borough]
    if complaint != "All":
        filtered = filtered[filtered["complaint_type"] == complaint]
    if status != "All":
        filtered = filtered[filtered["status"] == status]

    st.subheader("Geographic Complaint Concentration")
    map_data = filtered[["latitude", "longitude"]].dropna()
    st.map(map_data, latitude="latitude", longitude="longitude")
    st.write("Total Filtered Records:", f"{len(filtered):,}")
    st.subheader("Filtered Complaint Records")
    st.dataframe(filtered, use_container_width=True)

def query_page(page):
    st.title("🏙️ Urban Pulse | SQL Query Results")
    st.header(page)

    if page == "1. Total Requests":
        result = pd.DataFrame({"Total_Requests": [df["unique_key"].nunique()]})
        show_sql("""SELECT COUNT(DISTINCT unique_key) AS Total_Requests
FROM service_requests;""")
        st.metric("Total Requests", f'{result.iloc[0, 0]:,}')
        st.dataframe(result, use_container_width=True)

    elif page == "2. Top 10 Complaint Types":
        result = df.groupby("complaint_type").size().reset_index(name="Complaint_Count")
        result = result.sort_values("Complaint_Count", ascending=False).head(10)
        show_sql("""SELECT complaint_type, COUNT(*) AS Complaint_Count
FROM service_requests
GROUP BY complaint_type
ORDER BY Complaint_Count DESC
LIMIT 10;""")
        show_result(result, "bar", "complaint_type", "Complaint_Count")

    elif page == "3. Agency Workload":
        result = df.groupby("agency").size().reset_index(name="Complaint_Count")
        result = result.sort_values("Complaint_Count", ascending=False)
        show_sql("""SELECT agency, COUNT(*) AS Complaint_Count
FROM service_requests
GROUP BY agency
ORDER BY Complaint_Count DESC;""")
        show_result(result, "bar", "agency", "Complaint_Count")

    elif page == "4. Request Volume by Borough":
        result = df.groupby("borough").size().reset_index(name="Complaint_Count")
        result = result.sort_values("Complaint_Count", ascending=False)
        show_sql("""SELECT borough, COUNT(*) AS Complaint_Count
FROM service_requests
GROUP BY borough
ORDER BY Complaint_Count DESC;""")
        show_result(result, "bar", "borough", "Complaint_Count")

    elif page == "5. Complaint Status":
        result = df.groupby("status").size().reset_index(name="Complaint_Count")
        result = result.sort_values("Complaint_Count", ascending=False)
        show_sql("""SELECT status, COUNT(*) AS Complaint_Count
FROM service_requests
GROUP BY status
ORDER BY Complaint_Count DESC;""")
        show_result(result, "bar", "status", "Complaint_Count")

    elif page == "6. Borough-wise Status":
        result = df.groupby(["borough", "status"]).size().reset_index(name="Complaint_Count")
        result = result.sort_values(["borough", "Complaint_Count"], ascending=[True, False])
        show_sql("""SELECT borough, status, COUNT(*) AS Complaint_Count
FROM service_requests
GROUP BY borough, status
ORDER BY borough, Complaint_Count DESC;""")
        st.dataframe(result, use_container_width=True)
        if not result.empty:
            pivot = result.pivot(index="borough", columns="status", values="Complaint_Count").fillna(0)
            st.bar_chart(pivot)

    elif page == "7. Average Resolution by Borough":
        result = (df.dropna(subset=["resolution_hours"])
                    .groupby("borough")["resolution_hours"].mean()
                    .round(2).reset_index(name="Average_Resolution_Hours")
                    .sort_values("Average_Resolution_Hours", ascending=False))
        show_sql("""SELECT borough, ROUND(AVG(resolution_hours), 2) AS Average_Resolution_Hours
FROM service_requests
WHERE resolution_hours IS NOT NULL
GROUP BY borough
ORDER BY Average_Resolution_Hours DESC;""")
        show_result(result, "bar", "borough", "Average_Resolution_Hours")

    elif page == "8. Minimum & Maximum Resolution":
        result = pd.DataFrame({
            "Minimum_Resolution_Hours": [df["resolution_hours"].min()],
            "Maximum_Resolution_Hours": [df["resolution_hours"].max()]
        })
        show_sql("""SELECT MIN(resolution_hours) AS Minimum_Resolution_Hours,
       MAX(resolution_hours) AS Maximum_Resolution_Hours
FROM service_requests
WHERE resolution_hours IS NOT NULL;""")
        a, b = st.columns(2)
        a.metric("Minimum Resolution Hours", f'{result.iloc[0, 0]:,.2f}')
        b.metric("Maximum Resolution Hours", f'{result.iloc[0, 1]:,.2f}')
        st.dataframe(result, use_container_width=True)

    elif page == "9. Monthly Complaint Trend":
        result = (df.dropna(subset=["created_date"])
                    .assign(Complaint_Year=lambda x: x["created_date"].dt.year,
                            Complaint_Month=lambda x: x["created_date"].dt.month)
                    .groupby(["Complaint_Year", "Complaint_Month"]).size()
                    .reset_index(name="Complaint_Count")
                    .sort_values(["Complaint_Year", "Complaint_Month"]))
        result["Month"] = pd.to_datetime(
            result["Complaint_Year"].astype(str) + "-" +
            result["Complaint_Month"].astype(str).str.zfill(2) + "-01"
        ).dt.strftime("%Y-%m")
        show_sql("""SELECT YEAR(created_date) AS Complaint_Year,
       MONTH(created_date) AS Complaint_Month, COUNT(*) AS Complaint_Count
FROM service_requests
WHERE created_date IS NOT NULL
GROUP BY YEAR(created_date), MONTH(created_date)
ORDER BY Complaint_Year, Complaint_Month;""")
        show_result(result[["Complaint_Year", "Complaint_Month", "Complaint_Count", "Month"]],
                    "line", "Month", "Complaint_Count")

    elif page == "10. Hour-wise Complaint Analysis":
        result = (df.dropna(subset=["created_date"])
                    .assign(Complaint_Hour=lambda x: x["created_date"].dt.hour)
                    .groupby("Complaint_Hour").size()
                    .reset_index(name="Complaint_Count")
                    .sort_values("Complaint_Hour"))
        show_sql("""SELECT HOUR(created_date) AS Complaint_Hour, COUNT(*) AS Complaint_Count
FROM service_requests
WHERE created_date IS NOT NULL
GROUP BY HOUR(created_date)
ORDER BY Complaint_Hour;""")
        show_result(result, "bar", "Complaint_Hour", "Complaint_Count")

    elif page == "11. Weekday-wise Complaint Analysis":
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        result = df.groupby("weekday").size().reset_index(name="Complaint_Count")
        result["_order"] = result["weekday"].map({d: i for i, d in enumerate(weekday_order)})
        result = result.sort_values("Complaint_Count", ascending=False).drop(columns="_order")
        show_sql("""SELECT DAYNAME(created_date) AS Complaint_Day, COUNT(*) AS Complaint_Count
FROM service_requests
WHERE created_date IS NOT NULL
GROUP BY DAYNAME(created_date)
ORDER BY Complaint_Count DESC;""")
        show_result(result, "bar", "weekday", "Complaint_Count")

    elif page == "12. Open Complaints by Borough":
        result = (df[df["status"].astype(str).str.lower() == "open"]
                    .groupby("borough").size()
                    .reset_index(name="Open_Complaint_Count")
                    .sort_values("Open_Complaint_Count", ascending=False))
        show_sql("""SELECT borough, COUNT(*) AS Open_Complaint_Count
FROM service_requests
WHERE status = 'Open'
GROUP BY borough
ORDER BY Open_Complaint_Count DESC;""")
        show_result(result, "bar", "borough", "Open_Complaint_Count")

    elif page == "13. Top 10 Agencies":
        result = df.groupby("agency").size().reset_index(name="Complaint_Count")
        result = result.sort_values("Complaint_Count", ascending=False).head(10)
        show_sql("""SELECT agency, COUNT(*) AS Complaint_Count
FROM service_requests
GROUP BY agency
ORDER BY Complaint_Count DESC
LIMIT 10;""")
        show_result(result, "bar", "agency", "Complaint_Count")

    elif page == "14. Complaints Over 72 Hours":
        count = int((df["resolution_hours"] > 72).sum())
        result = pd.DataFrame({"Complaints_Over_72_Hours": [count]})
        show_sql("""SELECT COUNT(*) AS Complaints_Over_72_Hours
FROM service_requests
WHERE resolution_hours > 72;""")
        st.metric("Complaints Over 72 Hours", f"{count:,}")
        st.dataframe(result, use_container_width=True)

    elif page == "15. Overall Average Resolution Time":
        average = df["resolution_hours"].mean()
        result = pd.DataFrame({"Average_Resolution_Hours": [round(average, 2)]})
        show_sql("""SELECT ROUND(AVG(resolution_hours), 2) AS Average_Resolution_Hours
FROM service_requests
WHERE resolution_hours IS NOT NULL;""")
        st.metric("Average Resolution Hours", f"{average:.2f} hrs")
        st.dataframe(result, use_container_width=True)

if selected_page == "Main Dashboard":
    main_dashboard()
else:
    query_page(selected_page)
