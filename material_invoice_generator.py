#!/usr/bin/env python3
"""
Material Purchase Invoice Generator with GST Calculations
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models import Invoice, Customer, InvoiceItem
from src.pdf_generator import PDFGenerator
from src.config_manager import ConfigManager

class MaterialInvoiceGenerator:
    def __init__(self):
        self.config_manager = ConfigManager('config/settings.json')
        self.pdf_generator = PDFGenerator(self.config_manager)
        
    def get_customer_details(self):
        """Get customer details from user input"""
        print("\n=== CUSTOMER DETAILS ===")
        name = input("Customer/Company Name: ").strip()
        email = input("Email Address: ").strip()
        
        print("Address (press Enter twice when done):")
        address_lines = []
        while True:
            line = input().strip()
            if not line:
                break
            address_lines.append(line)
        address = "\n".join(address_lines)
        
        phone = input("Phone Number (optional): ").strip() or None
        gstin = input("GSTIN (optional): ").strip() or None
        
        return Customer(
            name=name,
            email=email,
            address=address,
            phone=phone
        ), gstin
    
    def get_material_items(self):
        """Get material purchase details"""
        print("\n=== MATERIAL PURCHASE DETAILS ===")
        items = []
        
        while True:
            print(f"\nItem #{len(items) + 1}")
            description = input("Material Description: ").strip()
            if not description:
                if items:
                    break
                else:
                    print("At least one item is required!")
                    continue
            
            try:
                quantity = float(input("Quantity: "))
                unit = input("Unit (kg/pcs/meters/etc): ").strip()
                rate_per_unit = float(input("Rate per unit (Rs.): "))
                
                # GST rate selection
                print("GST Rate Options:")
                print("1. 0% (Exempt)")
                print("2. 5%")
                print("3. 12%")
                print("4. 18%")
                print("5. 28%")
                
                gst_choice = input("Select GST rate (1-5): ").strip()
                gst_rates = {"1": 0, "2": 5, "3": 12, "4": 18, "5": 28}
                gst_rate = gst_rates.get(gst_choice, 18)
                
                # Calculate amounts
                basic_amount = Decimal(str(quantity * rate_per_unit))
                gst_amount = basic_amount * Decimal(str(gst_rate)) / Decimal('100')
                total_amount = basic_amount + gst_amount
                
                # Create enhanced description with GST details
                enhanced_desc = f"{description} ({quantity} {unit} @ Rs.{rate_per_unit:.2f}/unit, GST {gst_rate}%)"
                
                items.append({
                    'item': InvoiceItem(
                        description=enhanced_desc,
                        quantity=int(quantity) if quantity == int(quantity) else quantity,
                        unit_price=Decimal(str(rate_per_unit))
                    ),
                    'unit': unit,
                    'gst_rate': gst_rate,
                    'basic_amount': basic_amount,
                    'gst_amount': gst_amount,
                    'total_amount': total_amount
                })
                
                print(f"Added: {description}")
                print(f"  Basic Amount: Rs.{basic_amount:.2f}")
                print(f"  GST ({gst_rate}%): Rs.{gst_amount:.2f}")
                print(f"  Total: Rs.{total_amount:.2f}")
                
                add_more = input("Add another item? (y/n): ").strip().lower()
                if add_more != 'y':
                    break
                    
            except ValueError:
                print("Invalid input! Please enter valid numbers.")
                continue
        
        return items
    
    def calculate_totals(self, items):
        """Calculate comprehensive totals with GST breakdown"""
        subtotal = sum(item['basic_amount'] for item in items)
        
        # GST breakdown by rate
        gst_breakdown = {}
        total_gst = Decimal('0')
        
        for item in items:
            rate = item['gst_rate']
            if rate not in gst_breakdown:
                gst_breakdown[rate] = Decimal('0')
            gst_breakdown[rate] += item['gst_amount']
            total_gst += item['gst_amount']
        
        grand_total = subtotal + total_gst
        
        return {
            'subtotal': subtotal,
            'gst_breakdown': gst_breakdown,
            'total_gst': total_gst,
            'grand_total': grand_total
        }
    
    def get_invoice_details(self):
        """Get invoice specific details"""
        print("\n=== INVOICE DETAILS ===")
        
        invoice_no = input("Invoice Number (or press Enter for auto): ").strip()
        if not invoice_no:
            invoice_no = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Payment terms
        print("Payment Terms:")
        print("1. Immediate")
        print("2. 15 Days")
        print("3. 30 Days")
        print("4. 45 Days")
        print("5. Custom")
        
        term_choice = input("Select payment term (1-5): ").strip()
        term_days = {"1": 0, "2": 15, "3": 30, "4": 45}
        
        if term_choice == "5":
            try:
                days = int(input("Enter custom days: "))
            except ValueError:
                days = 30
        else:
            days = term_days.get(term_choice, 30)
        
        due_date = datetime.now() + timedelta(days=days)
        
        notes = input("Additional Notes (optional): ").strip() or None
        
        return invoice_no, due_date, notes
    
    def create_enhanced_pdf(self, invoice, items_data, totals, gstin=None):
        """Create enhanced PDF with GST breakdown"""
        
        # Create a custom PDF with GST details
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        
        # Generate filename
        filename = f"invoice_{invoice.invoice_number}_{datetime.now().strftime('%Y%m%d')}.pdf"
        filepath = os.path.join("output", filename)
        os.makedirs("output", exist_ok=True)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Company Header
        company_info = self.config_manager.get_company_info()
        story.append(Paragraph(f"<b>{company_info['name']}</b>", styles['Title']))
        story.append(Paragraph(company_info['address'], styles['Normal']))
        story.append(Paragraph(f"Phone: {company_info['phone']} | Email: {company_info['email']}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Invoice Title
        story.append(Paragraph(f"<b>TAX INVOICE</b>", styles['Heading1']))
        story.append(Paragraph(f"Invoice No: {invoice.invoice_number}", styles['Normal']))
        story.append(Paragraph(f"Date: {invoice.issue_date.strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Paragraph(f"Due Date: {invoice.due_date.strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Customer Details
        story.append(Paragraph("<b>Bill To:</b>", styles['Heading2']))
        story.append(Paragraph(invoice.customer.name, styles['Normal']))
        story.append(Paragraph(invoice.customer.address, styles['Normal']))
        if gstin:
            story.append(Paragraph(f"GSTIN: {gstin}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Items Table
        table_data = [['S.No', 'Description', 'Qty', 'Rate', 'Amount', 'GST%', 'GST Amt', 'Total']]
        
        for i, item_data in enumerate(items_data, 1):
            item = item_data['item']
            table_data.append([
                str(i),
                item.description,
                str(item.quantity),
                f"Rs.{item.unit_price:.2f}",
                f"Rs.{item_data['basic_amount']:.2f}",
                f"{item_data['gst_rate']}%",
                f"Rs.{item_data['gst_amount']:.2f}",
                f"Rs.{item_data['total_amount']:.2f}"
            ])
        
        table = Table(table_data, colWidths=[0.5*inch, 2.5*inch, 0.7*inch, 0.8*inch, 0.8*inch, 0.6*inch, 0.8*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        # Totals Section
        totals_data = [
            ['Subtotal (Before Tax):', f"Rs.{totals['subtotal']:.2f}"]
        ]
        
        # GST Breakdown
        for rate, amount in sorted(totals['gst_breakdown'].items()):
            if amount > 0:
                totals_data.append([f'GST @ {rate}%:', f"Rs.{amount:.2f}"])
        
        totals_data.extend([
            ['Total GST:', f"Rs.{totals['total_gst']:.2f}"],
            ['Grand Total:', f"Rs.{totals['grand_total']:.2f}"]
        ])
        
        totals_table = Table(totals_data, colWidths=[4*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.darkred),
            ('LINEBELOW', (0, -2), (-1, -2), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
        ]))
        
        story.append(totals_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Amount in words
        amount_words = self.number_to_words(float(totals['grand_total']))
        story.append(Paragraph(f"<b>Amount in Words:</b> {amount_words} Only", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Notes
        if invoice.notes:
            story.append(Paragraph(f"<b>Notes:</b> {invoice.notes}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Footer
        story.append(Paragraph("Thank you for your business!", styles['Normal']))
        story.append(Paragraph("This is a computer generated invoice.", styles['Normal']))
        
        doc.build(story)
        return filepath
    
    def number_to_words(self, number):
        """Convert number to words (simplified version)"""
        ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
        teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        
        def convert_hundreds(n):
            result = ""
            if n >= 100:
                result += ones[n // 100] + " Hundred "
                n %= 100
            if n >= 20:
                result += tens[n // 10] + " "
                n %= 10
            elif n >= 10:
                result += teens[n - 10] + " "
                n = 0
            if n > 0:
                result += ones[n] + " "
            return result
        
        if number == 0:
            return "Zero Rupees"
        
        crores = int(number // 10000000)
        number %= 10000000
        lakhs = int(number // 100000)
        number %= 100000
        thousands = int(number // 1000)
        number %= 1000
        hundreds = int(number)
        
        result = ""
        if crores > 0:
            result += convert_hundreds(crores) + "Crore "
        if lakhs > 0:
            result += convert_hundreds(lakhs) + "Lakh "
        if thousands > 0:
            result += convert_hundreds(thousands) + "Thousand "
        if hundreds > 0:
            result += convert_hundreds(hundreds)
        
        return result.strip() + " Rupees"
    
    def generate_material_invoice(self):
        """Main function to generate material purchase invoice"""
        print("MATERIAL PURCHASE INVOICE GENERATOR")
        print("=" * 50)
        
        try:
            # Get all details
            customer, gstin = self.get_customer_details()
            items_data = self.get_material_items()
            invoice_no, due_date, notes = self.get_invoice_details()
            
            # Calculate totals
            totals = self.calculate_totals(items_data)
            
            # Create basic invoice object for compatibility
            invoice_items = [item_data['item'] for item_data in items_data]
            invoice = Invoice(
                invoice_number=invoice_no,
                customer=customer,
                items=invoice_items,
                issue_date=datetime.now(),
                due_date=due_date,
                tax_rate=Decimal('0'),  # We handle GST separately
                discount_rate=Decimal('0'),
                notes=notes
            )
            
            # Generate enhanced PDF
            pdf_path = self.create_enhanced_pdf(invoice, items_data, totals, gstin)
            
            # Display summary
            print("\n" + "=" * 50)
            print("INVOICE GENERATED SUCCESSFULLY!")
            print("=" * 50)
            print(f"Invoice Number: {invoice_no}")
            print(f"Customer: {customer.name}")
            print(f"Total Items: {len(items_data)}")
            print(f"Subtotal: Rs.{totals['subtotal']:.2f}")
            print(f"Total GST: Rs.{totals['total_gst']:.2f}")
            print(f"Grand Total: Rs.{totals['grand_total']:.2f}")
            print(f"PDF saved to: {pdf_path}")
            print("\nGST Breakdown:")
            for rate, amount in sorted(totals['gst_breakdown'].items()):
                if amount > 0:
                    print(f"  GST @ {rate}%: Rs.{amount:.2f}")
            
            return pdf_path
            
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return None
        except Exception as e:
            print(f"Error generating invoice: {e}")
            return None

def main():
    """Main entry point"""
    generator = MaterialInvoiceGenerator()
    
    while True:
        print("\nMATERIAL INVOICE GENERATOR")
        print("1. Create New Invoice")
        print("2. Exit")
        
        choice = input("Select option (1-2): ").strip()
        
        if choice == "1":
            pdf_path = generator.generate_material_invoice()
            if pdf_path:
                print(f"\nInvoice ready for download: {pdf_path}")
        elif choice == "2":
            print("Thank you for using Material Invoice Generator!")
            break
        else:
            print("Invalid choice. Please select 1 or 2.")

if __name__ == '__main__':
    main()