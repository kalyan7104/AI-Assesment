"""
Crew Orchestrator - Coordinates all agents to process support tickets.
"""
from crewai import Crew, Task, Process
from typing import Dict, Union, Optional

from src.agents.triage_agent import create_triage_agent, get_triage_task_description
from src.agents.policy_retriever_agent import create_policy_retriever_agent, get_policy_retrieval_task_description
from src.agents.resolution_writer_agent import create_resolution_writer_agent, get_resolution_writer_task_description
from src.agents.compliance_agent import create_compliance_agent, get_compliance_task_description
from src.agents.final_formatter_agent import create_final_formatter_agent, get_final_formatter_task_description
from src.models.input_models import SupportTicketInput, OrderContext


class SupportTicketCrew:
    """Orchestrates the multi-agent system for support ticket resolution."""
    
    def __init__(self):
        """Initialize all agents."""
        print("Initializing Support Ticket Crew...")
        
        # Create agents
        self.triage_agent = create_triage_agent()
        self.policy_retriever_agent = create_policy_retriever_agent()
        self.resolution_writer_agent = create_resolution_writer_agent()
        self.compliance_agent = create_compliance_agent()
        self.final_formatter_agent = create_final_formatter_agent()
        
        print("✓ All agents initialized")
    
    def process_ticket(self, ticket: Union[str, SupportTicketInput, Dict], order_context: Optional[OrderContext] = None) -> Dict:
        """
        Process a customer support ticket through all agents.
        
        Args:
            ticket: The customer support ticket (str, SupportTicketInput, or dict)
            order_context: Optional structured order information
            
        Returns:
            Dict containing the results from each agent
        """
        # Parse input
        if isinstance(ticket, str):
            ticket_input = SupportTicketInput(
                ticket_text=ticket,
                order_context=order_context
            )
        elif isinstance(ticket, dict):
            ticket_input = SupportTicketInput(**ticket)
        else:
            ticket_input = ticket
        
        # Format for agents
        formatted_input = ticket_input.format_for_agents()
        
        print("\n" + "="*60)
        print("Processing Support Ticket")
        print("="*60)
        print(formatted_input)
        print("="*60)
        
        # Task 1: Triage
        triage_task = Task(
            description=f"""
            {get_triage_task_description()}
            
            {formatted_input}
            """,
            agent=self.triage_agent,
            expected_output="Structured triage analysis with issue category, missing information, and next steps"
        )
        
        # Task 2: Policy Retrieval
        policy_task = Task(
            description=f"""
            {get_policy_retrieval_task_description()}
            
            Use the triage analysis to search for relevant policies.
            """,
            agent=self.policy_retriever_agent,
            expected_output="Relevant policy information with proper citations (Document ID and Section)",
            context=[triage_task]
        )
        
        # Task 3: Resolution Writing
        resolution_task = Task(
            description=f"""
            {get_resolution_writer_task_description()}
            
            {formatted_input}
            
            Use the triage analysis and retrieved policies to write the response.
            """,
            agent=self.resolution_writer_agent,
            expected_output="Complete customer response with policy citations",
            context=[triage_task, policy_task]
        )
        
        # Task 4: Compliance Check
        compliance_task = Task(
            description=f"""
            {get_compliance_task_description()}
            
            Review the drafted response for accuracy and compliance.
            
            CRITICAL: If you find ANY of the following issues, you MUST output "COMPLIANCE_FAILED" at the start:
            - Missing citations (no Document ID or Section)
            - Unsupported claims (statements not backed by retrieved policy)
            - Factual inaccuracies
            - Hallucinated information
            
            If compliance fails, the entire process will stop and require human review.
            """,
            agent=self.compliance_agent,
            expected_output="Compliance review with approval status and any required corrections",
            context=[triage_task, policy_task, resolution_task]
        )
        
        final_task = Task(
            description=f"""
            {get_final_formatter_task_description()}
            
            Use the outputs from the triage analysis, policy retrieval, resolution draft, and compliance review to produce the final structured output.
            """,
            agent=self.final_formatter_agent,
            expected_output="Structured final ticket resolution output",
            context=[triage_task, policy_task, resolution_task, compliance_task]
        )
        
        # Create crew with sequential process
        crew = Crew(
            agents=[
                self.triage_agent,
                self.policy_retriever_agent,
                self.resolution_writer_agent,
                self.compliance_agent,
                self.final_formatter_agent
            ],
            tasks=[
                triage_task,
                policy_task,
                resolution_task,
                compliance_task,
                final_task
            ],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the crew
        print("\nStarting agent workflow...\n")
        result = crew.kickoff()
        
        # Check compliance status
        compliance_output_str = str(compliance_task.output)
        
        # Check for escalation (valid response when not in policy)
        if "ESCALATION_APPROVED" in compliance_output_str or "STATUS: ESCALATED" in compliance_output_str:
            print("\n" + "="*60)
            print("✓ REQUEST ESCALATED TO HUMAN REVIEW")
            print("="*60)
            print("\nThis request is not covered by existing policies.")
            print("Escalation to specialized support team approved.")
            print("="*60)
            
            return {
                'status': 'ESCALATED',
                'reason': 'Request not covered by existing policies',
                'final_output': result,
                'triage_output': triage_task.output,
                'policy_output': policy_task.output,
                'resolution_output': resolution_task.output,
                'compliance_output': compliance_task.output
            }
        
        # Check for compliance failure
        if "COMPLIANCE_FAILED" in compliance_output_str or "REJECTED" in compliance_output_str:
            print("\n" + "="*60)
            print("⚠️  COMPLIANCE CHECK FAILED - RUN BLOCKED")
            print("="*60)
            print("\nThe response did not pass compliance verification.")
            print("Issues found:")
            print(compliance_output_str)
            print("\n" + "="*60)
            
            return {
                'status': 'FAILED',
                'reason': 'Compliance check failed',
                'final_output': 'Response blocked due to compliance issues. Human review required.',
                'triage_output': triage_task.output,
                'policy_output': policy_task.output,
                'resolution_output': resolution_task.output,
                'compliance_output': compliance_task.output
            }
        
        print("\n" + "="*60)
        print("Ticket Processing Complete")
        print("="*60)
        
        return {
            'status': 'SUCCESS',
            'final_output': result,
            'triage_output': triage_task.output,
            'policy_output': policy_task.output,
            'resolution_output': resolution_task.output,
            'compliance_output': compliance_task.output
        }


def process_support_ticket(ticket: Union[str, SupportTicketInput, Dict], order_context: Optional[OrderContext] = None) -> Dict:
    """
    Convenience function to process a single support ticket.
    
    Args:
        ticket: Customer support ticket (str, SupportTicketInput, or dict)
        order_context: Optional structured order information
        
    Returns:
        Dict with results from all agents
    """
    crew = SupportTicketCrew()
    return crew.process_ticket(ticket, order_context)
