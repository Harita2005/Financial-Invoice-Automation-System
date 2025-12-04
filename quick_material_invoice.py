#!/usr/bin/env python3
"""
Quick Material Invoice Generator - Interactive CLI
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_quick_invoice():
    """Create a quick material invoice with sample data"""
    
    print("QUICK MATERIAL INVOICE GENERATOR")
    print("=" * 40)
    
    # Sample data for quick testing
    sample_materials = [
        {"name": "Steel Rods (12mm)", "unit": "kg", "rate": 65.0, "gst": 18},
        {"name": "Cement Bags", "unit": "bags", "rate": 350.0, "gst": 28},
        {"name": "Bricks", "unit": "pieces", "rate": 8.0, "gst": 5},
        {"name": "Sand", "unit": "cubic ft", "rate": 45.0, "gst": 5},
        {"name": "Electrical Wire", "unit": "meters", "rate": 25.0, "gst": 18},
        {"name": "Paint", "unit": "liters", "rate": 180.0, "gst": 28}
    ]
    
    print("Available Materials:")
    for i, material in enumerate(sample_materials, 1):
        print(f"{i}. {material['name']} - Rs.{material['rate']}/unit (GST: {material['gst']}%)")
    
    # Get customer details
    print("\nCustomer Details:")
    customer_name = input("Customer Name: ").strip() or "ABC Construction Co."
    customer_address = input("Address: ").strip() or "123 Building Street, Mumbai, Maharashtra"
    
    # Select materials and quantities
    selected_items = []
    
    while True:
        try:
            choice = input(f"\nSelect material (1-{len(sample_materials)}) or 'done' to finish: ").strip()
            
            if choice.lower() == 'done':
                if selected_items:
                    break
                else:
                    print("Please add at least one item!")
                    continue
            
            material_idx = int(choice) - 1
            if 0 <= material_idx < len(sample_materials):
                material = sample_materials[material_idx]
                
                quantity = float(input(f"Quantity ({material['unit']}): "))
                
                # Calculate amounts
                basic_amount = quantity * material['rate']
                gst_amount = basic_amount * material['gst'] / 100
                total_amount = basic_amount + gst_amount
                
                selected_items.append({
                    'description': f"{material['name']} ({quantity} {material['unit']})",
                    'quantity': quantity,
                    'rate': material['rate'],
                    'basic_amount': basic_amount,
                    'gst_rate': material['gst'],
                    'gst_amount': gst_amount,
                    'total_amount': total_amount
                })
                
                print(f"Added: {material['name']} - Rs.{total_amount:.2f}")
            else:
                print("Invalid selection!")
                
        except ValueError:
            print("Invalid input!")
    
    # Calculate totals
    subtotal = sum(item['basic_amount'] for item in selected_items)
    total_gst = sum(item['gst_amount'] for item in selected_items)
    grand_total = subtotal + total_gst
    
    # Generate invoice number
    invoice_no = f"MAT-INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Create simple PDF
    create_material_pdf(invoice_no, customer_name, customer_address, selected_items, subtotal, total_gst, grand_total)
    
    return invoice_no

def create_material_pdf(invoice_no, customer_name, customer_address, items, subtotal, total_gst, grand_total):
    """Create PDF for material invoice"""
    
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    filename = f"output/material_invoice_{invoice_no}.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch)
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='CompanyName',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.darkblue,
        alignment=TA_CENTER,
        spaceAfter=12
    ))
    
    story = []
    
    # Company Header
    story.append(Paragraph("MATERIAL SUPPLY COMPANY", styles['CompanyName']))
    story.append(Paragraph("123 Industrial Area, Mumbai, Maharashtra 400001", styles['Normal']))
    story.append(Paragraph("Phone: +91 98765 43210 | Email: sales@materials.com", styles['Normal']))
    story.append(Paragraph("GSTIN: 27ABCDE1234F1Z5", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Invoice Header
    story.append(Paragraph("TAX INVOICE", styles['Heading1']))
    story.append(Paragraph(f"Invoice No: {invoice_no}", styles['Normal']))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Paragraph(f"Due Date: {(datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Customer Details
    story.append(Paragraph("Bill To:", styles['Heading2']))
    story.append(Paragraph(customer_name, styles['Normal']))
    story.append(Paragraph(customer_address, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Items Table
    table_data = [['S.No', 'Description', 'Qty', 'Rate', 'Amount', 'GST%', 'GST Amount', 'Total']]
    
    for i, item in enumerate(items, 1):
        table_data.append([
            str(i),
            item['description'],
            f"{item['quantity']:.1f}",
            f"Rs.{item['rate']:.2f}",
            f"Rs.{item['basic_amount']:.2f}",
            f"{item['gst_rate']}%",
            f"Rs.{item['gst_amount']:.2f}",
            f"Rs.{item['total_amount']:.2f}"
        ])
    
    table = Table(table_data, colWidths=[0.5*inch, 2.2*inch, 0.7*inch, 0.8*inch, 0.9*inch, 0.6*inch, 0.9*inch, 0.9*inch])
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
    
    # Totals
    totals_data = [
        ['Subtotal (Before Tax):', f"Rs.{subtotal:.2f}"],
        ['Total GST:', f"Rs.{total_gst:.2f}"],
        ['Grand Total:', f"Rs.{grand_total:.2f}"]
    ]
    
    totals_table = Table(totals_data, colWidths=[4.5*inch, 1.5*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.darkred),
        ('LINEBELOW', (0, -2), (-1, -2), 1, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
    ]))
    
    story.append(totals_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    story.append(Paragraph("Terms & Conditions:", styles['Heading3']))
    story.append(Paragraph("1. Payment due within 30 days", styles['Normal']))
    story.append(Paragraph("2. Goods once sold will not be taken back", styles['Normal']))
    story.append(Paragraph("3. Subject to Mumbai jurisdiction", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("Thank you for your business!", styles['Normal']))
    story.append(Paragraph("This is a computer generated invoice.", styles['Normal']))
    
    doc.build(story)
    
    print(f"\nInvoice PDF created: {filename}")
    print(f"Total Amount: Rs.{grand_total:.2f}")
    print(f"GST Amount: Rs.{total_gst:.2f}")
    
    return filename

def main():
    """Main function"""
    try:
        invoice_no = create_quick_invoice()
        print(f"\nInvoice {invoice_no} generated successfully!")
        print("Check the 'output' folder for your PDF invoice.")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()