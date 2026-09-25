"""
The database loan.db consists of 5 tables:
   1. customers - table containing customer data
   2. loans - table containing loan data pertaining to customers
   3. credit - table containing credit and creditscore data pertaining to customers
   4. repayments - table containing loan repayment data pertaining to customers
   5. months - table containing month name and month ID data

You are required to make use of your knowledge in SQL to query the database object (saved as loan.db) and return the requested information.
Simply fill in the vacant space wrapped in triple quotes per question (each function represents a question)

NOTE:
The database will be reset when grading each section. Any changes made to the database in the previous `SQL` section can be ignored.
Each question in this section is isolated unless it is stated that questions are linked.
Remember to clean your data

"""


def question_1():
    """
    Make use of a JOIN to find the `AverageIncome` per `CustomerClass`
    """

    qry = """

    -- Calculates avg income per CustomerClass, both of the tables have 14 exact duplicates and joining them would double that
    -- Therefore a CTE (common table expression) is used to remove the duplicates in each table before the join

    WITH unique_customers AS (
        SELECT DISTINCT * FROM customers
    ),
    unique_credit AS (
        SELECT DISTINCT * FROM credit
    )

    SELECT AVG(c.Income) AS AverageIncome, cr.CustomerClass
    FROM unique_customers AS c
    JOIN unique_credit AS cr ON c.CustomerID = cr.CustomerID
    GROUP BY cr.CustomerClass
    ORDER BY cr.CustomerClass
    
    """

    return qry


def question_2():
    """
    Make use of a JOIN to return a breakdown of the number of 'RejectedApplications' per 'Province'.
    Ensure consistent use of either the abbreviated or full version of each province, matching the format found in the customer table.
    """

    qry = """

    -- Counting rejected loan applications per province
    -- There are two formats inside of the Region column, abbreviations and full names.
    --  Abbreviations are more dominant, therefore full names are mapped to abbreviations through CASE WHEN
    -- All duplications are removed first in CTE'S 

    WITH unique_customers AS (
        SELECT DISTINCT * FROM customers
    ),
    unique_loans AS (
        SELECT DISTINCT * FROM loans
    )

    SELECT CASE
            WHEN Region = 'EasternCape' THEN 'EC'
            WHEN Region = 'FreeState' THEN 'FS'
            WHEN Region = 'WesternCape' THEN 'WC'
            WHEN Region = 'KwaZulu-Natal' THEN 'KZN'
            WHEN Region = 'NorthWest' THEN 'NW'
            WHEN Region = 'Gauteng' THEN 'GT'
            WHEN Region = 'NorthernCape' THEN 'NC'
            WHEN Region = 'Mpumalanga' THEN 'MP'
            WHEN Region = 'Limpopo' THEN 'LP'
            ELSE Region 
        END AS Province,
        COUNT (*) AS RejectedApplications
    FROM unique_customers AS c
    JOIN unique_loans AS l ON c.CustomerID = l.CustomerID
    WHERE l.ApprovalStatus = 'Rejected'
    GROUP BY Province
    ORDER BY Province

    """

    return qry


def question_3():
    """
    Making use of the `INSERT` function, create a new table called `financing` which will include the following columns:
    `CustomerID`,`Income`,`LoanAmount`,`LoanTerm`,`InterestRate`,`ApprovalStatus` and `CreditScore`

    Do not return the new table, just create it.
    """

    qry = """

    -- Chose these data types since they match the columns in tables customers, loans and credit
    -- Removing all of the duplicate rows with 3 CTE's after the Insert but before Select
    -- Uses 2 joins to join all 3 tables on CustomerID together

    CREATE TABLE financing (
        CustomerID INT,
        Income INT,
        LoanAmount INT,
        LoanTerm INT,
        InterestRate FLOAT,
        ApprovalStatus VARCHAR,
        CreditScore INT
    );

    INSERT INTO financing
        (CustomerID, Income, LoanAmount, LoanTerm, InterestRate, ApprovalStatus, CreditScore)

    WITH unique_customers AS (
        SELECT DISTINCT * FROM customers
    ),
    unique_loans AS (
        SELECT DISTINCT * FROM loans
    ),
    unique_credit AS (
        SELECT DISTINCT * FROM credit
    )

    SELECT
        c.CustomerID, c.Income, l.LoanAmount, l.LoanTerm, l.InterestRate, l.ApprovalStatus, cr.CreditScore
    FROM unique_customers AS c
    JOIN unique_loans AS l ON c.CustomerID = l.CustomerID
    JOIN unique_credit AS cr ON c.CustomerID = cr.CustomerID

    """

    return qry


