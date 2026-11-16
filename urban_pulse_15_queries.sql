
USE urban_pulse_db;

#Task 1: Total Requests
SELECT COUNT(DISTINCT unique_key) AS Total_Requests
FROM service_requests;

#Task 2: Top 10 Complaint Types
SELECT
    complaint_type,
    COUNT(*) AS Complaint_Count
FROM service_requests
GROUP BY complaint_type
ORDER BY Complaint_Count DESC
LIMIT 10;

# Task 3: Agency Workload Analysis
SELECT
    agency,
    COUNT(*) AS Complaint_Count
FROM service_requests
GROUP BY agency
ORDER BY Complaint_Count DESC;

# Task 4: Request Volume by Borough
SELECT
    borough,
    COUNT(*) AS Complaint_Count
FROM service_requests
GROUP BY borough
ORDER BY Complaint_Count DESC;

# Task 5: Complaint Status Analysis
SELECT
    status,
    COUNT(*) AS Complaint_Count
FROM service_requests
GROUP BY status
ORDER BY Complaint_Count DESC;

#  Task 6: Borough-wise Status Analysis
SELECT
    borough,
    status,
    COUNT(*) AS Complaint_Count
FROM service_requests
GROUP BY borough, status
ORDER BY borough, Complaint_Count DESC;

# Task 7: Average Resolution Time by Borough
SELECT
    borough,
    ROUND(AVG(resolution_hours), 2) AS Average_Resolution_Hours
FROM service_requests
WHERE resolution_hours IS NOT NULL
GROUP BY borough
ORDER BY Average_Resolution_Hours DESC;

#  Task 8: Minimum and Maximum Resolution Time
SELECT
    MIN(resolution_hours) AS Minimum_Resolution_Hours,
    MAX(resolution_hours) AS Maximum_Resolution_Hours
FROM service_requests
WHERE resolution_hours IS NOT NULL; 

#  Task 9: Monthly Complaint Trend
SELECT
    YEAR(created_date) AS Complaint_Year,
    MONTH(created_date) AS Complaint_Month,
    COUNT(*) AS Complaint_Count
FROM service_requests
WHERE created_date IS NOT NULL
GROUP BY
    YEAR(created_date),
    MONTH(created_date)
ORDER BY
    Complaint_Year,
    Complaint_Month;

# Task 10: Hour-wise Complaint Analysis
SELECT
    HOUR(created_date) AS Complaint_Hour,
    COUNT(*) AS Complaint_Count
FROM service_requests
WHERE created_date IS NOT NULL
GROUP BY HOUR(created_date)
ORDER BY Complaint_Hour;

# Task 11: Weekday-wise Complaint Analysis
SELECT
    DAYNAME(created_date) AS Complaint_Day,
    COUNT(*) AS Complaint_Count
FROM service_requests
WHERE created_date IS NOT NULL
GROUP BY DAYNAME(created_date)
ORDER BY Complaint_Count DESC;

#   Task 12: Open Complaints by Borough
SELECT
    borough,
    COUNT(*) AS Open_Complaint_Count
FROM service_requests
WHERE status = 'Open'
GROUP BY borough
ORDER BY Open_Complaint_Count DESC;

#  Task 13: Top 10 Agencies by Complaint Volume
SELECT
    agency,
    COUNT(*) AS Complaint_Count
FROM service_requests
GROUP BY agency
ORDER BY Complaint_Count DESC
LIMIT 10;

# Task 14: Complaints Taking More Than 72 Hours
SELECT
    COUNT(*) AS Complaints_Over_72_Hours
FROM service_requests
WHERE resolution_hours > 72;

# Task 15: Overall Average Resolution Time
SELECT
    ROUND(AVG(resolution_hours), 2) AS Average_Resolution_Hours
FROM service_requests
WHERE resolution_hours IS NOT NULL;