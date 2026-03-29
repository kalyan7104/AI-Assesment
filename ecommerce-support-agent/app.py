"""
Gradio UI for E-commerce Support Agent System
"""
import os
import gradio as gr
from datetime import datetime
from dotenv import load_dotenv
from src.orchestration.crew import process_support_ticket

load_dotenv()


def clean_html_entities(text):
    """Clean HTML entities from text."""
    if not text:
        return text
    text = str(text)
    text = text.replace('&quot;', '"')
    text = text.replace('&gt;', '>')
    text = text.replace('&lt;', '<')
    text = text.replace('&#39;', "'")
    text = text.replace('&amp;', '&')
    return text


def process_ticket_ui(ticket_text, order_id="", order_date="", item_category="", order_total=""):
    """Process ticket through the agent system."""
    
    if not ticket_text or not ticket_text.strip():
        return "❌ Please enter a customer ticket", "", "", ""
    
    try:
        ticket_data = {"ticket_text": ticket_text.strip()}
        
        if order_id or order_date or item_category or order_total:
            order_context = {}
            if order_id:
                order_context["order_id"] = order_id
            if order_date:
                order_context["order_date"] = order_date
            if item_category:
                order_context["item_category"] = item_category
            if order_total:
                try:
                    order_context["order_total"] = float(order_total)
                except:
                    pass
            
            if order_context:
                ticket_data["order_context"] = order_context
        
        result = process_support_ticket(ticket_data)
        
        status = result.get('status', 'SUCCESS')
        final_output = clean_html_entities(str(result.get('final_output', '')))
        
        # Extract SECTION 6 - CUSTOMER RESPONSE DRAFT
        customer_section = ""
        internal_section = ""
        
        if "SECTION 6" in final_output:
            start_marker = "SECTION 6 — CUSTOMER RESPONSE DRAFT"
            end_marker = "SECTION 7 — NEXT STEPS"
            
            start_idx = final_output.find(start_marker)
            end_idx = final_output.find(end_marker)
            
            if start_idx > 0:
                if end_idx > start_idx:
                    customer_section = final_output[start_idx:end_idx].replace(start_marker, "").strip()
                else:
                    customer_section = final_output[start_idx:].replace(start_marker, "").strip()
                
                # Remove dashes
                if customer_section.startswith("-" * 60):
                    customer_section = customer_section[64:].strip()
                
                internal_section = final_output[:start_idx] + (final_output[end_idx:] if end_idx > 0 else "")
        else:
            customer_section = final_output
            internal_section = final_output
        
        if status == 'ESCALATED':
            status_msg = "⚠️ ESCALATED TO HUMAN REVIEW"
        elif status == 'FAILED':
            status_msg = "❌ COMPLIANCE FAILED"
        else:
            status_msg = "✅ PROCESSED SUCCESSFULLY"
        
        return status_msg, internal_section, customer_section, final_output
    
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        return error_msg, str(e), str(e), str(e)


def create_ui():
    """Create Gradio interface."""
    
    with gr.Blocks(title="E-commerce Support Agent") as demo:
        
        gr.Markdown("""
        # 🎯 E-commerce Support Agent System
        ### Multi-Agent RAG System with Anti-Hallucination Controls
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📝 Customer Ticket")
                
                ticket_input = gr.Textbox(
                    label="Customer Message",
                    placeholder="Enter customer support ticket...",
                    lines=6
                )
                
                gr.Markdown("### 📦 Order Context (Optional)")
                
                with gr.Row():
                    order_id = gr.Textbox(label="Order ID", placeholder="ORD-12345")
                    order_date = gr.Textbox(label="Order Date", placeholder="2024-01-15")
                
                with gr.Row():
                    item_category = gr.Dropdown(
                        label="Item Category",
                        choices=["", "perishable", "apparel", "electronics", "home_goods", "toys", "books", "other"],
                        value=""
                    )
                    order_total = gr.Textbox(label="Order Total ($)", placeholder="49.99")
                
                process_btn = gr.Button("🚀 Process Ticket", variant="primary", size="lg")
        
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Results")
                
                status_output = gr.Textbox(label="Status", lines=1, interactive=False)
                
                with gr.Tabs():
                    with gr.Tab("👤 Customer Response"):
                        customer_output = gr.Textbox(
                            label="Customer-Facing Message",
                            lines=15,
                            interactive=False
                        )
                    
                    with gr.Tab("🔍 Internal Analysis"):
                        internal_output = gr.Textbox(
                            label="Internal Analysis",
                            lines=15,
                            interactive=False
                        )
                    
                    with gr.Tab("📄 Full Output"):
                        full_output = gr.Textbox(
                            label="Complete Output",
                            lines=15,
                            interactive=False
                        )
        
        gr.Examples(
            examples=[
                ["My order #12345 arrived late and the cookies are melted. I want a full refund.", "ORD-12345", "2024-01-15", "perishable", "49.99"],
                ["I received the wrong item. I ordered a blue shirt but got red.", "ORD-67890", "2024-01-10", "apparel", "29.99"],
            ],
            inputs=[ticket_input, order_id, order_date, item_category, order_total]
        )
        
        process_btn.click(
            fn=process_ticket_ui,
            inputs=[ticket_input, order_id, order_date, item_category, order_total],
            outputs=[status_output, internal_output, customer_output, full_output]
        )
    
    return demo


def main():
    """Launch the UI."""
    
    provider = os.getenv("LLM_PROVIDER", "google").lower()
    if provider == "google":
        if not os.getenv("GOOGLE_API_KEY"):
            print("\n❌ ERROR: Google API key not configured!")
            return
    elif provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            print("\n❌ ERROR: OpenAI API key not configured!")
            return
    elif provider == "groq":
        if not os.getenv("GROQ_API_KEY"):
            print("\n❌ ERROR: Groq API key not configured!")
            return
    else:
        print(f"\n❌ ERROR: Unsupported provider: {provider}. Use 'openai' or 'google'")
        return
    
    print("\n🚀 Launching UI...")
    
    demo = create_ui()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )


if __name__ == "__main__":
    main()
