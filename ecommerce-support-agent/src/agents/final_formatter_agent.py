"""
Final Formatter Agent - Combines agent outputs into the required structured ticket resolution.
"""
from crewai import Agent
from src.agents.llm_factory import get_llm


def create_final_formatter_agent() -> Agent:
    """Create and configure the Final Formatter Agent."""
    llm = get_llm(temperature=0.0)

    agent = Agent(
        role="Support Ticket Output Formatter",
        goal=(
            "Transform multi-agent outputs into a clean, customer-friendly final response. "
            "Remove system jargon, keep policy codes out of customer messages, use tight "
            "bullet-point rationales, and ensure all claims are backed by citations in the "
            "reference section. Output must be production-ready and professional."
        ),
        backstory=(
            "You are a rigorous support operations specialist who transforms multi-agent "
            "outputs into a clean, structured ticket resolution. You are EXTREMELY careful "
            "to never hallucinate or invent information - you only use what's in the input "
            "ticket and retrieved policies. You keep rationales to exactly 3 lines: policy rule, "
            "application, and justification. You separate internal analysis from customer-facing "
            "output. You track metrics like citation coverage and unsupported claims. You never "
            "put policy codes in customer messages. You use 'NEEDS MORE INFO' instead of 'PARTIAL'. "
            "You are the final quality gate ensuring output is production-ready and accurate."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    return agent


def get_final_formatter_task_description() -> str:
    """Get the task description for the final formatter agent."""
    return """
Using the outputs from the triage analysis, policy retrieval, resolution draft, and compliance review, create a final structured ticket output.

**CRITICAL RULES:**
1. **NO HALLUCINATION** - Only use information from input ticket + retrieved policies. DO NOT invent prices, dates, or details.
2. **EXACT FORMAT** - Follow the structure below EXACTLY with all section dividers and formatting.
3. **DECISION LOGIC**:
   - If info missing → "NEEDS MORE INFO"
   - If approved → "APPROVE"
   - If denied → "DENY"
   - If not in policy → "ESCALATE"

**EXACT OUTPUT FORMAT:**

```
================================================================
CUSTOMER SUPPORT TICKET ANALYSIS
================================================================
TICKET ID     : [Order ID or generate TICKET-XXXXX]
PROCESSED AT  : [Current timestamp in UTC]
================================================================

----------------------------------------------------------------
SECTION 1 — CLASSIFICATION
----------------------------------------------------------------
Issue Type    : [Primary issue category]
Sub-type      : [Specific issue details]
Confidence    : [XX]%

----------------------------------------------------------------
SECTION 2 — CLARIFYING QUESTIONS
----------------------------------------------------------------
[List questions, or write: "None required. Sufficient information available to proceed."]

----------------------------------------------------------------
SECTION 3 — DECISION
----------------------------------------------------------------
Outcome       : [APPROVE / DENY / NEEDS MORE INFO / ESCALATE]
Type          : [Brief description of resolution]

----------------------------------------------------------------
SECTION 4 — RATIONALE
----------------------------------------------------------------
1. [First policy rule or fact - one sentence]
2. [How it applies to this case - one sentence]
3. [Additional relevant policy details - one sentence]
4. [Final justification or missing info - one sentence]

[Keep to 3-5 numbered points maximum. Be concise and factual.]

----------------------------------------------------------------
SECTION 5 — CITATIONS
----------------------------------------------------------------
[1] [POL-XXX, Section Y.Z] — [Section Title]
    [Brief description of what this policy covers]
    [Key rule or exception if applicable]

[2] [POL-XXX, Section Y.Z] — [Section Title]
    [Brief description]

[Continue for all cited policies...]

----------------------------------------------------------------
SECTION 6 — CUSTOMER RESPONSE DRAFT
----------------------------------------------------------------
Subject: [Appropriate subject line]

Dear Customer,

[Empathetic opening acknowledging their issue]

[Policy explanation with inline citations: (POL-XXX, Section Y.Z)]

[Resolution or next steps with specific details]

[Closing]

Warm regards,
Customer Support Team

----------------------------------------------------------------
SECTION 7 — NEXT STEPS / INTERNAL NOTES
----------------------------------------------------------------
[ ] [Action item 1 for support team]
[ ] [Action item 2 for support team]
[ ] [Action item 3 for support team]
[ ] [Escalation notes if needed]

----------------------------------------------------------------
METRICS
----------------------------------------------------------------
Citation Coverage   : [XX]% ([cited]/[total] claims cited)
Unsupported Claims  : [number]
Decision Confidence : [XX]%
Compliance Status   : [PASS / FAIL]
================================================================
END OF REPORT
================================================================
```

**FORMATTING RULES:**
- Use exactly 64 equals signs (=) for major dividers
- Use exactly 64 dashes (-) for section dividers
- Align colons in key-value pairs (use spaces)
- Use [ ] checkboxes for action items
- Number rationale points (1, 2, 3, 4)
- Number citations [1], [2], [3]
- Keep sections in exact order shown

**RATIONALE FORMAT (3-5 points max):**
1. [Policy rule]
2. [Application to case]
3. [Additional context]
4. [Final justification]

**CITATION FORMAT:**
[1] POL-XXX, Section Y.Z — Section Title
    Brief description of policy coverage.
    Key rules or exceptions.

**METRICS CALCULATION:**
- Citation Coverage = (number of cited claims / total policy claims) × 100
- Unsupported Claims = count of statements without policy backing
- Decision Confidence = based on information completeness
- Compliance Status = PASS if approved by compliance agent, FAIL otherwise

**CRITICAL:**
- DO NOT invent ticket IDs, timestamps, prices, or dates not in input
- Use actual order ID from input if provided
- Generate timestamp using current time
- All policy claims in customer response MUST have inline citations
- Keep rationale to 3-5 points maximum
- Use exact formatting with proper spacing and alignment
"""
