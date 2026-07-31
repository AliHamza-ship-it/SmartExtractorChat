import re
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

# --- Auth Schemas ---
class UserRegister(BaseModel):
    name: str
    email: str
    age: int = Field(gt=0)
    country: str
    password: str

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter.')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character.')
        return v

class OTPVerify(BaseModel):
    email: str
    otp: str

class UserLogin(BaseModel):
    email: str
    password: str

# --- Chat Schemas ---
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    system_prompt: Optional[str] = "AI Tech Mentor"
    custom_system_prompt: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    session_id: Optional[str] = None

class CreateSessionRequest(BaseModel):
    system_prompt: str = "AI Tech Mentor"
    title: Optional[str] = "New Chat"

# --- Invoice Extraction Schemas ---
class LineItem(BaseModel):
    description: str
    quantity: int = 1
    unit_price: float = 0.0
    total_price: float = 0.0

class InvoiceData(BaseModel):
    invoice_number: Optional[str] = None
    vendor_name: str
    client_name: Optional[str] = None
    date: Optional[str] = None
    items: List[LineItem] = Field(default_factory=list)
    subtotal: Optional[float] = 0.0
    tax: Optional[float] = 0.0
    total_amount: float
    currency: str = "USD"

class ExtractRequest(BaseModel):
    raw_text: str

class ExtractResponse(BaseModel):
    success: bool
    data: Optional[InvoiceData] = None
    attempts: int
    tokens_used: dict
    estimated_cost: float
    error: Optional[str] = None