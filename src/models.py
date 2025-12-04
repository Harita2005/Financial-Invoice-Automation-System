from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, validator
from decimal import Decimal

class InvoiceItem(BaseModel):
    description: str
    quantity: int
    unit_price: Decimal
    
    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v
    
    @validator('unit_price')
    def unit_price_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Unit price cannot be negative')
        return v
    
    @property
    def total(self) -> Decimal:
        return self.quantity * self.unit_price

class Customer(BaseModel):
    name: str
    email: str
    address: str
    phone: Optional[str] = None
    
    @validator('email')
    def email_must_contain_at(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v

class Invoice(BaseModel):
    invoice_number: str
    customer: Customer
    items: List[InvoiceItem]
    issue_date: datetime
    due_date: datetime
    tax_rate: Decimal = Decimal('0.08')
    discount_rate: Decimal = Decimal('0.00')
    notes: Optional[str] = None
    
    @validator('items')
    def items_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Invoice must have at least one item')
        return v
    
    @validator('due_date')
    def due_date_must_be_after_issue_date(cls, v, values):
        if 'issue_date' in values and v < values['issue_date']:
            raise ValueError('Due date must be after issue date')
        return v
    
    @property
    def subtotal(self) -> Decimal:
        return sum(item.total for item in self.items)
    
    @property
    def discount_amount(self) -> Decimal:
        return self.subtotal * self.discount_rate
    
    @property
    def taxable_amount(self) -> Decimal:
        return self.subtotal - self.discount_amount
    
    @property
    def tax_amount(self) -> Decimal:
        return self.taxable_amount * self.tax_rate
    
    @property
    def total_amount(self) -> Decimal:
        return self.taxable_amount + self.tax_amount