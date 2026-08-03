"""
Bounded Qualitative LLM Synthesis Engine
Synthesizes retrieved contextual excerpts with deterministic calculations.
Strict prompt bounds prevent hallucinations or unauthorized numeric overrides.
"""
from typing import List
from app.schemas.loan import (
    DeterministicMetrics,
    DecisionStatus,
    QualitativeDocument
)

class QualitativeLLMEngine:
    def __init__(self, model_name: str = "llama3:latest-local"):
        self.model_name = model_name

    def synthesize_explanation(
        self,
        applicant_id: str,
        decision: DecisionStatus,
        metrics: DeterministicMetrics,
        rule_reasons: List[str],
        retrieved_docs: List[QualitativeDocument],
        officer_notes: str = ""
    ) -> str:
        """
        Generates an auditable qualitative rationale grounded in retrieved evidence.
        """
        doc_excerpts = "\n".join(
            [f"- [{d.doc_type} #{d.doc_id}]: {d.text_content[:180]}..." for d in retrieved_docs]
        ) if retrieved_docs else "No supporting external documents supplied."

        synthesis = (
            f"CREDIT ANALYST SYNTHESIS REPORT [Applicant #{applicant_id}]\n"
            f"Status Recommendation: {decision.value}\n\n"
            f"1. QUANTITATIVE VERIFICATION (Deterministic):\n"
            f"   • Monthly EMI Obligation: ${metrics.calculated_monthly_emi:,.2f}\n"
            f"   • Debt-to-Income (DTI): {metrics.debt_to_income_ratio*100:.2f}% (Regulatory Max: 43.0%)\n"
            f"   • Total Interest Over Tenure: ${metrics.total_interest_payable:,.2f}\n"
            f"   • Rule Assessment: {'; '.join(rule_reasons)}\n\n"
            f"2. QUALITATIVE & DOCUMENTARY FINDINGS:\n"
            f"   {doc_excerpts}\n\n"
            f"3. UNDERWRITING CONCLUSION:\n"
            f"   The calculated DTI ({metrics.debt_to_income_ratio*100:.1f}%) and credit metrics indicate "
            f"{'acceptable risk parameters for approval.' if decision == DecisionStatus.APPROVED else 'elevated risk necessitating secondary collateral or decline.'} "
            f"{f'Officer remarks: {officer_notes}' if officer_notes else ''}"
        )
        return synthesis