# Question 4 and 5 are linked


def question_4():
    """
    Using a `CROSS JOIN` and the `months` table, create a new table called `timeline` that sumarises Repayments per customer per month.
    Columns should be: `CustomerID`, `MonthName`, `NumberOfRepayments`, `AmountTotal`.
    Repayments should only occur between 6am and 6pm London Time.
    Null values to be filled with 0.

    Hint: there should be 12x CustomerID = 1.
    """

    qry = """

    -- Regards to Timezone handling. RepaymentDate is stored without a timezone, with the local
    -- zone located in the TimeZone column. Each timestamp is therefore
    -- interpreted in its own zone and converted to Europe/London before filtering.
    -- IANA zone names are used such that daylight saving is applied correctly
    -- The ICU extension is installed and loaded, it is required for named zones.
    --
    -- Assumptions: CST, IST and PNT are a bit ambiguous. They are read as
    -- US Central, Israel Standard Time, and US Mountain
    -- The time window, 06:00-18:00 is treated as inclusive of both.
    --
    -- Structure: repayments are aggregated per customer per month, then attached to
    -- a grid of every customer and every month through a LEFT JOIN
    -- Such that months with no repayments are showed and filled with 0 by COALESCE. 
    -- Finally This produces 1000 customers x 12 months = 12,000 rows.

    INSTALL icu; LOAD icu;

    CREATE TABLE timeline (
        CustomerID INT,
        MonthName VARCHAR,
        NumberOfRepayments INT,
        AmountTotal INT
    );

    INSERT INTO timeline
        (CustomerID, MonthName, NumberOfRepayments, AmountTotal)

    WITH TimeZoneConversions AS (
        SELECT
            CustomerID,
            Amount,
            RepaymentDate
                AT TIME ZONE CASE TimeZone
                    WHEN 'GMT' THEN 'Europe/London'
                    WHEN 'UTC' THEN 'UTC'
                    WHEN 'CET' THEN 'Europe/Paris'
                    WHEN 'EET' THEN 'Europe/Athens'
                    WHEN 'JST' THEN 'Asia/Tokyo'
                    WHEN 'PST' THEN 'America/Los_Angeles'
                    WHEN 'CST' THEN 'America/Chicago'
                    WHEN 'IST' THEN 'Asia/Jerusalem'
                    WHEN 'PNT' THEN 'America/Phoenix'
                    ELSE TimeZone
                    END
                AT TIME ZONE 'Europe/London' AS LondonTime
        FROM repayments
    ),
    monthly_totals AS (
        SELECT CustomerID, Month(LondonTime) AS MonthID, COUNT(*) AS NumberOfRepayments, SUM(Amount) AS AmountTotal
        FROM TimeZoneConversions
        WHERE LondonTime::TIME >= '06:00' AND LondonTime::TIME <= '18:00'
        GROUP BY CustomerID, MonthID
    ),
    customers_months AS (
        SELECT c.CustomerID, m.MonthID, m.MonthName
        FROM (
            SELECT DISTINCT *
            FROM customers
        )  AS c
        CROSS JOIN months AS m
    )
    
    SELECT cm.CustomerID, cm.MonthName, COALESCE(mt.NumberOfRepayments, 0) AS NumberOfRepayments, COALESCE(mt.AmountTotal, 0) AS AmountTotal
    FROM customers_months AS cm
    LEFT JOIN monthly_totals AS mt
        ON cm.CustomerID = mt.CustomerID
        AND cm.MonthID = mt.MonthID
    ORDER BY cm.CustomerID, cm.MonthID

    """

    return qry


