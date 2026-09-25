import os

import numpy as np
import pandas as pd

"""
To answer the following questions, make use of datasets: 
    'scheduled_loan_repayments.csv'
    'actual_loan_repayments.csv'
These files are located in the 'data' folder. 

'scheduled_loan_repayments.csv' contains the expected monthly payments for each loan. These values are constant regardless of what is actually paid.
'actual_loan_repayments.csv' contains the actual amount paid to each loan for each month.

All loans have a loan term of 2 years with an annual interest rate of 10%. Repayments are scheduled monthly.
A type 1 default occurs on a loan when any scheduled monthly repayment is not met in full.
A type 2 default occurs on a loan when more than 15% of the expected total payments are unpaid for the year.

Note: Do not round any final answers.

"""


def calculate_df_balances(df_scheduled, df_actual):
    """
    This is a utility function that creates a merged dataframe that will be used in the following questions.
    This function will not be graded, do not make changes to it.

    Args:
        df_scheduled (DataFrame): Dataframe created from the 'scheduled_loan_repayments.csv' dataset
        df_actual (DataFrame): Dataframe created from the 'actual_loan_repayments.csv' dataset

    Returns:
        DataFrame: A merged Dataframe with additional calculated columns to help with the following questions.

    """

    df_merged = pd.merge(df_actual, df_scheduled)

    def calculate_balance(group):
        r_monthly = 0.1 / 12
        group = group.sort_values("Month")
        balances = []
        interest_payments = []
        loan_start_balances = []
        for index, row in group.iterrows():
            if balances:
                interest_payment = balances[-1] * r_monthly
                balance_with_interest = balances[-1] + interest_payment
            else:
                interest_payment = row["LoanAmount"] * r_monthly
                balance_with_interest = row["LoanAmount"] + interest_payment
                loan_start_balances.append(row["LoanAmount"])

            new_balance = balance_with_interest - row["ActualRepayment"]
            interest_payments.append(interest_payment)

            new_balance = max(0, new_balance)
            balances.append(new_balance)

        loan_start_balances.extend(balances)
        loan_start_balances.pop()
        group["LoanBalanceStart"] = loan_start_balances
        group["LoanBalanceEnd"] = balances
        group["InterestPayment"] = interest_payments
        return group

    df_balances = (
        df_merged.groupby("LoanID", as_index=False)
        .apply(calculate_balance)
        .reset_index(drop=True)
    )

    df_balances["LoanBalanceEnd"] = df_balances["LoanBalanceEnd"].round(2)
    df_balances["InterestPayment"] = df_balances["InterestPayment"].round(2)
    df_balances["LoanBalanceStart"] = df_balances["LoanBalanceStart"].round(2)

    return df_balances


# Do not edit these directories
root = os.getcwd()

if "Task_2" in root:
    df_scheduled = pd.read_csv("data/scheduled_loan_repayments.csv")
    df_actual = pd.read_csv("data/actual_loan_repayments.csv")
else:
    df_scheduled = pd.read_csv("Task_2/data/scheduled_loan_repayments.csv")
    df_actual = pd.read_csv("Task_2/data/actual_loan_repayments.csv")

df_balances = calculate_df_balances(df_scheduled, df_actual)


def question_1(df_balances):
    """
    Calculate the percent of loans that defaulted as per the type 1 default definition.

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The percentage of type 1 defaulted loans (ie 50.0 not 0.5)

    """

    # Flag each month where the actual repayment was less than the scheduled repayment
    # A single month is enough to collapse to the default, therefore .any() is used to check
    # The mean gives the proportion of loans that defaulted

    short_fall_months = df_balances["ActualRepayment"] < df_balances["ScheduledRepayment"]
    default_rate_percent = float(short_fall_months.groupby(df_balances["LoanID"]).any().mean() * 100)

    return default_rate_percent


def question_2(df_scheduled, df_balances):
    """
    Calculate the percent of loans that defaulted as per the type 2 default definition

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function
        df_scheduled (DataFrame): Dataframe created from the 'scheduled_loan_repayments.csv' dataset

    Returns:
        float: The percentage of type 2 defaulted loans (ie 50.0 not 0.5)

    """

    # ScheduledRepayment is constant, so the expected total is the monthly instalment * by 12
    # LoanID is set as the index such that this Series aligns with the grouped actuals by loan
    expected_total_payments = df_scheduled.set_index("LoanID")["ScheduledRepayment"] * 12
    actual_total_payments = df_balances.groupby("LoanID")["ActualRepayment"].sum()

    unpaid_amount = expected_total_payments - actual_total_payments
    unpaid_proportion = unpaid_amount / expected_total_payments

    default_rate_percent = float((unpaid_proportion > 0.15).mean() * 100)

    return default_rate_percent


def question_3(df_balances):
    """
    Calculate the anualized portfolio CPR (As a %) from the geometric mean SMM.
    SMM is calculated as: (Unscheduled Principal)/(Start of Month Loan Balance)
    SMM_mean is calculated as (∏(1+SMM))^(1/12) - 1
    CPR is calcualted as: 1 - (1- SMM_mean)^12

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The anualized CPR of the loan portfolio as a percent.

    """
    # Unscheduled principal is any amount paid above the scheduled instalment, which reduces the loan balance faster than the repayment schedule requires.
    # Shortfalls are clipped to zero, since those aren't prepayments.
    unscheduled_principal = (df_balances["ActualRepayment"] - df_balances["ScheduledRepayment"]).clip(lower=0)

    # SMM is calculated at portfolio level rather than per loan. The monthly
    # totals are summed before dividing, such that each loan is weighted by its size
    monthly_unscheduled = unscheduled_principal.groupby(df_balances["Month"]).sum()
    monthly_start_balance = df_balances.groupby("Month")["LoanBalanceStart"].sum()
    monthly_smm = monthly_unscheduled / monthly_start_balance

    smm_mean = (1 + monthly_smm).prod() ** (1 / 12) - 1

    cpr_percent = float((1 - (1 - smm_mean) ** 12) * 100)

    return cpr_percent


def question_4(df_balances):
    """
    Calculate the predicted total loss for the second year in the loan term.
    Use the equation: probability_of_default * total_loan_balance * (1 - recovery_rate).
    The probability_of_default value must be taken from either your question_1 or question_2 answer.
    Decide between the two answers based on which default definition you believe to be the more useful metric.
    Assume a recovery rate of 80%

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The predicted total loss for the second year in the loan term.

    """

    final_month = df_balances[df_balances["Month"] == 12]
    total_loan_balance = final_month["LoanBalanceEnd"].sum()

    # Type 2 is used as the probability of default. Type 1 triggers on a single missed payment
    # So it overstates the loans likely to create an actual loss.
    # question_2 is called, it needs df_scheduled, which is loaded at module level.
    # Divided by 100 to convert a percentage to a probability.
    probability_of_default = question_2(df_scheduled, df_balances) / 100

    recovery_rate = 0.8

    total_loss = float(probability_of_default * total_loan_balance * (1 - recovery_rate))

    return total_loss
