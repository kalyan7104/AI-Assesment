"""
Policy Retriever Agent - Finds relevant policy information with proper citations.
"""
from crewai import Agent
from src.agents.llm_factory import get_llm
from src.agents.tools import PolicyRetrievalTool


def create_policy_retriever_agent() -> Agent:
    """Create and configure the Policy Retriever Agent."""
    
    llm = get_llm(temperature=0.1)  # Low temperature for accurate retrieval
    
    # Initialize tools
    policy_tool = PolicyRetrievalTool()
    
    agent = Agent(
        role="Policy Research Specialist",
        goal=(
            "Find and extract the most relevant policy information for customer issues. "
            "Always provide accurate citations including document ID and section. "
            "Never make up information - only use what is found in the policy documents."
        ),
        backstory=(
            "You are a meticulous policy research specialist with deep knowledge of "
            "e-commerce policies. You excel at finding the exact policy sections that "
            "apply to customer situations. You understand that accuracy is paramount - "
            "you always cite your sources with document IDs and section numbers. "
            "You never fabricate policy information or make assumptions. If a policy "
            "doesn't exist or isn't clear, you explicitly state that. You know that "
            "proper citations build trust and allow for verification."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[policy_tool],
        llm=llm
    )
    
    return agent


def get_policy_retrieval_task_description() -> str:
    """Get the task description for the policy retriever agent."""
    return """
Based on the triage analysis, retrieve all relevant policy information needed to address the customer's issue.

**Your Task**:
1. Use the Policy Retrieval Tool to search for relevant policies
2. Search multiple times if needed to cover all aspects of the issue
3. Extract the specific policy details that apply to this situation
4. Organize the information logically

**Output Format**:
```
RELEVANT POLICIES FOUND:

Policy 1: [Policy Title]
Document ID: [e.g., POL-001]
Section: [Section name/number]
Key Information:
- [Specific rule or detail]
- [Timeframes, if applicable]
- [Conditions or exceptions]
- [Any other relevant details]

Policy 2: [If applicable]
Document ID: [e.g., POL-002]
Section: [Section name/number]
Key Information:
- [Details...]

SPECIAL CONSIDERATIONS:
- [Any exceptions that apply]
- [Regional variations if mentioned]
- [Important conditions or requirements]

POLICY GAPS:
- [If any aspect of the customer's issue is not covered by policy, state it clearly]
```

**CRITICAL RULES**:
- ALWAYS include Document ID (POL-XXX) for every policy cited
- ALWAYS include Section name/number
- ONLY cite information that was actually retrieved from the policy documents
- If you cannot find a policy for something, explicitly state "No policy found for [topic]"
- Do not paraphrase in a way that changes meaning
- Include specific timeframes, amounts, and conditions exactly as stated in policies
- If policies conflict or have exceptions, note them clearly

**Search Strategy**:
- Start with broad searches for the issue category
- Then search for specific details (timeframes, exceptions, etc.)
- Search for related policies that might apply
- Verify you've covered all aspects of the customer's situation
"""
