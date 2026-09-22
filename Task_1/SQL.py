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
Each question in this section is isolated, for example, you do not need to consider how Q5 may affect Q4.
Remember to clean your data.

"""


def question_1():
    """
    Find the name, surname and customer ids for all the duplicated customer ids in the customers dataset.
    Return the `Name`, `Surname` and `CustomerID`
    """

    qry = """

    -- Identifies customers whose CustomerID appears more than once. The subquery groups by CustomerID and only keeps IDs with more than one row
    -- DISTINCT is used to exclude duplicate rows and only return duplicated customers once. Results are then sorted by CustomerID
    
    SELECT DISTINCT Name, Surname, CustomerID
    FROM customers
    WHERE CustomerID IN (
        SELECT CustomerID
        FROM customers
        GROUP BY CustomerID
        HAVING COUNT(*) > 1
    )
    ORDER BY CustomerID
    """

    return qry


def question_2():
    """
    Return the `Name`, `Surname` and `Income` of all female customers in the dataset in descending order of income
    """

    qry = """
    
    -- Filtering to female customers. LOWER and LIKE 'fem%' gaurd against inconsistencies in the column
    -- Distinct removes duplicate customers 
    
    SELECT DISTINCT Name, Surname, Income
    FROM customers
    WHERE LOWER(Gender) LIKE 'fem%'
    ORDER BY Income DESC
    """

    return qry


def question_3():
    """
    Calculate the percentage of approved loans by LoanTerm, with the result displayed as a percentage out of 100.
    ie 50 not 0.5
    There is only 1 loan per customer ID.
    """

    qry = """

    -- There are 14 duplicate records, since there are one loan per customer duplicates are removed before calculating so no loan is counted twice
    -- The CASE WHEN counts approved loans which is then divided by the total number of loans

    SELECT 
        LoanTerm,  
        (SUM(CASE WHEN ApprovalStatus = 'Approved' THEN 1 ELSE 0 END) / COUNT(*)) * 100 AS Percentage
    FROM (
        SELECT DISTINCT *
        FROM loans
    ) AS unique_loans
    GROUP BY LoanTerm 
    ORDER BY LoanTerm
    
    """

    return qry


def question_4():
    """
    Return a breakdown of the number of customers per CustomerClass in the credit data
    Return columns `CustomerClass` and `Count`
    """

    qry = """

    -- Count the customers per CustomerClass, the duplicates are removed in the subclass, same as in the previous question. 

    SELECT CustomerClass, COUNT(*) AS Count
    FROM (
        SELECT DISTINCT *
        FROM credit
    ) AS unique_Customers
    GROUP BY CustomerClass
    ORDER BY CustomerClass    

    """

    return qry


def question_5():
    """
    Make use of the UPDATE function to amend/fix the following: Customers with a CreditScore between and including 600 to 650 must be classified as CustomerClass C.
    """

    qry = """____________________"""

    return qry
