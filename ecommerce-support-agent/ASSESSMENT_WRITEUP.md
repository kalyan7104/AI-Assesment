# E-commerce Support Resolution Agent — Write-Up

**Author:** Kalyan | **Framework:** CrewAI + ChromaDB + Google Gemini  
**GitHub:** https://github.com/kalyan7104/AI-Assesment

---

## Architecture Overview

A 5-agent sequential RAG pipeline. Each agent receives the outputs of all prior agents as context.

```
Customer Ticket
      │
      ▼
 [1. Triage] ──────────────────────────────────────────────────────┐
      │                                                             │
      ▼                                                             │
 [2. Policy Retriever] ← ChromaDB (gemini-embedding-001)           │
      │                                                             │
      ▼                                                             ▼
 [3. Resolution Writer]                                     context passed
      │                                                      to each agent
      ▼
 [4. Compliance] ── COMPLIANCE_FAILED? → block + return FAILED
      │
      ▼
 [5. Final Formatter] → Structured output (SUCCESS / ESCALATED / FAILED)
```

**Key design decision:** The Compliance Agent is a hard gate — if any claim lacks a `POL-XXX §Section` citation, the entire response is blocked and flagged for human review rather than sent to the customer.

---

## Agent Responsibilities & Prompts (High Level)

| Agent | Responsibility | Key Prompt Constraint | Temp |
|---|---|---|---|
| Triage | Classify into 13 issue types, flag missing info, assess urgency | "Never assume missing details" | 0.1 |
| Policy Retriever | Semantic search via PolicyRetrievalTool, return cited excerpts | "ALWAYS cite Document ID + Section. Never fabricate." | 0.1 |
| Resolution Writer | Draft customer-facing response from retrieved policies only | "Use ONLY retrieved policies. No hallucination." | 0.3 |
| Compliance | Verify every claim has a citation; output COMPLIANCE_FAILED if not | "Block if ANY unsupported claim exists." | 0.0 |
| Final Formatter | Separate internal analysis from customer message, clean output | "Remove policy codes from customer-facing text." | 0.0 |

---

## Data Sources

- **12 synthetic policy documents** covering returns, shipping, payments, warranties, promotions, cancellations, gift cards, loyalty, price match, account, product availability, and privacy
- **Chunking:** 800 chars, 100 overlap — balances retrieval precision vs context completeness
- **Vector store:** ChromaDB (persistent), embeddings via `gemini-embedding-001`
- **Retrieval:** Top-5 results; minimum evidence threshold of 2 documents enforced before answering
- **Test cases:** 30 tickets — 15 standard + 15 tricky (exceptions, policy conflicts, ambiguous inputs)

---

## Evaluation Summary

| Metric | Expected Result |
|---|---|
| Citation coverage rate | 95–100% |
| Unsupported claim rate | < 0.2 issues / test |
| Correct escalation rate | 90–100% |
| Correct "needs more info" rate | 90–100% |

**3 example runs provided** (`examples/example_outputs/`):
- Exception correctly applied: perishable item at exact 48h boundary → **APPROVED**
- Policy conflict escalated: marketplace 14-day vs platform 30-day → **ESCALATED**
- Correct abstention: vague ticket with no order details → **NEEDS MORE INFO**

**Key failure modes:**
- Vague policy language (e.g. "reasonable timeframe") causes over-escalation — acceptable but conservative
- Multi-issue tickets may get partial resolution if triage prioritises one issue
- LLM output formatting variability despite temp=0 on Compliance/Formatter agents

---

## What I Would Improve Next

1. **Structured JSON output** — enforce via Pydantic response models to eliminate formatting variability
2. **Confidence scores** — numeric per-decision confidence to prioritise human review queue
3. **Multi-turn support** — handle follow-up clarifications within the same session
4. **Retrieval tuning** — A/B test chunk sizes (600/800/1000) and top-k (3/5/7) against citation accuracy
5. **Async processing** — parallel agent execution where dependencies allow, targeting < 5s response time
6. **Observability** — LangSmith or W&B tracing for per-agent latency and retrieval quality monitoring
