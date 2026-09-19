import streamlit as st
from app.core.rules import evaluate_deterministic_rules
from app.schemas.loan import (
    ApplicantFinancials,
    LoanRequestDetails,
    EmploymentType,
    LoanPurpose,
    DecisionStatus
)
from app.core.retriever import VectorDocumentRetriever
from app.core.llm_engine import QualitativeLLMEngine
from app.schemas.loan import QualitativeDocument

st.set_page_config(page_title="Credit Analyst AI Engine", layout="wide", page_icon="🏦")

st.title("🏦 Hybrid Retail Loan Credit Analyst Engine")
st.markdown("Deterministic Python Risk Engine (Zero LLM Math) + Semantic Vector Search & Bounded AI Rationale")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Applicant Financials & Request")
    gross_income = st.number_input("Monthly Gross Income ($)", min_value=500.0, value=7500.0, step=250.0)
    existing_debt = st.number_input("Existing Monthly Debt ($)", min_value=0.0, value=650.0, step=50.0)
    credit_score = st.slider("Credit Score (FICO)", min_value=300, max_value=850, value=740)
    tenure_months = st.number_input("Employment Tenure (Months)", min_value=0, value=24)
    emp_type = st.selectbox("Employment Type", [e.value for e in EmploymentType])

    st.subheader("2. Loan Details")
    requested_amount = st.number_input("Loan Amount Requested ($)", min_value=1000.0, value=25000.0, step=1000.0)
    loan_tenure = st.slider("Loan Tenure (Months)", min_value=6, max_value=84, value=36)
    interest_rate = st.number_input("Annual Interest Rate (%)", min_value=1.0, max_value=35.0, value=6.5) / 100.0
    loan_purpose = st.selectbox("Loan Purpose", [p.value for p in LoanPurpose])

    officer_notes = st.text_area("Officer Notes / Qualitative Memo", "Applicant provided employer verification letter confirming stable senior engineering position.")

with col2:
    st.subheader("3. Underwriting Decision & Telemetry")
    if st.button("Run Hybrid Underwriting Assessment", type="primary"):
        financials = ApplicantFinancials(
            monthly_gross_income=gross_income,
            existing_monthly_debt=existing_debt,
            credit_score=credit_score,
            employment_type=EmploymentType(emp_type),
            employment_tenure_months=tenure_months
        )
        loan = LoanRequestDetails(
            requested_amount=requested_amount,
            tenure_months=loan_tenure,
            annual_interest_rate=interest_rate,
            loan_purpose=LoanPurpose(loan_purpose)
        )

        metrics, decision, reasons = evaluate_deterministic_rules(financials, loan)

        # Status badge
        if decision == DecisionStatus.APPROVED:
            st.success(f"DECISION: {decision.value}")
        elif decision == DecisionStatus.CONDITIONALLY_APPROVED:
            st.warning(f"DECISION: {decision.value}")
        else:
            st.error(f"DECISION: {decision.value}")

        # Metrics cards
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Calculated EMI", f"${metrics.calculated_monthly_emi:,.2f}")
        m_col2.metric("Debt-to-Income (DTI)", f"{metrics.debt_to_income_ratio*100:.1f}%")
        m_col3.metric("Total Interest", f"${metrics.total_interest_payable:,.2f}")

        st.markdown("#### Deterministic Rule Logs:")
        for r in reasons:
            st.write(f"- {r}")

        # Qualitative synthesis
        retriever = VectorDocumentRetriever()
        sample_doc = QualitativeDocument(
            doc_id="DOC-991",
            doc_type="employer_letter",
            text_content=officer_notes
        )
        retriever.add_documents([sample_doc])
        retrieved = [doc for doc, _ in retriever.search("employment stability", top_k=1)]

        llm = QualitativeLLMEngine()
        synthesis = llm.synthesize_explanation(
            applicant_id="APP-DEMO-001",
            decision=decision,
            metrics=metrics,
            rule_reasons=reasons,
            retrieved_docs=retrieved,
            officer_notes=officer_notes
        )

        st.markdown("#### AI Qualitative Synthesis Report:")
        st.code(synthesis, language="text")
