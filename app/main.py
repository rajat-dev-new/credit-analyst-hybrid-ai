"""
FastAPI Entry Point for Hybrid Credit Analyst Engine
"""
import hashlib
from fastapi import FastAPI, HTTPException, status
from app.schemas.loan import LoanEvaluationRequest, CreditDecisionResponse
from app.core.rules import evaluate_deterministic_rules
from app.core.retriever import VectorDocumentRetriever
from app.core.llm_engine import QualitativeLLMEngine

app = FastAPI(
    title="Hybrid Credit Analyst Engine API",
    description="Deterministic EMI/DTI Rule Engine combined with FAISS Semantic Search and Qualitative LLM Rationale.",
    version="1.0.0"
)

llm_engine = QualitativeLLMEngine()

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {
        "status": "healthy",
        "service": "credit-analyst-hybrid-ai",
        "engine_mode": "hybrid-deterministic-rag"
    }

@app.post("/api/v1/loan/evaluate", response_model=CreditDecisionResponse)
def evaluate_loan_application(request: LoanEvaluationRequest):
    try:
        # Step 1: Run deterministic calculations (Zero LLM arithmetic)
        metrics, provisional_decision, reasons = evaluate_deterministic_rules(
            financials=request.financials,
            loan=request.loan
        )

        # Step 2: Index and search supporting documents via Vector Retriever
        retriever = VectorDocumentRetriever()
        if request.supporting_documents:
            retriever.add_documents(request.supporting_documents)
        
        search_query = f"{request.loan.loan_purpose.value} income stability employer"
        search_results = retriever.search(search_query, top_k=2)
        retrieved_docs = [doc for doc, _ in search_results]

        # Step 3: Synthesize qualitative rationale bounded by rule scores
        qualitative_text = llm_engine.synthesize_explanation(
            applicant_id=request.application_id,
            decision=provisional_decision,
            metrics=metrics,
            rule_reasons=reasons,
            retrieved_docs=retrieved_docs,
            officer_notes=request.qualitative_notes or ""
        )

        # Step 4: Generate immutable audit hash of the decision
        raw_audit = f"{request.application_id}:{metrics.calculated_monthly_emi}:{provisional_decision.value}"
        audit_hash = hashlib.sha256(raw_audit.encode()).hexdigest()[:16]

        return CreditDecisionResponse(
            application_id=request.application_id,
            decision=provisional_decision,
            deterministic_metrics=metrics,
            rule_engine_reasons=reasons,
            qualitative_synthesis=qualitative_text,
            audit_hash=audit_hash
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation error: {str(e)}"
        )
