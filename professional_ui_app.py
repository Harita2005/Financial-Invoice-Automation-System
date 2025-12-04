#!/usr/bin/env python3
"""
Professional Colorful UI Invoice Generator
"""

from flask import Flask, render_template, request, send_file, jsonify
import os
from datetime import datetime, timedelta
from decimal import Decimal
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

app = Flask(__name__)

def create_invoice_pdf(data):
    """Create professional PDF invoice"""
    invoice_no = data['invoice_number']
    filename = f"invoice_{invoice_no}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = os.path.join("output", filename)
    os.makedirs("output", exist_ok=True)
    
    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    story.append(Paragraph("PROFESSIONAL TAX INVOICE", styles['Title']))
    story.append(Paragraph(f"Invoice No: {invoice_no}", styles['Normal']))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Customer
    story.append(Paragraph("Bill To:", styles['Heading2']))
    story.append(Paragraph(data['customer_name'], styles['Normal']))
    story.append(Paragraph(data['customer_address'], styles['Normal']))
    if data.get('customer_email'):
        story.append(Paragraph(f"Email: {data['customer_email']}", styles['Normal']))
    if data.get('customer_phone'):
        story.append(Paragraph(f"Phone: {data['customer_phone']}", styles['Normal']))
    if data.get('customer_gstin'):
        story.append(Paragraph(f"GSTIN: {data['customer_gstin']}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Items table
    table_data = [['S.No', 'Description', 'Qty', 'Rate (Rs.)', 'GST%', 'Amount (Rs.)']]
    
    subtotal = 0
    total_gst = 0
    
    for i, item in enumerate(data['items'], 1):
        qty = float(item['quantity'])
        rate = float(item['rate'])
        gst_rate = float(item['gst_rate'])
        
        amount = qty * rate
        gst_amount = amount * gst_rate / 100
        total_amount = amount + gst_amount
        
        subtotal += amount
        total_gst += gst_amount
        
        table_data.append([
            str(i),
            item['description'],
            f"{qty:.1f}",
            f"{rate:.2f}",
            f"{gst_rate:.0f}%",
            f"{total_amount:.2f}"
        ])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    
    # Totals
    discount_rate = float(data.get('discount_rate', 0))
    discount_amount = subtotal * discount_rate / 100
    grand_total = subtotal + total_gst - discount_amount
    
    totals_data = [
        ['Subtotal:', f"Rs. {subtotal:.2f}"],
        ['GST:', f"Rs. {total_gst:.2f}"],
        ['Discount:', f"Rs. {discount_amount:.2f}"],
        ['Grand Total:', f"Rs. {grand_total:.2f}"]
    ]
    
    totals_table = Table(totals_data, colWidths=[3*inch, 1.5*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#667eea')),
    ]))
    
    story.append(totals_table)
    
    if data.get('notes'):
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"Notes: {data['notes']}", styles['Normal']))
    
    doc.build(story)
    return filename

@app.route('/')
def index():
    return render_template('professional_ui.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        filename = create_invoice_pdf(data)
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join('output', filename), as_attachment=True)

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    print("Professional Invoice Generator starting at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)