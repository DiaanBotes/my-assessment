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

    qry = """____________________"""

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

    qry = """____________________"""

    return qry


def question_5():
    """
    Make use of conditional aggregation to pivot the `timeline` table such that the columns are as follows:
    `CustomerID`, `JanuaryRepayments`, `JanuaryTotal`,...,`DecemberRepayments`, `DecemberTotal`,...etc
    MonthRepayments columns (e.g JanuaryRepayments) should be integers

    Hint: there should be 1x CustomerID = 1
    """

    qry = """____________________"""

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

    qry = """____________________"""

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

    qry = """____________________"""

    return qry
