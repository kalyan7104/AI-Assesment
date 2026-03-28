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
2. **NO POLICY CODES IN CUSTOMER MESSAGE** - Customer response must be completely clean of technical codes.
3. **DECISION LOGIC**:
   - If info missing → "NEEDS MORE INFO"
   - If approved → "APPROVED"
   - If denied → "DENIED"
   - If not in policy → "ESCALATED"

Required Output Structure:

```
=== INTERNAL ANALYSIS ===

CLASSIFICATION: [Issue Type] (Confidence: [%])

RATIONALE:
1. [Relevant policy rule - one line]
2. [How it applies to this case - one line]
3. [What's missing OR final justification - one line]

ASSUMPTIONS / NOT IN POLICY:
- [Any missing information]
- [Any assumptions made]
- [Any aspects not covered by policy]
[If none, write: "None"]

METRICS:
- Citation Coverage: [X]%
- Unsupported Claims: [X]/[Total]
- Decision Confidence: [X]%

POLICY REFERENCES:
- [Policy Name] (Document: [POL-XXX], Section: [Section Name])
- [Additional references...]

DECISION: [APPROVED / DENIED / NEEDS MORE INFO / ESCALATED]

CLARIFYING QUESTIONS:
- [Question 1 if needed]
- [Question 2 if needed]
[If none needed, write: "None"]

NEXT STEPS (Internal):
[What support team should do - brief, actionable]

=== CUSTOMER RESPONSE ===

Dear Customer,

[Empathetic acknowledgment]

[Policy explanation in simple terms - NO codes, NO technical jargon]

[Resolution or next steps]

[Numbered action items if customer needs to do something]

Best regards,
Customer Support Team
```

**RATIONALE FORMAT - STRICT 3-LINE RULE:**
```
RATIONALE:
1. [Policy rule in one sentence]
2. [Application to this case in one sentence]
3. [Missing info OR justification in one sentence]
```

**BAD Rationale (Too long, mixed thinking):**
```
RATIONALE:
- POL-001 §3.3: Perishables refundable if damaged with photo proof (24h window)
- POL-001 §4.3: Items under $25 - no return required
- Customer reported within 48h window ✓
- Missing: Photos of damage, item value confirmation
- Need to verify if cookies are under $25
- Policy allows keeping items under $25
```

**GOOD Rationale (Clear, short, logical):**
```
RATIONALE:
1. Perishable items refundable if damaged and reported within 48h with photos (POL-001 §3.3)
2. Customer reported within timeframe but missing required photo evidence
3. Cannot proceed without photos - need more information
```

**CRITICAL - NO HALLUCINATION:**
- DO NOT invent prices (e.g., "$49.99") if not in input
- DO NOT invent dates if not provided
- DO NOT invent order details
- ONLY use what's in the ticket input + order context + retrieved policies

**DECISION MAPPING:**
- Missing info (photos, order number, etc.) → "NEEDS MORE INFO"
- Policy allows request → "APPROVED"
- Policy denies request → "DENIED"
- Not covered by policy → "ESCALATED"
- DO NOT use "PARTIAL" - use "NEEDS MORE INFO" instead

**CUSTOMER RESPONSE RULES:**
- Completely clean - no (POL-XXX) codes
- No technical jargon
- Natural, friendly language
- Specific and actionable

Use only information from the provided task outputs. Never invent details.
"""
