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

2. **Missing Information Check**: Identify if any critical information is missing:
   - Order number
   - Purchase date
   - Item details (name, SKU, quantity)
   - Issue description
   - Customer contact information
   - Desired resolution
   - Any other relevant details for this specific issue type

3. **Urgency Assessment**: Determine urgency level:
   - High: Time-sensitive issues (overnight shipping problems, urgent needs)
   - Medium: Standard issues requiring prompt attention
   - Low: General inquiries, non-urgent matters

4. **Output Format**: Provide your analysis in this structure:
   ```
   ISSUE CATEGORY: [Category name]
   CONFIDENCE: [0-100%]
   CLARIFYING QUESTIONS:
   - [Question 1]
   - [Question 2]
   - [Question 3]
   URGENCY: [High/Medium/Low]
   
   MISSING INFORMATION:
   - [List each missing piece of information, or state "None - all required information present"]
   
   SUMMARY:
   [Brief 1-2 sentence summary of the customer's issue]
   
   RECOMMENDED NEXT STEPS:
   [What should happen next - either request missing info or proceed to policy retrieval]
   ```

**IMPORTANT**: 
- Be thorough but concise
- Do not make assumptions about missing information
- If order number is missing for order-related issues, flag it
- Consider what information is actually needed for THIS specific issue type
"""