def question_5():
    """
    Make use of conditional aggregation to pivot the `timeline` table such that the columns are as follows:
    `CustomerID`, `JanuaryRepayments`, `JanuaryTotal`,...,`DecemberRepayments`, `DecemberTotal`,...etc
    MonthRepayments columns (e.g JanuaryRepayments) should be integers

    Hint: there should be 1x CustomerID = 1
    """

    qry = """

    -- For each month, SUM is applied to a CASE expression that returns the value only for that month and 0 for all others
    -- The repayment count columns are cast to INT

    SELECT 
        CustomerID,
        SUM(CASE WHEN MonthName = 'January' THEN NumberOfRepayments ELSE 0 END)::INT AS JanuaryRepayments,
        SUM(CASE WHEN MonthName = 'January' THEN AmountTotal ELSE 0 END)::INT AS JanuaryTotal,
        SUM(CASE WHEN MonthName = 'February' THEN NumberOfRepayments ELSE 0 END)::INT AS FebruaryRepayments,
        SUM(CASE WHEN MonthName = 'February' THEN AmountTotal ELSE 0 END)::INT AS FebruaryTotal,
        SUM(CASE WHEN MonthName = 'March' THEN NumberOfRepayments ELSE 0 END)::INT AS MarchRepayments,
        SUM(CASE WHEN MonthName = 'March' THEN AmountTotal ELSE 0 END)::INT AS MarchTotal,
        SUM(CASE WHEN MonthName = 'April' THEN NumberOfRepayments ELSE 0 END)::INT AS AprilRepayments,
        SUM(CASE WHEN MonthName = 'April' THEN AmountTotal ELSE 0 END)::INT AS AprilTotal,
        SUM(CASE WHEN MonthName = 'May' THEN NumberOfRepayments ELSE 0 END)::INT AS MayRepayments,
        SUM(CASE WHEN MonthName = 'May' THEN AmountTotal ELSE 0 END)::INT AS MayTotal,
        SUM(CASE WHEN MonthName = 'June' THEN NumberOfRepayments ELSE 0 END)::INT AS JuneRepayments,
        SUM(CASE WHEN MonthName = 'June' THEN AmountTotal ELSE 0 END)::INT AS JuneTotal,
        SUM(CASE WHEN MonthName = 'July' THEN NumberOfRepayments ELSE 0 END)::INT AS JulyRepayments,
        SUM(CASE WHEN MonthName = 'July' THEN AmountTotal ELSE 0 END)::INT AS JulyTotal,
        SUM(CASE WHEN MonthName = 'August' THEN NumberOfRepayments ELSE 0 END)::INT AS AugustRepayments,
        SUM(CASE WHEN MonthName = 'August' THEN AmountTotal ELSE 0 END)::INT AS AugustTotal,
        SUM(CASE WHEN MonthName = 'September' THEN NumberOfRepayments ELSE 0 END)::INT AS SeptemberRepayments,
        SUM(CASE WHEN MonthName = 'September' THEN AmountTotal ELSE 0 END)::INT AS SeptemberTotal,
        SUM(CASE WHEN MonthName = 'October' THEN NumberOfRepayments ELSE 0 END)::INT AS OctoberRepayments,
        SUM(CASE WHEN MonthName = 'October' THEN AmountTotal ELSE 0 END)::INT AS OctoberTotal,
        SUM(CASE WHEN MonthName = 'November' THEN NumberOfRepayments ELSE 0 END)::INT AS NovemberRepayments,
        SUM(CASE WHEN MonthName = 'November' THEN AmountTotal ELSE 0 END)::INT AS NovemberTotal,
        SUM(CASE WHEN MonthName = 'December' THEN NumberOfRepayments ELSE 0 END)::INT AS DecemberRepayments,
        SUM(CASE WHEN MonthName = 'December' THEN AmountTotal ELSE 0 END)::INT AS DecemberTotal
    FROM timeline
    GROUP BY CustomerID
    ORDER BY CustomerID

    """

    return qry


# QUESTION 6 and 7 are linked, Do not be concerned with timezones or repayment times for these question.


