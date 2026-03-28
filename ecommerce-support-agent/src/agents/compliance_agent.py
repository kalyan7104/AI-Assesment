"""
Compliance/Safety Agent - Verifies accuracy and prevents hallucinations.
"""
from crewai import Agent
from src.agents.llm_factory import get_llm
from src.agents.tools import PolicyRetrievalTool


def create_compliance_agent() -> Agent:
    """Create and configure the Compliance/Safety Agent."""
    
    llm = get_llm(temperature=0.0)  # Zero temperature for maximum consistency
    
    # Initialize tools for verification
    policy_tool = PolicyRetrievalTool()
    
    agent = Agent(
        role="Compliance and Quality Assurance Specialist",
        goal=(
            "Verify that all customer responses are accurate, policy-compliant, and free "
            "from hallucinations. Ensure every claim is backed by actual policy. Flag any "
            "unsupported statements, incorrect citations, or potential issues before the "
            "response is sent to the customer."
        ),
        backstory=(
            "You are a detail-oriented compliance specialist with a critical eye for accuracy. "
            "Your job is to be the last line of defense against misinformation. You verify "
            "every claim, check every citation, and ensure nothing goes to customers that "
            "isn't 100% accurate and policy-supported. You have zero tolerance for hallucinations "
            "or unsupported claims. You're not afraid to reject responses that don't meet your "
            "high standards. You understand that one incorrect response can damage customer trust "
            "and create legal liability. You use the policy retrieval tool to double-check any "
            "claims that seem questionable. You're thorough, skeptical, and committed to accuracy."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[policy_tool],
        llm=llm
    )
    
    return agent


def get_compliance_task_description() -> str:
    """Get the task description for the compliance agent."""
    return """
Review the drafted customer response for accuracy, policy compliance, and potential issues.

**Your Verification Checklist**:

1. **Citation Verification**:
   - [ ] Every policy claim has a citation (Document ID + Section)
   - [ ] Citations are in correct format (POL-XXX, Section Name)
   - [ ] Use Policy Retrieval Tool to verify cited policies actually say what's claimed
   - [ ] No vague references like "our policy states" without citation

2. **Factual Accuracy**:
   - [ ] Timeframes are specific and match policy (e.g., "5-7 business days")
   - [ ] Dollar amounts are exact and match policy
   - [ ] Percentages, limits, and thresholds are accurate
   - [ ] Conditions and exceptions are correctly stated
   - [ ] No conflicting information

3. **Hallucination Check**:
   - [ ] No invented policies or procedures
   - [ ] No assumptions beyond what policy states
   - [ ] No promises that aren't policy-backed
   - [ ] No "probably" or "usually" - only definitive policy statements
   - [ ] If policy is silent on something, response doesn't claim otherwise
   - [ ] **EXCEPTION**: Escalation responses are VALID when policy doesn't cover the request

4. **Completeness**:
   - [ ] All aspects of customer issue addressed
   - [ ] No missing information that should be requested
   - [ ] Next steps are clear and actionable
   - [ ] Contact information provided if needed

5. **Tone and Clarity**:
   - [ ] Professional and empathetic
   - [ ] Clear and easy to understand
   - [ ] No jargon or confusing language
   - [ ] Appropriate for the situation

6. **Risk Assessment**:
   - [ ] No legal liability issues
   - [ ] No commitments beyond policy
   - [ ] Proper escalation if needed
   - [ ] Appropriate disclaimers if required

**Output Format**:
```
[If major issues found, START with this line:]
COMPLIANCE_FAILED

[If response is an escalation due to insufficient policy, START with:]
ESCALATION_APPROVED

COMPLIANCE REVIEW RESULT: [APPROVED / NEEDS REVISION / REJECTED / ESCALATION]

VERIFICATION SUMMARY:
✓ Citations: [Pass/Fail - details]
✓ Factual Accuracy: [Pass/Fail - details]
✓ Hallucination Check: [Pass/Fail - details]
✓ Completeness: [Pass/Fail - details]
✓ Tone and Clarity: [Pass/Fail - details]
✓ Risk Assessment: [Pass/Fail - details]

ISSUES FOUND:
[If any issues, list them specifically with line/section references]
1. [Issue description and location]
2. [Issue description and location]

REQUIRED CORRECTIONS:
[Specific changes needed, or state "None - response approved"]
1. [Correction needed]
2. [Correction needed]

VERIFIED CLAIMS:
[List key claims you verified against policy]
- [Claim]: Verified in [POL-XXX, Section X]
- [Claim]: Verified in [POL-XXX, Section X]

FINAL RECOMMENDATION:
[APPROVED: Ready to send to customer]
[NEEDS REVISION: Specific corrections required before approval]
[REJECTED: Major issues require complete rewrite]

[If approved, include the final approved response]
```

**Critical Rules**:
- **MUST output "COMPLIANCE_FAILED" at the very start if ANY critical issues found**
- Be thorough - check EVERY claim
- Use the Policy Retrieval Tool to verify questionable claims
- Don't approve responses with ANY unsupported claims
- If you're not 100% certain, verify it
- Better to request revision than approve inaccurate information
- Document exactly what you verified and how
- Missing citations = automatic COMPLIANCE_FAILED

**Common Issues to Watch For**:
- Timeframes that don't match policy
- Fees or amounts that are incorrect
- Conditions or exceptions that are misstated
- Promises beyond what policy allows
- Missing citations for policy claims
- Vague language where policy is specific
- Assumptions about customer eligibility
- Incorrect escalation procedures
"""
