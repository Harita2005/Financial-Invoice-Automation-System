#!/usr/bin/env python3
"""
Simple Web Invoice Generator - Fixed PDF Generation
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
    """Create PDF invoice directly"""
    
    # Create filename
    invoice_no = data['invoice_number']
    filename = f"invoice_{invoice_no}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = os.path.join("output", filename)
    os.makedirs("output", exist_ok=True)
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    story.append(Paragraph("INVOICE", styles['Title']))
    story.append(Paragraph(f"Invoice No: {invoice_no}", styles['Normal']))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Customer
    story.append(Paragraph("Bill To:", styles['Heading2']))
    story.append(Paragraph(data['customer_name'], styles['Normal']))
    story.append(Paragraph(data['customer_address'], styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Items table
    table_data = [['Item', 'Qty', 'Rate', 'GST%', 'Amount']]
    
    subtotal = 0
    total_gst = 0
    
    for item in data['items']:
        qty = float(item['quantity'])
        rate = float(item['rate'])
        gst_rate = float(item['gst_rate'])
        
        amount = qty * rate
        gst_amount = amount * gst_rate / 100
        total_amount = amount + gst_amount
        
        subtotal += amount
        total_gst += gst_amount
        
        table_data.append([
            item['description'],
            str(qty),
            f"Rs.{rate:.2f}",
            f"{gst_rate}%",
            f"Rs.{total_amount:.2f}"
        ])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    
    # Totals
    discount_rate = float(data.get('discount_rate', 0))
    discount_amount = subtotal * discount_rate / 100
    grand_total = subtotal + total_gst - discount_amount
    
    totals_data = [
        ['Subtotal:', f"Rs.{subtotal:.2f}"],
        ['GST:', f"Rs.{total_gst:.2f}"],
        ['Discount:', f"Rs.{discount_amount:.2f}"],
        ['Total:', f"Rs.{grand_total:.2f}"]
    ]
    
    totals_table = Table(totals_data, colWidths=[3*inch, 1.5*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
    ]))
    
    story.append(totals_table)
    
    if data.get('notes'):
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"Notes: {data['notes']}", styles['Normal']))
    
    doc.build(story)
    return filename

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Invoice Generator</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .item-row { display: flex; gap: 10px; margin-bottom: 10px; }
        .item-row input { flex: 1; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .totals { background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .error { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 4px; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>Invoice Generator</h1>
    
    <form id="invoiceForm">
        <div class="form-group">
            <label>Invoice Number:</label>
            <input type="text" id="invoice_number" value="INV-''' + datetime.now().strftime('%Y%m%d%H%M%S') + '''" required>
        </div>
        
        <div class="form-group">
            <label>Customer Name:</label>
            <input type="text" id="customer_name" required>
        </div>
        
        <div class="form-group">
            <label>Customer Email:</label>
            <input type="email" id="customer_email" required>
        </div>
        
        <div class="form-group">
            <label>Customer Address:</label>
            <textarea id="customer_address" rows="3" required></textarea>
        </div>
        
        <h3>Items</h3>
        <div id="items">
            <div class="item-row">
                <input type="text" placeholder="Description" class="item-desc" required>
                <input type="number" placeholder="Qty" class="item-qty" step="0.01" required>
                <input type="number" placeholder="Rate" class="item-rate" step="0.01" required>
                <select class="item-gst">
                    <option value="0">0%</option>
                    <option value="5">5%</option>
                    <option value="12">12%</option>
                    <option value="18" selected>18%</option>
                    <option value="28">28%</option>
                </select>
                <button type="button" onclick="removeItem(this)">Remove</button>
            </div>
        </div>
        <button type="button" onclick="addItem()">Add Item</button>
        
        <div class="form-group">
            <label>Discount %:</label>
            <input type="number" id="discount_rate" value="0" step="0.01" min="0">
        </div>
        
        <div class="form-group">
            <label>Notes:</label>
            <textarea id="notes" rows="2"></textarea>
        </div>
        
        <div class="totals" id="totals">
            <div>Subtotal: Rs.<span id="subtotal">0.00</span></div>
            <div>GST: Rs.<span id="gst">0.00</span></div>
            <div>Discount: Rs.<span id="discount">0.00</span></div>
            <div><strong>Total: Rs.<span id="total">0.00</span></strong></div>
        </div>
        
        <button type="submit">Generate Invoice PDF</button>
    </form>
    
    <div id="result"></div>
    
    <script>
        function addItem() {
            const items = document.getElementById('items');
            const newItem = items.children[0].cloneNode(true);
            newItem.querySelectorAll('input').forEach(input => input.value = '');
            newItem.querySelector('select').selectedIndex = 3;
            items.appendChild(newItem);
            calculateTotals();
        }
        
        function removeItem(btn) {
            if (document.getElementById('items').children.length > 1) {
                btn.parentElement.remove();
                calculateTotals();
            }
        }
        
        function calculateTotals() {
            let subtotal = 0, totalGst = 0;
            
            document.querySelectorAll('.item-row').forEach(row => {
                const qty = parseFloat(row.querySelector('.item-qty').value) || 0;
                const rate = parseFloat(row.querySelector('.item-rate').value) || 0;
                const gstRate = parseFloat(row.querySelector('.item-gst').value) || 0;
                
                const amount = qty * rate;
                const gstAmount = amount * gstRate / 100;
                
                subtotal += amount;
                totalGst += gstAmount;
            });
            
            const discountRate = parseFloat(document.getElementById('discount_rate').value) || 0;
            const discountAmount = subtotal * discountRate / 100;
            const grandTotal = subtotal + totalGst - discountAmount;
            
            document.getElementById('subtotal').textContent = subtotal.toFixed(2);
            document.getElementById('gst').textContent = totalGst.toFixed(2);
            document.getElementById('discount').textContent = discountAmount.toFixed(2);
            document.getElementById('total').textContent = grandTotal.toFixed(2);
        }
        
        document.addEventListener('input', calculateTotals);
        
        document.getElementById('invoiceForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const items = [];
            document.querySelectorAll('.item-row').forEach(row => {
                const desc = row.querySelector('.item-desc').value;
                const qty = row.querySelector('.item-qty').value;
                const rate = row.querySelector('.item-rate').value;
                const gst = row.querySelector('.item-gst').value;
                
                if (desc && qty && rate) {
                    items.push({description: desc, quantity: qty, rate: rate, gst_rate: gst});
                }
            });
            
            if (items.length === 0) {
                alert('Add at least one item!');
                return;
            }
            
            const data = {
                invoice_number: document.getElementById('invoice_number').value,
                customer_name: document.getElementById('customer_name').value,
                customer_email: document.getElementById('customer_email').value,
                customer_address: document.getElementById('customer_address').value,
                discount_rate: document.getElementById('discount_rate').value,
                notes: document.getElementById('notes').value,
                items: items
            };
            
            fetch('/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    document.getElementById('result').innerHTML = 
                        '<div class="success">Invoice generated! <a href="/download/' + result.filename + '">Download PDF</a></div>';
                } else {
                    document.getElementById('result').innerHTML = 
                        '<div class="error">Error: ' + result.error + '</div>';
                }
            });
        });
        
        calculateTotals();
    </script>
</body>
</html>
    '''

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
    os.makedirs('output', exist_ok=True)
    print("Invoice Generator starting at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)