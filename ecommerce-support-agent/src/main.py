"""
Main entry point for the E-commerce Support Agent system.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.orchestration.crew import process_support_ticket


def print_header():
    """Print application header."""
    print("\n" + "="*70)
    print(" "*15 + "E-COMMERCE SUPPORT AGENT SYSTEM")
    print(" "*20 + "Multi-Agent RAG System")
    print("="*70)


def print_result(result: dict):
    """Print the final result in a formatted way."""
    print("\n" + "="*70)
    print("TICKET RESOLUTION")
    print("="*70)
    
    # Check status
    status = result.get('status', 'SUCCESS')
    
    if status == 'ESCALATED':
        print("\n⚠️  STATUS: ESCALATED TO HUMAN REVIEW")
        print("Reason:", result.get('reason', 'Not covered by policy'))
        print("\n" + "-"*70)
    elif status == 'FAILED':
        print("\n❌ STATUS: COMPLIANCE FAILED")
        print("Reason:", result.get('reason', 'Compliance issues detected'))
        print("\n" + "-"*70)
    else:
        print("\n✓ STATUS: PROCESSED")
        print("-"*70)
    
    # Print the final output
    final_output = str(result['final_output'])
    
    # Clean up any HTML entities that might have slipped through
    final_output = final_output.replace('&quot;', '"')
    final_output = final_output.replace('&gt;', '>')
    final_output = final_output.replace('&lt;', '<')
    final_output = final_output.replace('&#39;', "'")
    final_output = final_output.replace('&amp;', '&')
    
    print(final_output)
    print("="*70)


def run_example_tickets():
    """Run some example support tickets with structured input."""
    
    example_tickets = [
        {
            "title": "Damaged Electronics - Marketplace Seller",
            "ticket_data": {
                "ticket_text": "I received my order #67890 yesterday and the laptop I ordered arrived with a cracked screen. The box was damaged when it arrived. I'd like to return it for a full refund. I paid $899.99 for it.",
                "order_context": {
                    "order_id": "ORD-67890",
                    "order_date": "2024-01-10",
                    "delivery_date": "2024-01-18",
                    "item_category": "electronics",
                    "fulfillment_type": "marketplace_seller",
                    "shipping_region": "US-NY",
                    "order_status": "delivered",
                    "order_total": 899.99,
                    "shipping_method": "express"
                }
            }
        },
        {
            "title": "Shipping Delay Question",
            "ticket_data": {
                "ticket_text": "Hi, I placed an order 5 days ago (order #11111) and selected standard shipping. The tracking hasn't updated in 3 days and just says 'in transit'. When should I expect my package? I need it by next week.",
                "order_context": {
                    "order_id": "ORD-11111",
                    "order_date": "2024-01-15",
                    "shipping_region": "US-TX",
                    "order_status": "in_transit",
                    "shipping_method": "standard",
                    "tracking_number": "1Z999AA10123456784"
                }
            }
        },
        {
            "title": "Perishable Item Damage",
            "ticket_data": {
                "ticket_text": "My order arrived late and the cookies are melted. I want a full refund and to keep the item.",
                "order_context": {
                    "order_id": "ORD-12345",
                    "order_date": "2024-01-15",
                    "delivery_date": "2024-01-20",
                    "item_category": "perishable",
                    "fulfillment_type": "first_party",
                    "shipping_region": "US-CA",
                    "order_status": "delivered",
                    "order_total": 49.99,
                    "shipping_method": "standard"
                }
            }
        },
        {
            "title": "Coupon Code Not Working",
            "ticket_data": {
                "ticket_text": "I'm trying to use the coupon code SAVE20 but it says it's invalid. The email I received said it's valid until the end of this month. My cart total is $150. Can you help me apply this discount?"
                # No order context - testing minimal input
            }
        }
    ]
    
    print("\nRunning example support tickets with structured input...\n")
    
    # Test with the first ticket (you can change index to test others)
    example = example_tickets[2]  # Perishable item example
    print(f"\n{'='*70}")
    print(f"EXAMPLE: {example['title']}")
    print(f"{'='*70}")
    
    # Process the ticket with structured input
    result = process_support_ticket(example['ticket_data'])
    
    # Print result
    print_result(result)


def run_interactive_mode():
    """Run in interactive mode for custom tickets."""
    print("\n" + "="*70)
    print("INTERACTIVE MODE")
    print("="*70)
    print("Enter a customer support ticket (or 'quit' to exit)")
    print("Type 'examples' to run example tickets")
    print("-"*70)
    
    while True:
        print("\nEnter ticket (or command):")
        ticket = input("> ").strip()
        
        if ticket.lower() == 'quit':
            print("\nGoodbye!")
            break
        
        if ticket.lower() == 'examples':
            run_example_tickets()
            continue
        
        if not ticket:
            print("Please enter a ticket or command.")
            continue
        
        # Process the ticket
        result = process_support_ticket(ticket)
        
        # Print result
        print_result(result)


def main():
    """Main function."""
    # Load environment variables
    load_dotenv()
    
    # Check for API key based on provider
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "google":
        if not os.getenv("GOOGLE_API_KEY"):
            print("\n❌ ERROR: Google API key not configured!")
            print("Please set GOOGLE_API_KEY in your .env file")
            return
    elif provider == "openai":
        if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
            print("\n❌ ERROR: OpenAI API key not configured!")
            print("Please set OPENAI_API_KEY in your .env file")
            return
    elif provider == "groq":
        if not os.getenv("GROQ_API_KEY"):
            print("\n❌ ERROR: Groq API key not configured!")
            print("Please set GROQ_API_KEY in your .env file")
            return
    else:
        print(f"\n❌ ERROR: Unsupported provider: {provider}. Use 'openai', 'google', or 'groq'")
        return
    
    # Check if vector store exists
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    if not Path(persist_dir).exists():
        print("\n❌ ERROR: Vector store not found!")
        print("Please run the ingestion pipeline first:")
        print("  python src/ingestion/pipeline.py")
        return
    
    # Print header
    print_header()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--examples':
            run_example_tickets()
        elif sys.argv[1] == '--ticket':
            if len(sys.argv) > 2:
                ticket = ' '.join(sys.argv[2:])
                result = process_support_ticket(ticket)
                print_result(result)
            else:
                print("Usage: python src/main.py --ticket 'Your ticket text here'")
        else:
            print("Usage:")
            print("  python src/main.py                    # Interactive mode")
            print("  python src/main.py --examples         # Run example tickets")
            print("  python src/main.py --ticket 'text'    # Process single ticket")
    else:
        # Interactive mode
        run_interactive_mode()


if __name__ == "__main__":
    main()
