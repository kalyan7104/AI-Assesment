"""
Example usage of the support ticket system with structured input.
Demonstrates both simple text input and structured JSON input with order context.
"""
import json
from src.models.input_models import SupportTicketInput, OrderContext
from src.orchestration.crew import process_support_ticket


# Example 1: Simple text-only input (backward compatible)
def example_text_only():
    """Process a ticket with just text."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Text-Only Input (Backward Compatible)")
    print("="*70)
    
    ticket_text = "My order arrived late and the cookies are melted. I want a full refund and to keep the item."
    
    result = process_support_ticket(ticket_text)
    print("\n✓ Processed successfully")


# Example 2: Text + Order Context (using objects)
def example_with_order_context():
    """Process a ticket with structured order context."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Text + Order Context (Structured)")
    print("="*70)
    
    ticket_text = "My order arrived late and the cookies are melted. I want a full refund and to keep the item."
    
    order_context = OrderContext(
        order_id="ORD-12345",
        order_date="2024-01-15",
        delivery_date="2024-01-20",
        item_category="perishable",
        fulfillment_type="first_party",
        shipping_region="US-CA",
        order_status="delivered",
        order_total=49.99,
        shipping_method="standard"
    )
    
    result = process_support_ticket(ticket_text, order_context)
    print("\n✓ Processed successfully")


# Example 3: Complete JSON input
def example_json_input():
    """Process a ticket from JSON format."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Complete JSON Input")
    print("="*70)
    
    ticket_json = {
        "ticket_text": "I received the wrong item. I ordered a blue shirt size M but got a red shirt size L.",
        "order_context": {
            "order_id": "ORD-67890",
            "order_date": "2024-01-10",
            "delivery_date": "2024-01-18",
            "item_category": "apparel",
            "fulfillment_type": "marketplace_seller",
            "shipping_region": "US-NY",
            "order_status": "delivered",
            "order_total": 29.99,
            "shipping_method": "express"
        }
    }
    
    # Can pass dict directly
    result = process_support_ticket(ticket_json)
    print("\n✓ Processed successfully")


# Example 4: Using SupportTicketInput object
def example_ticket_input_object():
    """Process using SupportTicketInput object."""
    print("\n" + "="*70)
    print("EXAMPLE 4: SupportTicketInput Object")
    print("="*70)
    
    ticket_input = SupportTicketInput(
        ticket_text="My package shows delivered but I never received it. Can you help?",
        order_context=OrderContext(
            order_id="ORD-11111",
            order_date="2024-01-12",
            delivery_date="2024-01-19",
            item_category="electronics",
            fulfillment_type="first_party",
            shipping_region="US-TX",
            order_status="delivered",
            order_total=299.99,
            shipping_method="overnight",
            tracking_number="1Z999AA10123456784"
        )
    )
    
    result = process_support_ticket(ticket_input)
    print("\n✓ Processed successfully")


# Example 5: Minimal order context (only required fields)
def example_minimal_context():
    """Process with minimal order information."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Minimal Order Context")
    print("="*70)
    
    ticket_json = {
        "ticket_text": "The item I received is defective. The screen has dead pixels.",
        "order_context": {
            "order_date": "2024-01-05",
            "item_category": "electronics",
            "fulfillment_type": "first_party",
            "order_status": "delivered"
        }
    }
    
    result = process_support_ticket(ticket_json)
    print("\n✓ Processed successfully")


# Example 6: Load from JSON file
def example_from_json_file():
    """Process tickets from a JSON file."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Load from JSON File")
    print("="*70)
    
    # Example JSON structure for batch processing
    tickets_data = [
        {
            "ticket_text": "I want to cancel my order before it ships.",
            "order_context": {
                "order_id": "ORD-22222",
                "order_date": "2024-01-20",
                "item_category": "home_goods",
                "fulfillment_type": "first_party",
                "shipping_region": "US-FL",
                "order_status": "processing",
                "order_total": 89.99
            }
        },
        {
            "ticket_text": "Can I use my 20% off coupon on this order?",
            "order_context": {
                "order_id": "ORD-33333",
                "order_date": "2024-01-21",
                "item_category": "toys",
                "fulfillment_type": "first_party",
                "shipping_region": "US-WA",
                "order_status": "placed",
                "order_total": 150.00
            }
        }
    ]
    
    print(f"\nProcessing {len(tickets_data)} tickets from batch...")
    
    for i, ticket_data in enumerate(tickets_data, 1):
        print(f"\n--- Processing Ticket {i}/{len(tickets_data)} ---")
        result = process_support_ticket(ticket_data)
        print(f"✓ Ticket {i} processed")


def print_input_format_documentation():
    """Print documentation for the input format."""
    print("\n" + "="*70)
    print("INPUT FORMAT DOCUMENTATION")
    print("="*70)
    
    print("\n1. TEXT-ONLY INPUT (Simple):")
    print("-" * 70)
    print('process_support_ticket("My order is late")')
    
    print("\n2. TEXT + ORDER CONTEXT (Structured):")
    print("-" * 70)
    print('''
ticket = "My order is late"
context = OrderContext(
    order_id="ORD-12345",
    order_date="2024-01-15",
    delivery_date="2024-01-20",
    item_category="perishable",
    fulfillment_type="first_party",
    shipping_region="US-CA",
    order_status="delivered"
)
process_support_ticket(ticket, context)
''')
    
    print("\n3. JSON INPUT (API-friendly):")
    print("-" * 70)
    print('''
ticket_json = {
    "ticket_text": "My order is late",
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
process_support_ticket(ticket_json)
''')
    
    print("\n4. REQUIRED FIELDS:")
    print("-" * 70)
    print("  ticket_text: str (REQUIRED)")
    print("  order_context: dict (OPTIONAL)")
    
    print("\n5. ORDER CONTEXT FIELDS (All Optional):")
    print("-" * 70)
    print("  - order_id: str")
    print("  - order_date: str (YYYY-MM-DD)")
    print("  - delivery_date: str (YYYY-MM-DD)")
    print("  - item_category: perishable|apparel|electronics|home_goods|toys|books|other")
    print("  - fulfillment_type: first_party|marketplace_seller")
    print("  - shipping_region: str (e.g., US-CA, UK, EU)")
    print("  - order_status: placed|processing|shipped|in_transit|out_for_delivery|delivered|returned|cancelled")
    print("  - order_total: float")
    print("  - shipping_method: str")
    print("  - tracking_number: str")
    print("  - customer_id: str")


if __name__ == "__main__":
    # Print documentation
    print_input_format_documentation()
    
    # Run examples (uncomment to test)
    # example_text_only()
    # example_with_order_context()
    # example_json_input()
    # example_ticket_input_object()
    # example_minimal_context()
    # example_from_json_file()
