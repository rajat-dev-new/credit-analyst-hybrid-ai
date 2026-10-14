import pytest
from app.core.rules import calculate_monthly_emi, evaluate_deterministic_rules
from app.schemas.loan import (
    ApplicantFinancials,
    LoanRequestDetails,
    EmploymentType,
    LoanPurpose,
    DecisionStatus
)

def test_calculate_monthly_emi_standard():
    # $10,000 at 5% annual over 12 months
    # Formula check: Approx $856.07
    emi = calculate_monthly_emi(principal=10000.0, annual_rate=0.05, tenure_months=12)
    assert 855.0 < emi < 857.0

def test_calculate_monthly_emi_zero_rate():
    # $12,000 at 0% over 12 months = $1,000/mo
    emi = calculate_monthly_emi(principal=12000.0, annual_rate=0.0, tenure_months=12)
    assert emi == 1000.0

def test_evaluate_approved_application():
    financials = ApplicantFinancials(
        monthly_gross_income=8000.0,
        existing_monthly_debt=500.0,
        credit_score=780,
        employment_type=EmploymentType.SALARIED,
        employment_tenure_months=36
    )
    loan = LoanRequestDetails(
        requested_amount=20000.0,
        tenure_months=36,
        annual_interest_rate=0.06,
        loan_purpose=LoanPurpose.HOME_PURCHASE
    )

    metrics, decision, reasons = evaluate_deterministic_rules(financials, loan)

    assert decision == DecisionStatus.APPROVED
    assert metrics.dti_threshold_passed is True
    assert metrics.credit_score_threshold_passed is True
    assert metrics.debt_to_income_ratio < 0.43

def test_evaluate_rejected_high_dti():
    financials = ApplicantFinancials(
        monthly_gross_income=3000.0,
        existing_monthly_debt=1200.0,
        credit_score=700,
        employment_type=EmploymentType.SALARIED,
        employment_tenure_months=24
    )
    loan = LoanRequestDetails(
        requested_amount=30000.0,
        tenure_months=24,
        annual_interest_rate=0.08,
        loan_purpose=LoanPurpose.PERSONAL
    )

    metrics, decision, reasons = evaluate_deterministic_rules(financials, loan)

    assert decision == DecisionStatus.REJECTED
    assert metrics.dti_threshold_passed is False

def test_evaluate_rejected_low_credit_score():
    financials = ApplicantFinancials(
        monthly_gross_income=10000.0,
        existing_monthly_debt=200.0,
        credit_score=550, # Below 620 minimum
        employment_type=EmploymentType.SALARIED,
        employment_tenure_months=48
    )
    loan = LoanRequestDetails(
        requested_amount=5000.0,
        tenure_months=12,
        annual_interest_rate=0.05,
        loan_purpose=LoanPurpose.PERSONAL
    )

    metrics, decision, reasons = evaluate_deterministic_rules(financials, loan)

    assert decision == DecisionStatus.REJECTED
    assert metrics.credit_score_threshold_passed is False
