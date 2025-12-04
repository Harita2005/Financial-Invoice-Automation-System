#!/usr/bin/env python3
"""
Create invoices without database - standalone version
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models import Invoice, Customer, InvoiceItem
from src.pdf_generator import PDFGenerator
from src.config_manager import ConfigManager

def create_sample_invoices():
    """Create multiple sample invoices without database"""
    
    # Initialize components
    config_manager = ConfigManager('config/settings.json')
    pdf_generator = PDFGenerator(config_manager)
    
    # Sample customers
    customers = [
        Customer(
            name="Acme Corporation",
            email="billing@acme.com",
            address="123 Business Avenue\nMumbai, Maharashtra 400001\nIndia",
            phone="+91 98765 43210"
        ),
        Customer(
            name="Tech Solutions Pvt Ltd",
            email="accounts@techsolutions.in",
            address="456 Innovation Drive\nBangalore, Karnataka 560001\nIndia",
            phone="+91 87654 32109"
        ),
        Customer(
            name="Global Services India",
            email="finance@globalservices.in",
            address="789 Commerce Street\nDelhi, Delhi 110001\nIndia",
            phone="+91 76543 21098"
        )
    ]
    
    # Sample invoice data
    invoice_data = [
        {
            "customer": customers[0],
            "items": [
                InvoiceItem(description="Web Development Services", quantity=40, unit_price=Decimal('2500.00')),
                InvoiceItem(description="Domain Registration (Annual)", quantity=1, unit_price=Decimal('1200.00')),
                InvoiceItem(description="SSL Certificate", quantity=1, unit_price=Decimal('3500.00')),
                InvoiceItem(description="Technical Support Hours", quantity=8, unit_price=Decimal('1500.00'))
            ],
            "notes": "Thank you for choosing our services. Payment due within 30 days."
        },
        {
            "customer": customers[1],
            "items": [
                InvoiceItem(description="Software License (Annual)", quantity=5, unit_price=Decimal('15000.00')),
                InvoiceItem(description="Implementation Services", quantity=12, unit_price=Decimal('5000.00')),
                InvoiceItem(description="Training Sessions", quantity=3, unit_price=Decimal('8000.00'))
            ],
            "notes": "Bulk discount applied. GST included as per Indian tax regulations."
        },
        {
            "customer": customers[2],
            "items": [
                InvoiceItem(description="Business Consultation", quantity=8, unit_price=Decimal('4000.00')),
                InvoiceItem(description="Market Analysis Report", quantity=1, unit_price=Decimal('25000.00')),
                InvoiceItem(description="Strategy Planning", quantity=4, unit_price=Decimal('7500.00'))
            ],
            "notes": "Consulting services as per agreement dated 15th January 2024."
        }
    ]
    
    generated_invoices = []
    
    for i, data in enumerate(invoice_data, 1):
        # Create invoice
        invoice = Invoice(
            invoice_number=f"INV-2024-{i:03d}",
            customer=data["customer"],
            items=data["items"],
            issue_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            tax_rate=Decimal('0.18'),  # 18% GST
            discount_rate=Decimal('0.05') if i == 2 else Decimal('0.00'),
            notes=data["notes"]
        )
        
        # Generate PDF
        pdf_path = pdf_generator.generate_invoice(invoice)
        generated_invoices.append((invoice, pdf_path))
        
        print(f"Invoice {invoice.invoice_number} generated:")
        print(f"  Customer: {invoice.customer.name}")
        print(f"  Total: Rs.{invoice.total_amount:.2f}")
        print(f"  PDF: {pdf_path}")
        print()
    
    return generated_invoices

def create_custom_invoice():
    """Create a custom invoice with user input"""
    
    config_manager = ConfigManager('config/settings.json')
    pdf_generator = PDFGenerator(config_manager)
    
    print("Create Custom Invoice")
    print("=" * 30)
    
    # Get customer details
    customer_name = input("Customer Name: ").strip()
    customer_email = input("Customer Email: ").strip()
    customer_address = input("Customer Address: ").strip()
    customer_phone = input("Customer Phone (optional): ").strip() or None
    
    customer = Customer(
        name=customer_name,
        email=customer_email,
        address=customer_address,
        phone=customer_phone
    )
    
    # Get invoice details
    invoice_number = input("Invoice Number (or press Enter for auto): ").strip()
    if not invoice_number:
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Get items
    items = []
    print("\nAdd Items (press Enter with empty description to finish):")
    
    while True:
        desc = input("Item Description: ").strip()
        if not desc:
            break
        
        try:
            qty = int(input("Quantity: "))
            price = float(input("Unit Price (Rs.): "))
            
            items.append(InvoiceItem(
                description=desc,
                quantity=qty,
                unit_price=Decimal(str(price))
            ))
            
            print(f"Added: {desc} x {qty} @ Rs.{price:.2f}")
            
        except ValueError:
            print("Invalid quantity or price. Item skipped.")
    
    if not items:
        print("No items added. Invoice not created.")
        return None
    
    # Get optional details
    notes = input("Notes (optional): ").strip() or None
    
    try:
        discount_rate = float(input("Discount % (0 for none): ") or "0") / 100
    except ValueError:
        discount_rate = 0.0
    
    # Create invoice
    invoice = Invoice(
        invoice_number=invoice_number,
        customer=customer,
        items=items,
        issue_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=30),
        tax_rate=Decimal('0.18'),  # 18% GST
        discount_rate=Decimal(str(discount_rate)),
        notes=notes
    )
    
    # Generate PDF
    pdf_path = pdf_generator.generate_invoice(invoice)
    
    print(f"\nInvoice created successfully!")
    print(f"Invoice Number: {invoice.invoice_number}")
    print(f"Total Amount: Rs.{invoice.total_amount:.2f}")
    print(f"PDF saved to: {pdf_path}")
    
    return invoice, pdf_path

def main():
    """Main function"""
    print("Invoice Generator - No Database Mode")
    print("=" * 40)
    print("1. Generate sample invoices")
    print("2. Create custom invoice")
    print("3. Exit")
    
    while True:
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            try:
                print("\nGenerating sample invoices...")
                invoices = create_sample_invoices()
                print(f"Successfully generated {len(invoices)} sample invoices!")
            except Exception as e:
                print(f"Error generating sample invoices: {e}")
        
        elif choice == "2":
            try:
                result = create_custom_invoice()
                if result:
                    print("Custom invoice created successfully!")
            except Exception as e:
                print(f"Error creating custom invoice: {e}")
        
        elif choice == "3":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == '__main__':
    main()