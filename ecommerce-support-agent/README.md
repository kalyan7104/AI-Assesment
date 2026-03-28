# E-commerce Support Resolution Agent

A multi-agent RAG system that resolves customer support tickets using policy documents, with strong controls against hallucination.

## Overview

Five specialized AI agents process each ticket sequentially:

| Agent | Role |
|---|---|
| Triage | Classifies issue, flags missing info, assesses urgency |
| Policy Retriever | Semantic search over policy docs, returns citations |
| Resolution Writer | Drafts customer-facing response grounded in policy |
| Compliance | Verifies all claims have citations; blocks hallucinated responses |
| Final Formatter | Produces structured final output |

## Project Structure

```
ecommerce-support-agent/
├── src/
│   ├── agents/          # Agent definitions + LLM factory
│   ├── ingestion/       # Document loader, chunker, pipeline
│   ├── retrieval/       # ChromaDB vector store (multi-provider)
│   ├── orchestration/   # CrewAI crew + task wiring
│   ├── evaluation/      # Evaluation script
│   ├── models/          # Pydantic input models
│   └── main.py          # CLI entry point
├── data/
│   ├── policies/        # 12 markdown policy documents
│   └── test_cases/      # test_tickets.json, tricky_test_tickets.json
├── evaluation/          # Evaluation results (generated at runtime)
├── examples/
│   └── example_outputs/ # 3 annotated example runs
├── app.py               # Gradio web UI
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

### Prerequisites
- Python 3.9+
- Google API key (default) **or** OpenAI API key

### Installation

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env       # Windows
cp .env.example .env         # macOS/Linux
# Edit .env and add your API key
```

### Environment Variables (`.env`)

```env
# Pick one provider
LLM_PROVIDER=google          # or: openai

# Google (default)
GOOGLE_API_KEY=your_key_here
GOOGLE_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=gemini-embedding-001

# OpenAI (alternative)
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4-turbo-preview
```

### Build the Vector Store

Run once before first use (or to rebuild):

```bash
python run_ingestion.py
```

This loads all 12 policy documents from `data/policies/`, chunks them, generates embeddings, and persists to ChromaDB.

## Running the Agent

### CLI

```bash
# Interactive mode
python src/main.py

# Single ticket
python src/main.py --ticket "My order #12345 arrived damaged, I want a refund"

# Run built-in examples
python src/main.py --examples
```

### Python API

```python
from src.orchestration.crew import process_support_ticket

# Simple text input
result = process_support_ticket("My order is late")

# With structured order context
result = process_support_ticket({
    "ticket_text": "My order arrived late and the cookies are melted.",
    "order_context": {
        "order_id": "ORD-12345",
        "order_date": "2024-01-15",
        "delivery_date": "2024-01-20",
        "item_category": "perishable",
        "fulfillment_type": "first_party",
        "shipping_region": "US-CA",
        "order_status": "delivered"
    }
})

print(result["final_output"])
# result["status"] → "SUCCESS" | "ESCALATED" | "FAILED"
```

## Running Evaluation

```bash
python src/evaluation/run_evaluation.py
```

Runs all test cases in `data/test_cases/` and writes JSON results to `evaluation/`. Reports:

- Citation coverage rate
- Unsupported claim rate
- Correct escalation rate
- Correct "needs more info" rate

## Example Inputs & Outputs

Three annotated examples are in `examples/example_outputs/`:

| File | Scenario | Decision |
|---|---|---|
| `example_1_exception_handled.md` | Perishable item spoiled at 48h boundary | APPROVED |
| `example_2_conflict_escalation.md` | Marketplace vs platform policy conflict | ESCALATED |
| `example_3_needs_more_info.md` | Vague ticket with no order details | NEEDS MORE INFO |

## Anti-Hallucination Controls

- Every policy claim requires a `POL-XXX §Section` citation
- Compliance Agent blocks any response with unsupported claims
- Policy Retrieval Tool enforces a minimum evidence threshold (configurable via `MIN_EVIDENCE_THRESHOLD`)
- Compliance Agent runs at temperature=0 for deterministic verification

## Technology Stack

| Component | Technology |
|---|---|
| Agent framework | CrewAI |
| LLM | Google Gemini 2.5 Flash / GPT-4 |
| Embeddings | Gemini Embedding 001 / OpenAI text-embedding-3-small |
| Vector store | ChromaDB |
