#!/usr/bin/env python3
"""
Web-based Invoice Generator with Modern UI
"""

from flask import Flask, render_template, request, send_file, jsonify
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
import json

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models import Invoice, Customer, InvoiceItem
from src.pdf_generator import PDFGenerator
from src.config_manager import ConfigManager

app = Flask(__name__)

class WebInvoiceGenerator:
    def __init__(self):
        self.config_manager = ConfigManager('config/settings.json')
        self.pdf_generator = PDFGenerator(self.config_manager)
    
    def create_invoice_pdf(self, invoice_data):
        """Create invoice PDF from form data"""
        
        # Create customer
        customer = Customer(
            name=invoice_data['customer_name'],
            email=invoice_data['customer_email'],
            address=invoice_data['customer_address'],
            phone=invoice_data.get('customer_phone')
        )
        
        # Create items with GST calculations
        items = []
        for item_data in invoice_data['items']:
            quantity = float(item_data['quantity'])
            rate = float(item_data['rate'])
            gst_rate = float(item_data['gst_rate'])
            
            # Calculate GST
            basic_amount = Decimal(str(quantity * rate))
            gst_amount = basic_amount * Decimal(str(gst_rate)) / Decimal('100')
            
            # Enhanced description with GST info
            description = f"{item_data['description']} (GST {gst_rate}%)"
            
            items.append(InvoiceItem(
                description=description,
                quantity=int(quantity) if quantity == int(quantity) else quantity,
                unit_price=Decimal(str(rate))
            ))
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_data['invoice_number'],
            customer=customer,
            items=items,
            issue_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=int(invoice_data.get('payment_days', 30))),
            tax_rate=Decimal('0.18'),  # Default GST
            discount_rate=Decimal(str(invoice_data.get('discount_rate', 0))) / Decimal('100'),
            notes=invoice_data.get('notes')
        )
        
        # Generate PDF
        pdf_path = self.pdf_generator.generate_invoice(invoice)
        return pdf_path

web_generator = WebInvoiceGenerator()

@app.route('/')
def index():
    """Main invoice form page"""
    return render_template('invoice_form.html')

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    """Generate invoice PDF from form data"""
    try:
        invoice_data = request.json
        pdf_path = web_generator.create_invoice_pdf(invoice_data)
        
        return jsonify({
            'success': True,
            'pdf_path': pdf_path,
            'download_url': f'/download/{os.path.basename(pdf_path)}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated PDF"""
    file_path = os.path.join('output', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

if __name__ == '__main__':
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    
    print("Starting Invoice Generator Web App...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)