def question_6():
    """
    The `customers` table was created by merging two separate tables: one containing data for male customers and the other for female customers.
    Due to an error, the data in the age columns were misaligned in both original tables, resulting in a shift of two places upwards in
    relation to the corresponding CustomerID.

    Create a table called `corrected_customers` with columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`
    Utilize a window function to correct this mistake in the new `CorrectedAge` column.
    Null values can be input manually - i.e. values that overflow should loop to the top of each gender.

    Also return a result set for this table (ie SELECT * FROM corrected_customers)
    """

    qry = """

    -- With the misalignment, ages were shifted two places upwards within each table
    -- LEAD(Age, 2) recovers it, partitioned by Gender since the male and female tables were shifted independently.
    --
    -- The last two customers per gender have no rows below them, so their values
    -- are just added manually, wrapping to the first two ages of the same gender
    -- (male 994 and 1000 from customers 7 and 8, female 998 and 999 from 1 and 2).
    --
    -- With Customers, the duplicates are removed first

    CREATE TABLE corrected_customers AS
    SELECT
        CustomerID,
        Age,
        COALESCE(
            LEAD(Age, 2) OVER (PARTITION BY Gender ORDER BY CustomerID),
            CASE CustomerID
                WHEN 994 THEN 21
                WHEN 1000 THEN 64
                WHEN 998 THEN 24
                WHEN 999 THEN 34
            END
        ) AS CorrectedAge,
        Gender
    FROM (
        SELECT DISTINCT * FROM customers
    )
    ORDER BY CustomerID;

    SELECT * FROM corrected_customers;
    
    """

    return qry


def question_7():
    """
    Create a column in corrected_customers called 'AgeCategory' that categorizes customers by age.
    Age categories should be as follows:
        - `Teen`: CorrectedAge < 20
        - `Young Adult`: 20 <= CorrectedAge < 30
        - `Adult`: 30 <= CorrectedAge < 60
        - `Pensioner`: CorrectedAge >= 60

    Make use of a windows function to assign a rank to each customer based on the total number of repayments per age group. Add this into a "Rank" column.
    The ranking should not skip numbers in the sequence, even when there are ties, i.e. 1,2,2,2,3,4 not 1,2,2,2,5,6
    Customers with no repayments should be included as 0 in the result.

    Return columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`, `AgeCategory`, `Rank`
    """

    qry = """

    -- Two CTEs are needed because AgeCategory must exist as a column before it can
    -- be used as the partition key of the window function.
    --
    -- The LEFT JOIN with COALESCE keeps customers who made no repayments, counting
    -- them as 0 so they are ranked last rather than dropped.
    --
    -- DENSE_RANK is used rather than RANK so that tied customers do not create gaps
    -- in the sequence (1,2,2,3 not 1,2,2,4). Ranking is descending, so the customer
    -- with the most repayments in each age group is ranked 1.

    CREATE OR REPLACE TABLE corrected_customers AS 
    WITH repayment_counts AS (
        SELECT CustomerID, COUNT(*) AS NumberOfRepayments
        FROM repayments
        GROUP BY CustomerID
    ),
    categorised AS (
        SELECT
            cc.CustomerID,
            cc.Age,
            cc.CorrectedAge,
            cc.Gender,
            COALESCE(rc.NumberOfRepayments, 0) AS NumberOfRepayments,
            CASE
                WHEN cc.CorrectedAge < 20 THEN 'Teen'
                WHEN cc.CorrectedAge < 30 THEN 'Young Adult'
                WHEN cc.CorrectedAge < 60 THEN 'Adult'
                ELSE 'Pensioner'
            END AS AgeCategory
        FROM corrected_customers AS cc
        LEFT JOIN repayment_counts AS rc
            ON cc.CustomerID = rc.CustomerID
    )
    SELECT
        CustomerID,
        Age,
        CorrectedAge,
        Gender,
        AgeCategory,
        DENSE_RANK() OVER (
            PARTITION BY AgeCategory
            ORDER BY NumberOfRepayments DESC
        ) AS Rank
    FROM categorised
    ORDER BY AgeCategory, Rank, CustomerID;

    SELECT * FROM corrected_customers;

    """

    return qry
