# 🏦 Hybrid Retail Loan Credit Analyst Engine

> **Deterministic Financial Risk Rule Engine + Local LLM Qualitative Document Analysis & FAISS Vector Search**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![pytest](https://img.shields.io/badge/pytest-Passing-brightgreen?style=flat-square&logo=pytest&logoColor=white)](https://pytest.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)

---

## 🏛️ Architectural Thesis

In banking and retail loan underwriting, **LLMs should never perform arithmetic**. Large Language Models are stochastic token predictors that frequently hallucinate compounding interest, amortization schedules, and debt-to-income (DTI) ratios.

This system establishes an enterprise hybrid architecture:
1. **100% Deterministic Mathematical Core:** Python algorithms strictly compute amortized Equated Monthly Installment (EMI), total repayment liability, and DTI ratios against regulatory thresholds (max 43%).
2. **Semantic Document Retrieval (FAISS):** Indexes unstructured applicant documentation (employer verification letters, tax notices, bank memos) into vector space.
3. **Bounded Qualitative LLM Synthesis:** Generates human-readable, auditable underwriting reports grounded strictly in verified math and retrieved documents with zero arithmetic authority.

---

## 📐 System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   HYBRID CREDIT UNDERWRITING ARCHITECTURE                        │
└──────────────────────────────────────────────────────────────────────────────────┘
    [Credit Officer / API Request]
                  │
                  ▼
    [FastAPI & Pydantic v2 Gateway]
                  │
        ┌─────────┴────────────────────────────────────────┐
        ▼                                                  ▼
 [Deterministic Rule Engine]               [FAISS Vector Document Index]
 • Amortized Monthly EMI Calculation       • Cosine Semantic Search
 • Regulatory DTI Ratio Checks (≤43%)      • Employer & Income Document Parser
 • FICO Tier Eligibility                   • Context Chunking
        │                                                  │
        └─────────────────────────┬────────────────────────┘
                                  ▼
                   [Bounded LLM Synthesis Engine]
                   • Auditable Underwriting Report
                   • Qualitative Risk Justification
                   • Immutable SHA-256 Decision Hash
                                  │
                                  ▼
                    [REST Response / Streamlit UI]
```

---

## 📂 Repository Structure

```
credit-analyst-hybrid-ai/
├── app/
│   ├── core/
│   │   ├── rules.py         # 100% Deterministic EMI, DTI & banking threshold engine
│   │   ├── retriever.py     # In-memory FAISS-style semantic vector retriever
│   │   └── llm_engine.py    # Bounded qualitative report synthesizer
│   ├── schemas/
│   │   └── loan.py          # Strict Pydantic v2 data contracts
│   └── main.py              # FastAPI REST API endpoints
├── frontend/
│   └── streamlit_app.py     # Interactive underwriter dashboard
├── tests/
│   └── test_rules.py        # Complete pytest coverage for financial logic
├── Dockerfile               # Multi-stage production container
└── requirements.txt         # Pinned production dependencies
```

---

## 🚀 Quickstart & Local Setup

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/rajat-dev-new/credit-analyst-hybrid-ai.git
cd credit-analyst-hybrid-ai

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Test Suite
```bash
pytest tests/ -v
```

### 3. Launch the FastAPI Backend
```bash
uvicorn app.main:app --reload --port 8000
# OpenAPI Docs available at: http://localhost:8000/docs
```

### 4. Launch the Streamlit Underwriter UI
```bash
streamlit run frontend/streamlit_app.py
```

---

## 🧪 Example API Request

```bash
curl -X POST "http://localhost:8000/api/v1/loan/evaluate" \
     -H "Content-Type: application/json" \
     -d '{
       "application_id": "APP-2026-789",
       "financials": {
         "monthly_gross_income": 8500.0,
         "existing_monthly_debt": 600.0,
         "credit_score": 750,
         "employment_type": "SALARIED",
         "employment_tenure_months": 28
       },
       "loan": {
         "requested_amount": 35000.0,
         "tenure_months": 48,
         "annual_interest_rate": 0.065,
         "loan_purpose": "HOME_PURCHASE"
       },
       "qualitative_notes": "Senior cloud engineer with verified continuous employment."
     }'
```

---

## 🛡️ Key Principles & Guardrails
* **Zero Hallucination Arithmetic:** Regulatory compliance demands exact precision down to the cent.
* **Auditability:** Every credit decision includes an immutable SHA-256 hash tying the inputs to the decision.
* **Extensible AI Layer:** Ready for drop-in integration with local Ollama instances (`llama3`) or hosted LLM endpoints.

---

## 👤 Author
**Rajat Patle** — Senior Software Engineer & AI Architect
- **Interactive Portfolio:** [rajat-dev-new.github.io](https://rajat-dev-new.github.io)
- **GitHub:** [@rajat-dev-new](https://github.com/rajat-dev-new)
- **Email:** [patlerajat94@gmail.com](mailto:patlerajat94@gmail.com)
