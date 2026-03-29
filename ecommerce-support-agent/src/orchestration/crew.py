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
    
    def process_ticket(self, ticket: Union[str, SupportTicketInput, Dict], order_context: Optional[OrderContext] = None, max_retries: int = 2) -> Dict:
        """
        Process a customer support ticket through all agents with retry loop.
        
        Args:
            ticket: The customer support ticket (str, SupportTicketInput, or dict)
            order_context: Optional structured order information
            max_retries: Maximum number of retry attempts for compliance failures
            
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
        
        # Task 1: Triage (runs once)
        triage_task = Task(
            description=f"""
            {get_triage_task_description()}
            
            {formatted_input}
            """,
            agent=self.triage_agent,
            expected_output="Structured triage analysis with issue category, missing information, and next steps"
        )
        
        # Task 2: Policy Retrieval (runs once)
        policy_task = Task(
            description=f"""
            {get_policy_retrieval_task_description()}
            
            Use the triage analysis to search for relevant policies.
            """,
            agent=self.policy_retriever_agent,
            expected_output="Relevant policy information with proper citations (Document ID and Section)",
            context=[triage_task]
        )
        
        # Run triage and policy retrieval once
        initial_crew = Crew(
            agents=[self.triage_agent, self.policy_retriever_agent],
            tasks=[triage_task, policy_task],
            process=Process.sequential,
            verbose=True
        )
        
        print("\n[Phase 1] Running Triage and Policy Retrieval...\n")
        initial_crew.kickoff()
        
        # Retry loop for resolution writing and compliance
        for attempt in range(max_retries + 1):
            print(f"\n[Phase 2 - Attempt {attempt + 1}/{max_retries + 1}] Resolution Writing and Compliance Check...\n")
            
            # Add compliance feedback to resolution task if this is a retry
            compliance_feedback = ""
            if attempt > 0:
                compliance_feedback = f"""
                
                PREVIOUS ATTEMPT FAILED COMPLIANCE:
                {previous_compliance_output}
                
                You MUST fix these issues in your response. Pay special attention to:
                - Add missing citations
                - Remove unsupported claims
                - Fix factual inaccuracies
                """
            
            # Task 3: Resolution Writing
            resolution_task = Task(
                description=f"""
                {get_resolution_writer_task_description()}
                
                {formatted_input}
                
                Use the triage analysis and retrieved policies to write the response.
                {compliance_feedback}
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
                """,
                agent=self.compliance_agent,
                expected_output="Compliance review with approval status and any required corrections",
                context=[triage_task, policy_task, resolution_task]
            )
            
            # Run resolution and compliance
            retry_crew = Crew(
                agents=[self.resolution_writer_agent, self.compliance_agent],
                tasks=[resolution_task, compliance_task],
                process=Process.sequential,
                verbose=True
            )
            
            retry_crew.kickoff()
            
            # Check compliance status
            compliance_output_str = str(compliance_task.output)
            
            # Check for escalation
            if "ESCALATION_APPROVED" in compliance_output_str or "STATUS: ESCALATED" in compliance_output_str:
                print("\n" + "="*60)
                print("✓ REQUEST ESCALATED TO HUMAN REVIEW")
                print("="*60)
                break
            
            # Check for compliance failure
            if "COMPLIANCE_FAILED" in compliance_output_str or "REJECTED" in compliance_output_str:
                if attempt < max_retries:
                    print(f"\n⚠️  Compliance failed on attempt {attempt + 1}. Retrying...")
                    previous_compliance_output = compliance_output_str
                    continue
                else:
                    print("\n" + "="*60)
                    print("⚠️  COMPLIANCE CHECK FAILED - MAX RETRIES REACHED")
                    print("="*60)
                    print("\nThe response did not pass compliance after multiple attempts.")
                    print("Issues found:")
                    print(compliance_output_str)
                    print("\n" + "="*60)
                    
                    return {
                        'status': 'FAILED',
                        'reason': 'Compliance check failed after retries',
                        'final_output': 'Response blocked due to compliance issues. Human review required.',
                        'triage_output': triage_task.output,
                        'policy_output': policy_task.output,
                        'resolution_output': resolution_task.output,
                        'compliance_output': compliance_task.output,
                        'attempts': attempt + 1
                    }
            else:
                # Compliance passed!
                print(f"\n✓ Compliance passed on attempt {attempt + 1}")
                break
        
        # Final formatting
        print("\n[Phase 3] Final Formatting...\n")
        
        final_task = Task(
            description=f"""
            {get_final_formatter_task_description()}
            
            Use the outputs from the triage analysis, policy retrieval, resolution draft, and compliance review to produce the final structured output.
            """,
            agent=self.final_formatter_agent,
            expected_output="Structured final ticket resolution output",
            context=[triage_task, policy_task, resolution_task, compliance_task]
        )
        
        final_crew = Crew(
            agents=[self.final_formatter_agent],
            tasks=[final_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = final_crew.kickoff()
        
        # Determine final status
        compliance_output_str = str(compliance_task.output)
        
        if "ESCALATION_APPROVED" in compliance_output_str or "STATUS: ESCALATED" in compliance_output_str:
            status = 'ESCALATED'
            reason = 'Request not covered by existing policies'
        else:
            status = 'SUCCESS'
            reason = 'Processed successfully'
        
        print("\n" + "="*60)
        print("Ticket Processing Complete")
        print("="*60)
        
        return {
            'status': status,
            'reason': reason,
            'final_output': result,
            'triage_output': triage_task.output,
            'policy_output': policy_task.output,
            'resolution_output': resolution_task.output,
            'compliance_output': compliance_task.output,
            'attempts': attempt + 1
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
