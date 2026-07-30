from pydantic import BaseModel, Field
from typing import List, Optional

# Chat Schemas
class ChatMessage(BaseModel):
    role: str  # "user", "assistant", or "system"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    system_prompt: Optional[str] = "AI Tech Mentor"
    custom_system_prompt: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    session_id: Optional[str] = None  # Added for Supabase linking

class CreateSessionRequest(BaseModel):
    system_prompt: str = "AI Tech Mentor"
    title: Optional[str] = "New Chat"

# Invoice Extraction Schemas
class LineItem(BaseModel):
    description: str = Field(description="Description of the item or service")
    quantity: int = Field(default=1, description="Quantity of items")
    unit_price: float = Field(default=0.0, description="Price per unit")
    total_price: float = Field(default=0.0, description="Total cost for this item line")

class InvoiceData(BaseModel):
    invoice_number: Optional[str] = Field(default=None, description="Invoice or receipt reference number")
    vendor_name: str = Field(description="Name of the company/vendor issuing invoice")
    client_name: Optional[str] = Field(default=None, description="Client or customer name")
    date: Optional[str] = Field(default=None, description="Date of invoice")
    items: List[LineItem] = Field(default_factory=list, description="List of items billed")
    subtotal: Optional[float] = Field(default=0.0, description="Subtotal amount before tax")
    tax: Optional[float] = Field(default=0.0, description="Tax amount")
    total_amount: float = Field(description="Final total monetary amount")
    currency: str = Field(default="USD", description="Currency symbol or code")

class ExtractRequest(BaseModel):
    raw_text: str

class ExtractResponse(BaseModel):
    success: bool
    data: Optional[InvoiceData] = None
    attempts: int
    tokens_used: dict
    estimated_cost: float
    error: Optional[str] = None