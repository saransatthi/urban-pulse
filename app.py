import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(
    page_title="Urban Pulse",
    page_icon="🏙️",
    layout="wide"
)

st.subheader("MySQL Database Connection")

mysql_password = st.text_input(
    "Enter MySQL Password",
    type="password"
)

if st.button("Connect to MySQL"):
    if mysql_password:
        try:
            st.session_state.mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password=mysql_password,
                port=3307,
                database="urban_pulse_db"
            )

            if st.session_state.mydb.is_connected():
                st.success("MySQL Connected Successfully!")

        except Exception as e:
            st.error(f"Connection Failed: {e}")
    else:
        st.warning("Please enter MySQL password")
st.title("🏙️ Urban Pulse")
if "mydb" in st.session_state and st.session_state.mydb.is_connected():

    query = """
    SELECT COUNT(*) AS total_requests
    FROM service_requests
    """

    df_kpi = pd.read_sql(query, st.session_state["mydb"])

    st.metric(
        label="Total Requests",
        value=f"{df_kpi['total_requests'][0]:,}"
    )
query = """
    SELECT
        ROUND(
            SUM(CASE WHEN Status = 'Closed' THEN 1 ELSE 0 END)
            * 100.0 / COUNT(*), 2
        ) AS closure_percentage
    FROM service_requests
    """
df_closure = pd.read_sql(query, st.session_state.mydb)
st.metric(
        label="Recorded Closure %",
        value=f"{df_closure['closure_percentage'][0]}%"
    )
query = """
SELECT COUNT(*) AS open_requests
FROM service_requests
WHERE Status = 'Open'
"""

df_open = pd.read_sql(query, st.session_state["mydb"])

st.metric(
    label="Open Requests",
    value=f"{df_open['open_requests'][0]:,}"
)
query = """
SELECT
    ROUND(
        AVG(median_value), 2
    ) AS median_resolution_hours
FROM (
    SELECT
        resolution_hours AS median_value,
        ROW_NUMBER() OVER (
            ORDER BY resolution_hours
        ) AS row_num,
        COUNT(*) OVER () AS total_rows
    FROM service_requests
    WHERE resolution_hours >= 0
) AS ranked_data
WHERE row_num IN (
    FLOOR((total_rows + 1) / 2),
    FLOOR((total_rows + 2) / 2)
)
"""

df_median = pd.read_sql(query, st.session_state["mydb"])

st.metric(
    label="Median Resolution Hours",
    value=f"{df_median['median_resolution_hours'][0]} hrs"
)
query = """
SELECT
    ROUND(
        SUM(CASE WHEN resolution_hours > 72 THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*), 2
    ) AS over_72_percentage
FROM service_requests
WHERE resolution_hours >= 0
"""

df_over72 = pd.read_sql(query, st.session_state.mydb)

st.metric(
    label="Over 72 Hours %",
    value=f"{df_over72['over_72_percentage'][0]}%"
)
st.subheader("Complaint Type Analysis")

query = """
SELECT
    complaint_type,
    COUNT(*) AS complaint_count
FROM service_requests
GROUP BY complaint_type
ORDER BY complaint_count DESC
LIMIT 10
"""

df_complaints = pd.read_sql(query, st.session_state["mydb"])

st.bar_chart(
    df_complaints.set_index("complaint_type")
)
st.subheader("Agency Workload Analysis")

query = """
SELECT
    agency,
    COUNT(*) AS complaint_count
FROM service_requests
GROUP BY agency
ORDER BY complaint_count DESC
"""

df_agency = pd.read_sql(query, st.session_state["mydb"])

st.bar_chart(
    df_agency.set_index("agency")
)
st.subheader("Borough-wise Requests Analysis")

query = """
SELECT
    borough,
    COUNT(*) AS complaint_count
FROM service_requests
GROUP BY borough
ORDER BY complaint_count DESC
"""

df_borough = pd.read_sql(query, st.session_state["mydb"])

st.bar_chart(
    df_borough.set_index("borough")
)

st.subheader("Monthly Complaint Trend")

query = """
SELECT
    DATE_FORMAT(created_date, '%Y-%m') AS complaint_month,
    COUNT(*) AS complaint_count
FROM service_requests
WHERE created_date IS NOT NULL
GROUP BY DATE_FORMAT(created_date, '%Y-%m')
ORDER BY complaint_month
"""

df_monthly = pd.read_sql(query, st.session_state["mydb"])

st.line_chart(
    df_monthly.set_index("complaint_month")
)
st.subheader("Weekday & Hour Analysis")

query = """
SELECT
    weekday,
    hour,
    COUNT(*) AS complaint_count
FROM service_requests
GROUP BY weekday, hour
ORDER BY weekday, hour
"""

df_time = pd.read_sql(query, st.session_state["mydb"])

st.dataframe(df_time, use_container_width=True)
st.subheader("Resolution Analysis")

query = """
SELECT
    ROUND(AVG(resolution_hours), 2) AS average_hours,
    MIN(resolution_hours) AS minimum_hours,
    MAX(resolution_hours) AS maximum_hours
FROM service_requests
WHERE resolution_hours >= 0
"""

df_resolution = pd.read_sql(query, st.session_state["mydb"])

st.dataframe(df_resolution, use_container_width=True)
st.subheader("Interactive Filters")

filter_query = """
SELECT DISTINCT borough
FROM service_requests
WHERE borough IS NOT NULL
ORDER BY borough
"""

df_filter = pd.read_sql(filter_query, st.session_state["mydb"])

selected_borough = st.selectbox(
    "Select Borough",
    ["All"] + df_filter["borough"].tolist()
)

st.write("Selected Borough:", selected_borough)
filter_query = """
SELECT DISTINCT complaint_type
FROM service_requests
WHERE complaint_type IS NOT NULL
ORDER BY complaint_type
"""

df_type_filter = pd.read_sql(filter_query, st.session_state["mydb"])

selected_complaint = st.selectbox(
    "Select Complaint Type",
    ["All"] + df_type_filter["complaint_type"].tolist()
)
filter_query = """
SELECT DISTINCT Status
FROM service_requests
WHERE Status IS NOT NULL
ORDER BY Status
"""

df_status_filter = pd.read_sql(filter_query, st.session_state["mydb"])

selected_status = st.selectbox(
    "Select Status",
    ["All"] + df_status_filter["Status"].tolist()
)
st.subheader("Filtered Complaint Records")

data_query = "SELECT * FROM service_requests WHERE 1=1"

if selected_borough != "All":
    data_query += f" AND borough = '{selected_borough}'"

if selected_complaint != "All":
    data_query += f" AND complaint_type = '{selected_complaint}'"

if selected_status != "All":
    data_query += f" AND status = '{selected_status}'"

df_filtered = pd.read_sql(data_query, st.session_state["mydb"])
st.subheader("Geographic Complaint Concentration")

df_map = df_filtered[["latitude", "longitude"]].copy()

df_map["latitude"] = pd.to_numeric(
    df_map["latitude"], errors="coerce"
)

df_map["longitude"] = pd.to_numeric(
    df_map["longitude"], errors="coerce"
)

df_map = df_map.dropna(
    subset=["latitude", "longitude"]
)

st.map(
    df_map,
    latitude="latitude",
    longitude="longitude"
)

st.write("Total Filtered Records:", len(df_filtered))

st.dataframe(df_filtered, use_container_width=True)


