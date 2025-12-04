#!/usr/bin/env python3
"""
Create a sample invoice to demonstrate the system
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.invoice_generator import InvoiceGenerator
from src.models import Invoice, Customer, InvoiceItem

def create_sample_invoice():
    """Create a sample invoice for demonstration"""
    
    # Create sample customer
    customer = Customer(
        name="Acme Corporation",
        email="billing@acme.com",
        address="123 Business Avenue\nNew York, NY 10001\nUnited States",
        phone="+1 (555) 123-4567"
    )
    
    # Create sample items
    items = [
        InvoiceItem(
            description="Web Development Services",
            quantity=40,
            unit_price=Decimal('125.00')
        ),
        InvoiceItem(
            description="Domain Registration (Annual)",
            quantity=1,
            unit_price=Decimal('15.99')
        ),
        InvoiceItem(
            description="SSL Certificate",
            quantity=1,
            unit_price=Decimal('89.99')
        ),
        InvoiceItem(
            description="Technical Support Hours",
            quantity=8,
            unit_price=Decimal('75.00')
        )
    ]
    
    # Create invoice
    invoice = Invoice(
        invoice_number="INV-2024-SAMPLE-001",
        customer=customer,
        items=items,
        issue_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=30),
        tax_rate=Decimal('0.08'),
        discount_rate=Decimal('0.05'),
        notes="Thank you for choosing our services. Payment is due within 30 days."
    )
    
    return invoice

def main():
    """Generate sample invoice"""
    try:
        print("Creating sample invoice...")
        
        # Create invoice object
        invoice = create_sample_invoice()
        
        # Initialize generator
        generator = InvoiceGenerator('config/settings.json')
        
        # Generate PDF (without saving to database)
        pdf_path = generator.get_invoice_preview(invoice)
        
        print(f"Sample invoice created successfully!")
        print(f"PDF saved to: {pdf_path}")
        print(f"Invoice total: Rs.{invoice.total_amount:.2f}")
        print(f"Customer: {invoice.customer.name}")
        print(f"Due date: {invoice.due_date.strftime('%Y-%m-%d')}")
        
        # Print invoice summary
        print("\nInvoice Summary:")
        print(f"   Subtotal: Rs.{invoice.subtotal:.2f}")
        if invoice.discount_rate > 0:
            print(f"   Discount ({invoice.discount_rate*100:.1f}%): -Rs.{invoice.discount_amount:.2f}")
        print(f"   GST ({invoice.tax_rate*100:.1f}%): Rs.{invoice.tax_amount:.2f}")
        print(f"   Total: Rs.{invoice.total_amount:.2f}")
        
        print(f"\nOpen the PDF file to see the professional invoice layout!")
        
    except Exception as e:
        print(f"Error creating sample invoice: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())