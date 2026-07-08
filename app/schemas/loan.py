from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class EmploymentType(str, Enum):
    SALARIED = "SALARIED"
    SELF_EMPLOYED = "SELF_EMPLOYED"
    CONTRACTOR = "CONTRACTOR"

class LoanPurpose(str, Enum):
    HOME_PURCHASE = "HOME_PURCHASE"
    DEBT_CONSOLIDATION = "DEBT_CONSOLIDATION"
    EDUCATION = "EDUCATION"
    PERSONAL = "PERSONAL"

class DecisionStatus(str, Enum):
    APPROVED = "APPROVED"
    CONDITIONALLY_APPROVED = "CONDITIONALLY_APPROVED"
    REJECTED = "REJECTED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"

class ApplicantFinancials(BaseModel):
    monthly_gross_income: float = Field(..., gt=0, description="Monthly gross income in USD/EUR")
    existing_monthly_debt: float = Field(default=0.0, ge=0, description="Existing recurring debt payments (loans, credit cards)")
    credit_score: int = Field(..., ge=300, le=850, description="FICO or equivalent credit score (300-850)")
    employment_type: EmploymentType = Field(default=EmploymentType.SALARIED)
    employment_tenure_months: int = Field(..., ge=0, description="Months at current employer/business")

class LoanRequestDetails(BaseModel):
    requested_amount: float = Field(..., gt=0, description="Total principal requested")
    tenure_months: int = Field(..., gt=0, le=360, description="Repayment period in months")
    annual_interest_rate: float = Field(..., ge=0.01, le=0.50, description="Annual nominal interest rate as decimal (e.g. 0.075 for 7.5%)")
    loan_purpose: LoanPurpose = Field(default=LoanPurpose.PERSONAL)

class QualitativeDocument(BaseModel):
    doc_id: str
    doc_type: str = Field(description="bank_statement, employer_letter, tax_return")
    text_content: str

class LoanEvaluationRequest(BaseModel):
    application_id: str
    financials: ApplicantFinancials
    loan: LoanRequestDetails
    qualitative_notes: Optional[str] = Field(default="", description="Additional officer notes or applicant statements")
    supporting_documents: Optional[List[QualitativeDocument]] = Field(default_factory=list)

class DeterministicMetrics(BaseModel):
    calculated_monthly_emi: float
    debt_to_income_ratio: float
    total_repayment_amount: float
    total_interest_payable: float
    max_allowable_emi: float
    dti_threshold_passed: bool
    credit_score_threshold_passed: bool
    employment_stability_passed: bool

class CreditDecisionResponse(BaseModel):
    application_id: str
    decision: DecisionStatus
    deterministic_metrics: DeterministicMetrics
    rule_engine_reasons: List[str]
    qualitative_synthesis: str
    audit_hash: str
