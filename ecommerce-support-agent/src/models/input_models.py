"""
Input models for the support ticket system.
Defines structured formats for ticket and order context.
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class OrderContext(BaseModel):
    """Structured order context information."""
    
    order_id: Optional[str] = Field(None, description="Order identifier (e.g., ORD-12345)")
    order_date: Optional[str] = Field(None, description="Date order was placed (YYYY-MM-DD)")
    delivery_date: Optional[str] = Field(None, description="Date order was/will be delivered (YYYY-MM-DD)")
    
    item_category: Optional[Literal[
        "perishable",
        "apparel", 
        "electronics",
        "home_goods",
        "toys",
        "books",
        "other"
    ]] = Field(None, description="Category of the ordered item")
    
    fulfillment_type: Optional[Literal[
        "first_party",
        "marketplace_seller"
    ]] = Field(None, description="Who fulfills the order")
    
    shipping_region: Optional[str] = Field(None, description="Shipping destination (e.g., US-CA, UK, EU)")
    
    order_status: Optional[Literal[
        "placed",
        "processing",
        "shipped",
        "in_transit",
        "out_for_delivery",
        "delivered",
        "returned",
        "cancelled"
    ]] = Field(None, description="Current order status")
    
    # Additional optional fields
    order_total: Optional[float] = Field(None, description="Total order amount in USD")
    shipping_method: Optional[str] = Field(None, description="Shipping method (standard/express/overnight)")
    tracking_number: Optional[str] = Field(None, description="Shipping tracking number")
    customer_id: Optional[str] = Field(None, description="Customer identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
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


class SupportTicketInput(BaseModel):
    """Complete support ticket input with text and optional order context."""
    
    ticket_text: str = Field(..., description="Free-form customer support ticket text")
    order_context: Optional[OrderContext] = Field(None, description="Structured order information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticket_text": "My order arrived late and the cookies are melted. I want a full refund and to keep the item.",
                "order_context": {
                    "order_id": "ORD-12345",
                    "order_date": "2024-01-15",
                    "delivery_date": "2024-01-20",
                    "item_category": "perishable",
                    "fulfillment_type": "first_party",
                    "shipping_region": "US-CA",
                    "order_status": "delivered"
                }
            }
        }
    
    def format_for_agents(self) -> str:
        """Format the input for agent consumption."""
        output = [f"CUSTOMER TICKET:\n{self.ticket_text}"]
        
        if self.order_context:
            output.append("\nORDER CONTEXT:")
            
            if self.order_context.order_id:
                output.append(f"  Order ID: {self.order_context.order_id}")
            if self.order_context.order_date:
                output.append(f"  Order Date: {self.order_context.order_date}")
            if self.order_context.delivery_date:
                output.append(f"  Delivery Date: {self.order_context.delivery_date}")
            if self.order_context.item_category:
                output.append(f"  Item Category: {self.order_context.item_category}")
            if self.order_context.fulfillment_type:
                output.append(f"  Fulfillment Type: {self.order_context.fulfillment_type}")
            if self.order_context.shipping_region:
                output.append(f"  Shipping Region: {self.order_context.shipping_region}")
            if self.order_context.order_status:
                output.append(f"  Order Status: {self.order_context.order_status}")
            if self.order_context.order_total:
                output.append(f"  Order Total: ${self.order_context.order_total:.2f}")
            if self.order_context.shipping_method:
                output.append(f"  Shipping Method: {self.order_context.shipping_method}")
            if self.order_context.tracking_number:
                output.append(f"  Tracking Number: {self.order_context.tracking_number}")
        
        return "\n".join(output)
