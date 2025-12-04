#!/usr/bin/env python3
"""
Simple Material Invoice Generator - No Database Required
"""

import os
from datetime import datetime, timedelta
from decimal import Decimal

def create_material_invoice():
    """Create material invoice with sample data"""
    
    # Sample customer data
    customer = {
        'name': 'ABC Construction Company',
        'address': '123 Building Street\nMumbai, Maharashtra 400001\nIndia',
        'phone': '+91 98765 43210',
        'gstin': '27ABCDE1234F1Z5'
    }
    
    # Sample material purchases
    materials = [
        {
            'description': 'Steel Rods (12mm TMT)',
            'quantity': 50,
            'unit': 'kg',
            'rate': 65.00,
            'gst_rate': 18
        },
        {
            'description': 'Cement Bags (OPC 53 Grade)',
            'quantity': 20,
            'unit': 'bags',
            'rate': 350.00,
            'gst_rate': 28
        },
        {
            'description': 'Red Bricks (First Class)',
            'quantity': 1000,
            'unit': 'pieces',
            'rate': 8.00,
            'gst_rate': 5
        },
        {
            'description': 'River Sand (Fine)',
            'quantity': 100,
            'unit': 'cubic ft',
            'rate': 45.00,
            'gst_rate': 5
        },
        {
            'description': 'Electrical Wire (2.5mm)',
            'quantity': 200,
            'unit': 'meters',
            'rate': 25.00,
            'gst_rate': 18
        }
    ]
    
    # Calculate amounts for each item
    invoice_items = []
    subtotal = Decimal('0')
    total_gst = Decimal('0')
    
    for material in materials:
        basic_amount = Decimal(str(material['quantity'])) * Decimal(str(material['rate']))
        gst_amount = basic_amount * Decimal(str(material['gst_rate'])) / Decimal('100')
        total_amount = basic_amount + gst_amount
        
        invoice_items.append({
            'description': f"{material['description']} ({material['quantity']} {material['unit']})",
            'quantity': material['quantity'],
            'unit': material['unit'],
            'rate': material['rate'],
            'basic_amount': basic_amount,
            'gst_rate': material['gst_rate'],
            'gst_amount': gst_amount,
            'total_amount': total_amount
        })
        
        subtotal += basic_amount
        total_gst += gst_amount
    
    grand_total = subtotal + total_gst
    
    # Generate invoice
    invoice_no = f"MAT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    pdf_path = create_pdf_invoice(invoice_no, customer, invoice_items, subtotal, total_gst, grand_total)
    
    return pdf_path, invoice_no, grand_total

