# E-commerce Support Resolution Agent - Assessment Write-Up

**Author:** Lokesh  
**Date:** January 2024  
**Framework:** CrewAI  
**Assessment:** Purple Merit Technologies - Multi-Agent RAG System

---

## Architecture Overview

This system implements a **5-agent sequential pipeline** using CrewAI to resolve customer support tickets with policy-grounded, citation-backed responses:

```
Customer Ticket → [Triage] → [Policy Retriever] → [Resolution Writer] → [Compliance] → [Formatter] → Final Output
```

**Agent Flow:**
1. **Triage Agent** (temp=0.1): Classifies issue type, identifies missing information, assesses urgency
2. **Policy Retriever Agent** (temp=0.1): Searches vector store, returns relevant policies with citations (Document ID + Section)
3. **Resolution Writer Agent** (temp=0.3): Drafts customer response using only retrieved policies
4. **Compliance Agent** (temp=0.0): Verifies accuracy, checks citations, blocks unsupported claims with "COMPLIANCE_FAILED" flag
5. **Final Formatter Agent** (temp=0.0): Structures output, separates internal analysis from customer message

**Key Design Decision:** Sequential process ensures each agent builds on verified outputs from previous agents, with Compliance Agent as final quality gate.

---

## Agent Responsibilities & Prompts (High Level)

| Agent | Role | Key Prompt Instructions | Temperature |
|-------|------|------------------------|-------------|
| **Triage** | Issue classifier | "Categorize into 13 issue types, identify missing info, assess urgency. Never assume." | 0.1 |
| **Policy Retriever** | RAG specialist | "Use PolicyRetrievalTool. ALWAYS cite Document ID + Section. Never fabricate." | 0.1 |
| **Resolution Writer** | Response drafter | "Write empathetic response using ONLY retrieved policies. NO hallucination." | 0.3 |
| **Compliance** | Quality gate | "Verify every claim. Output 'COMPLIANCE_FAILED' if ANY issues. Use temp=0." | 0.0 |
| **Formatter** | Output structurer | "Clean output. Remove policy codes from customer message. Track metrics." | 0.0 |

**Anti-Hallucination Controls:**
- Mandatory PolicyRetrievalTool usage (agents cannot cite without retrieval)
- Compliance Agent with temperature=0 for deterministic verification
- "COMPLIANCE_FAILED" blocking mechanism stops execution if citations missing
- Evidence-only generation prompts with explicit refusal rules
- Escalation path for "not in policy" scenarios

---

## Data Sources

- **12 synthetic policy documents** (~20,200 words) covering returns, shipping, payments, warranties, promotions, cancellations, etc.
- **30 test cases** (15 standard + 15 tricky) including exceptions, conflicts, and edge cases
- **Vector Store:** ChromaDB with Google Gemini embeddings (gemini-embedding-001)
- **Chunking:** 800 tokens, 100 overlap (balances context vs precision)
- **Retrieval:** Top-5 results with metadata filtering

See `data/sources.md` for complete documentation.

---

## Evaluation Summary

**Test Set:** 30 tickets (8 standard, 6 exception-heavy, 3 conflict, 3 not-in-policy, 10 additional edge cases)

**Key Metrics (Expected):**
- **Citation Coverage Rate:** 95-100% (all policy claims backed by POL-XXX citations)
- **Unsupported Claim Rate:** <0.2 issues/test (Compliance Agent blocks unsupported claims)
- **Correct Escalation Rate:** 90-100% (conflict/not-in-policy cases properly escalated)

**Example Runs Provided:**
1. **Exception Handled:** Perishable item with 48h photo requirement (TRICKY-003) → APPROVED with conditions
2. **Conflict Escalation:** Marketplace seller 14-day vs platform 30-day policy (TRICKY-002) → ESCALATED
3. **Abstention:** Missing order number and details (TRICKY-006) → NEEDS MORE INFO

See `examples/example_outputs/` for full runs and `evaluation/results_summary.json` for detailed metrics.

---

## Key Failure Modes

1. **Ambiguous Policies:** When policy language is vague (e.g., "reasonable timeframe"), system correctly escalates rather than guessing
2. **Multi-Issue Tickets:** Complex tickets with 3+ issues may require clarification to prioritize resolution
3. **Edge Case Boundaries:** Exact boundary conditions (e.g., day 30 vs day 31 for returns) handled correctly but may need human review for customer satisfaction
4. **Seller-Specific Data:** Marketplace seller policies not in vector store require escalation
5. **LLM Variability:** Despite temp=0 for compliance, occasional formatting inconsistencies in output structure

**Mitigation:** Compliance Agent catches most issues; escalation path ensures no incorrect resolutions sent to customers.

---

## What I Would Improve Next

1. **Structured Output Parsing:** Use Pydantic models to enforce strict JSON output format (eliminate formatting variability)
2. **Confidence Scoring:** Add numerical confidence scores for each decision to help prioritize human review
3. **Multi-Turn Conversations:** Extend to handle follow-up questions and clarifications in same session
4. **A/B Testing Framework:** Compare different chunking strategies (600 vs 800 vs 1000 tokens) and retrieval settings (top-3 vs top-5)
5. **Feedback Loop:** Implement human-in-the-loop corrections to fine-tune retrieval and improve policy coverage
6. **Performance Optimization:** Cache embeddings and add async processing for faster response times (<5 seconds)
7. **Observability:** Add LangSmith/Weights & Biases integration for detailed agent execution tracing

---

**Total Development Time:** ~20 hours  
**Lines of Code:** ~2,500  
**Dependencies:** CrewAI, ChromaDB, Google Gemini, LangChain

**GitHub Repository:** [Include your repo URL here]
