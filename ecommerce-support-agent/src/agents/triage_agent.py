"""
Triage Agent - Classifies customer issues and identifies missing information.
"""
from crewai import Agent
from src.agents.llm_factory import get_llm


def create_triage_agent() -> Agent:
    """Create and configure the Triage Agent."""
    
    llm = get_llm(temperature=0.1)  # Low temperature for consistent classification
    
    agent = Agent(
        role="Customer Support Triage Specialist",
        goal=(
            "Accurately classify customer support tickets into categories and identify "
            "any missing information needed to resolve the issue. Ensure all necessary "
            "details are present before proceeding to resolution."
        ),
        backstory=(
            "You are an experienced customer support triage specialist with years of "
            "experience in e-commerce. You have a keen eye for detail and can quickly "
            "identify the core issue in customer inquiries. You know exactly what "
            "information is needed to resolve different types of issues efficiently. "
            "You never make assumptions - if information is missing, you clearly state "
            "what additional details are required."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    return agent


def get_triage_task_description() -> str:
    """Get the task description for the triage agent."""
    return """
Analyze the customer support ticket and perform the following:

1. **Issue Classification**: Categorize the issue into one of these categories:
   - Returns & Refunds
   - Order Cancellation
   - Shipping & Delivery
   - Lost/Damaged Package
   - Payment Issues
   - Product Issues (defective, wrong item, missing items)
   - Account Issues
   - Promotions & Coupons
   - Gift Cards
   - Loyalty Program
   - Price Match
   - Warranty
   - Other

2. **Policy Conflict Detection**: Check for potential policy conflicts:
   - If customer is in EU region (EU-*, UK, etc.) → EU consumer law applies (14-day cooling-off period)
   - Check if marketplace seller vs platform policies differ
   - Identify if platform, seller, and regional laws conflict
   - If 2 or more policies conflict → Decision = NEEDS ESCALATION

3. **Missing Information Check**: Identify if any critical information is missing:
   - ONLY ask for information that CHANGES the decision outcome
   - Maximum 3 clarifying questions
   - Do NOT ask for nice-to-have details (exact SKU, product name) unless they affect eligibility
   - Required info varies by issue type:
     * Returns: order date, region, item category, fulfillment type
     * Shipping: order date, shipping method, tracking status
     * Refunds: order date, payment method, issue type

4. **Urgency Assessment**: Determine urgency level:
   - High: Time-sensitive issues (overnight shipping problems, urgent needs)
   - Medium: Standard issues requiring prompt attention
   - Low: General inquiries, non-urgent matters

5. **Output Format**: Provide your analysis in this structure:
   ```
   ISSUE CATEGORY: [Category name]
   CONFIDENCE: [0-100%]
   
   POLICY CONFLICTS DETECTED:
   - [List any conflicting policies: EU law, seller policy, platform policy]
   - [If 2+ conflicts exist, state "REQUIRES ESCALATION"]
   
   CLARIFYING QUESTIONS (MAX 3, only if answer changes decision):
   - [Question 1 - only if critical]
   - [Question 2 - only if critical]
   - [Question 3 - only if critical]
   
   URGENCY: [High/Medium/Low]
   
   MISSING INFORMATION:
   - [List each missing piece of information that affects the decision, or state "None - sufficient information to proceed"]
   
   SUMMARY:
   [Brief 1-2 sentence summary of the customer's issue]
   
   RECOMMENDED NEXT STEPS:
   [What should happen next - either request missing info, escalate due to conflicts, or proceed to policy retrieval]
   ```

**CRITICAL DECISION RULES**: 
- If 2 or more policies conflict → Decision = NEEDS ESCALATION (do not make a decision)
- If EU region detected (EU-*, UK) → always cite EU consumer law as a policy alongside seller and platform policies
- Clarifying questions → maximum 3, only ask if the answer changes the decision outcome
- Do NOT ask questions just for record-keeping purposes (e.g., exact SKU, product name unless it affects eligibility)
- If you have order date, region, and issue type → you likely have enough to proceed
- Be thorough but concise
- Do not make assumptions about missing information
"""