def create_pdf_invoice(invoice_no, customer, items, subtotal, total_gst, grand_total):
    """Create PDF invoice"""
    
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    filename = f"output/material_invoice_{invoice_no}.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch)
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='CompanyHeader',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.darkblue,
        alignment=TA_CENTER,
        spaceAfter=12
    ))
    
    story = []
    
    # Company Header
    story.append(Paragraph("MATERIAL SUPPLY COMPANY", styles['CompanyHeader']))
    story.append(Paragraph("456 Industrial Estate, Mumbai, Maharashtra 400042", styles['Normal']))
    story.append(Paragraph("Phone: +91 22 2345 6789 | Email: sales@materialsupply.com", styles['Normal']))
    story.append(Paragraph("GSTIN: 27XYZAB1234C1Z5 | PAN: XYZAB1234C", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Invoice Title
    story.append(Paragraph("TAX INVOICE", styles['Heading1']))
    story.append(Spacer(1, 0.1*inch))
    
    # Invoice Details Table
    invoice_details = [
        ['Invoice No:', invoice_no, 'Date:', datetime.now().strftime('%d/%m/%Y')],
        ['Due Date:', (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y'), 'Place of Supply:', 'Maharashtra']
    ]
    
    details_table = Table(invoice_details, colWidths=[1.2*inch, 1.8*inch, 1*inch, 1.5*inch])
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    
    story.append(details_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Customer Details
    story.append(Paragraph("Bill To:", styles['Heading2']))
    story.append(Paragraph(customer['name'], styles['Normal']))
    story.append(Paragraph(customer['address'], styles['Normal']))
    story.append(Paragraph(f"Phone: {customer['phone']}", styles['Normal']))
    story.append(Paragraph(f"GSTIN: {customer['gstin']}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Items Table Header
    table_data = [['S.No', 'Description', 'Qty', 'Unit', 'Rate (Rs.)', 'Amount (Rs.)', 'GST%', 'GST Amt (Rs.)', 'Total (Rs.)']]
    
    # Add items
    for i, item in enumerate(items, 1):
        table_data.append([
            str(i),
            item['description'],
            str(item['quantity']),
            item['unit'],
            f"{item['rate']:.2f}",
            f"{item['basic_amount']:.2f}",
            f"{item['gst_rate']}%",
            f"{item['gst_amount']:.2f}",
            f"{item['total_amount']:.2f}"
        ])
    
    # Create table
    table = Table(table_data, colWidths=[0.4*inch, 2*inch, 0.5*inch, 0.6*inch, 0.8*inch, 0.9*inch, 0.5*inch, 0.8*inch, 0.9*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    
    # GST Summary
    gst_summary = {}
    for item in items:
        rate = item['gst_rate']
        if rate not in gst_summary:
            gst_summary[rate] = {'taxable': Decimal('0'), 'gst': Decimal('0')}
        gst_summary[rate]['taxable'] += item['basic_amount']
        gst_summary[rate]['gst'] += item['gst_amount']
    
    # GST Breakdown Table
    gst_data = [['GST Rate', 'Taxable Amount (Rs.)', 'GST Amount (Rs.)']]
    for rate in sorted(gst_summary.keys()):
        gst_data.append([
            f"{rate}%",
            f"{gst_summary[rate]['taxable']:.2f}",
            f"{gst_summary[rate]['gst']:.2f}"
        ])
    
    gst_table = Table(gst_data, colWidths=[1.5*inch, 2*inch, 2*inch])
    gst_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(Paragraph("GST Summary:", styles['Heading3']))
    story.append(gst_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Totals Section
    totals_data = [
        ['Subtotal (Before Tax):', f"Rs. {subtotal:.2f}"],
        ['Total GST:', f"Rs. {total_gst:.2f}"],
        ['Grand Total:', f"Rs. {grand_total:.2f}"]
    ]
    
    totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
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
    
    # Amount in Words
    amount_words = number_to_words(float(grand_total))
    story.append(Paragraph(f"Amount in Words: {amount_words} Only", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Terms and Conditions
    story.append(Paragraph("Terms & Conditions:", styles['Heading3']))
    terms = [
        "1. Payment due within 30 days from invoice date",
        "2. Interest @ 18% p.a. will be charged on overdue amounts",
        "3. Goods once sold will not be taken back",
        "4. All disputes subject to Mumbai jurisdiction only",
        "5. This is a computer generated invoice"
    ]
    
    for term in terms:
        story.append(Paragraph(term, styles['Normal']))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Thank you for your business!", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    return filename

def number_to_words(number):
    """Convert number to words (Indian format)"""
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
    
    # Handle decimal part
    rupees = int(number)
    paise = int((number - rupees) * 100)
    
    # Convert rupees
    crores = rupees // 10000000
    rupees %= 10000000
    lakhs = rupees // 100000
    rupees %= 100000
    thousands = rupees // 1000
    rupees %= 1000
    hundreds = rupees
    
    result = ""
    if crores > 0:
        result += convert_hundreds(crores) + "Crore "
    if lakhs > 0:
        result += convert_hundreds(lakhs) + "Lakh "
    if thousands > 0:
        result += convert_hundreds(thousands) + "Thousand "
    if hundreds > 0:
        result += convert_hundreds(hundreds)
    
    result = result.strip() + " Rupees"
    
    if paise > 0:
        result += " and " + convert_hundreds(paise).strip() + " Paise"
    
    return result

def main():
    """Main function"""
    print("MATERIAL INVOICE GENERATOR")
    print("=" * 30)
    print("Generating sample material purchase invoice...")
    
    try:
        pdf_path, invoice_no, total = create_material_invoice()
        
        print(f"\nSUCCESS!")
        print(f"Invoice Number: {invoice_no}")
        print(f"Total Amount: Rs. {total:.2f}")
        print(f"PDF saved to: {pdf_path}")
        print(f"\nYour invoice is ready for download!")
        
        # Display summary
        print(f"\nInvoice Summary:")
        print(f"- Customer: ABC Construction Company")
        print(f"- Items: 5 different materials")
        print(f"- GST Rates: 5%, 18%, 28%")
        print(f"- Total with GST: Rs. {total:.2f}")
        
    except Exception as e:
        print(f"Error generating invoice: {e}")

if __name__ == '__main__':
    main()