"""
Deterministic Financial Calculation & Rule Engine
Guarantees 100% mathematical precision for EMI, DTI, and banking threshold checks.
Zero LLM arithmetic is permitted in this module.
"""
import math
from typing import List, Tuple
from app.schemas.loan import (
    ApplicantFinancials,
    LoanRequestDetails,
    DeterministicMetrics,
    DecisionStatus
)

# Standard Banking Credit Risk Thresholds
MAX_PERMISSIBLE_DTI = 0.43            # Max 43% Debt-to-Income standard
PRIME_CREDIT_SCORE = 720
MINIMUM_ELIGIBLE_SCORE = 620
MINIMUM_TENURE_MONTHS = 6

def calculate_monthly_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """
    Standard Equated Monthly Installment (EMI) amortized formula:
    EMI = [P x R x (1+R)^N] / [(1+R)^N - 1]
    Where P = Principal, R = Monthly interest rate, N = Months.
    """
    if principal <= 0 or tenure_months <= 0:
        return 0.0

    monthly_rate = annual_rate / 12.0
    
    if monthly_rate == 0:
        return round(principal / tenure_months, 2)

    compounded = math.pow(1 + monthly_rate, tenure_months)
    emi = (principal * monthly_rate * compounded) / (compounded - 1)
    return round(emi, 2)

def evaluate_deterministic_rules(
    financials: ApplicantFinancials,
    loan: LoanRequestDetails
) -> Tuple[DeterministicMetrics, DecisionStatus, List[str]]:
    """
    Runs deterministic verification rules against applicant financials.
    Returns metrics, provisional decision status, and deterministic rationale items.
    """
    monthly_emi = calculate_monthly_emi(loan.requested_amount, loan.annual_interest_rate, loan.tenure_months)
    total_repayment = round(monthly_emi * loan.tenure_months, 2)
    total_interest = round(total_repayment - loan.requested_amount, 2)

    total_monthly_obligations = financials.existing_monthly_debt + monthly_emi
    dti_ratio = round(total_monthly_obligations / financials.monthly_gross_income, 4)
    max_allowable_emi = round(financials.monthly_gross_income * MAX_PERMISSIBLE_DTI - financials.existing_monthly_debt, 2)

    dti_passed = dti_ratio <= MAX_PERMISSIBLE_DTI
    score_passed = financials.credit_score >= MINIMUM_ELIGIBLE_SCORE
    tenure_passed = financials.employment_tenure_months >= MINIMUM_TENURE_MONTHS

    reasons: List[str] = []

    # Rule checks
    if not score_passed:
        reasons.append(f"Credit score {financials.credit_score} is below minimum threshold of {MINIMUM_ELIGIBLE_SCORE}.")
    elif financials.credit_score >= PRIME_CREDIT_SCORE:
        reasons.append(f"Credit score {financials.credit_score} qualifies for Prime Tier underwriting.")

    if not dti_passed:
        reasons.append(
            f"Calculated Debt-to-Income (DTI) of {dti_ratio*100:.1f}% exceeds maximum regulatory ceiling of {MAX_PERMISSIBLE_DTI*100:.1f}%."
        )
    else:
        reasons.append(f"DTI ratio of {dti_ratio*100:.1f}% is healthy (within {MAX_PERMISSIBLE_DTI*100:.1f}% threshold).")

    if not tenure_passed:
        reasons.append(f"Employment tenure of {financials.employment_tenure_months} months is below required {MINIMUM_TENURE_MONTHS} months minimum.")

    # Determine status
    if not score_passed or not dti_passed:
        decision = DecisionStatus.REJECTED
    elif not tenure_passed:
        decision = DecisionStatus.MANUAL_REVIEW_REQUIRED
    elif dti_ratio > 0.38:
        decision = DecisionStatus.CONDITIONALLY_APPROVED
        reasons.append("Conditional approval subject to verification of secondary liquid collateral.")
    else:
        decision = DecisionStatus.APPROVED

    metrics = DeterministicMetrics(
        calculated_monthly_emi=monthly_emi,
        debt_to_income_ratio=dti_ratio,
        total_repayment_amount=total_repayment,
        total_interest_payable=total_interest,
        max_allowable_emi=max(0.0, max_allowable_emi),
        dti_threshold_passed=dti_passed,
        credit_score_threshold_passed=score_passed,
        employment_stability_passed=tenure_passed
    )

    return metrics, decision, reasons
