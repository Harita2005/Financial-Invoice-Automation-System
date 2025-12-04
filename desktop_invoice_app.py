#!/usr/bin/env python3
"""
Desktop Invoice Generator - Guaranteed PDF Download
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from decimal import Decimal
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Invoice Generator - Best UI")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        self.items = []
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame with scrollbar
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, text="🧾 INVOICE GENERATOR", 
                        font=('Arial', 24, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title.pack(pady=(0, 20))
        
        # Create notebook for sections
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Invoice Details Tab
        invoice_frame = ttk.Frame(notebook)
        notebook.add(invoice_frame, text="📋 Invoice Details")
        self.setup_invoice_tab(invoice_frame)
        
        # Customer Tab
        customer_frame = ttk.Frame(notebook)
        notebook.add(customer_frame, text="👤 Customer")
        self.setup_customer_tab(customer_frame)
        
        # Items Tab
        items_frame = ttk.Frame(notebook)
        notebook.add(items_frame, text="📦 Items")
        self.setup_items_tab(items_frame)
        
        # Generate Tab
        generate_frame = ttk.Frame(notebook)
        notebook.add(generate_frame, text="🚀 Generate")
        self.setup_generate_tab(generate_frame)
    
    def setup_invoice_tab(self, parent):
        # Invoice details
        tk.Label(parent, text="Invoice Number:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky='w', padx=10, pady=10)
        self.invoice_no = tk.StringVar(value=f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        tk.Entry(parent, textvariable=self.invoice_no, font=('Arial', 12), width=30).grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(parent, text="Payment Terms:", font=('Arial', 12, 'bold')).grid(row=1, column=0, sticky='w', padx=10, pady=10)
        self.payment_days = tk.StringVar(value="30")
        payment_combo = ttk.Combobox(parent, textvariable=self.payment_days, values=["0", "15", "30", "45"], width=27)
        payment_combo.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(parent, text="Discount %:", font=('Arial', 12, 'bold')).grid(row=2, column=0, sticky='w', padx=10, pady=10)
        self.discount = tk.StringVar(value="0")
        tk.Entry(parent, textvariable=self.discount, font=('Arial', 12), width=30).grid(row=2, column=1, padx=10, pady=10)
    
    def setup_customer_tab(self, parent):
        # Customer details
        fields = [
            ("Customer Name *:", "customer_name"),
            ("Email *:", "customer_email"),
            ("Phone:", "customer_phone"),
            ("GSTIN:", "customer_gstin")
        ]
        
        self.customer_vars = {}
        for i, (label, var_name) in enumerate(fields):
            tk.Label(parent, text=label, font=('Arial', 12, 'bold')).grid(row=i, column=0, sticky='w', padx=10, pady=10)
            self.customer_vars[var_name] = tk.StringVar()
            tk.Entry(parent, textvariable=self.customer_vars[var_name], font=('Arial', 12), width=40).grid(row=i, column=1, padx=10, pady=10)
        
        tk.Label(parent, text="Address *:", font=('Arial', 12, 'bold')).grid(row=len(fields), column=0, sticky='nw', padx=10, pady=10)
        self.customer_address = tk.Text(parent, height=4, width=40, font=('Arial', 12))
        self.customer_address.grid(row=len(fields), column=1, padx=10, pady=10)
    
    def setup_items_tab(self, parent):
        # Items section
        items_label_frame = tk.LabelFrame(parent, text="Invoice Items", font=('Arial', 14, 'bold'), padx=10, pady=10)
        items_label_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Item entry frame
        entry_frame = tk.Frame(items_label_frame)
        entry_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(entry_frame, text="Description:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5)
        self.item_desc = tk.Entry(entry_frame, width=25, font=('Arial', 10))
        self.item_desc.grid(row=1, column=0, padx=5)
        
        tk.Label(entry_frame, text="Quantity:", font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=5)
        self.item_qty = tk.Entry(entry_frame, width=10, font=('Arial', 10))
        self.item_qty.grid(row=1, column=1, padx=5)
        
        tk.Label(entry_frame, text="Rate (Rs.):", font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=5)
        self.item_rate = tk.Entry(entry_frame, width=12, font=('Arial', 10))
        self.item_rate.grid(row=1, column=2, padx=5)
        
        tk.Label(entry_frame, text="GST %:", font=('Arial', 10, 'bold')).grid(row=0, column=3, padx=5)
        self.item_gst = ttk.Combobox(entry_frame, values=["0", "5", "12", "18", "28"], width=8)
        self.item_gst.set("18")
        self.item_gst.grid(row=1, column=3, padx=5)
        
        tk.Button(entry_frame, text="Add Item", command=self.add_item, 
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold')).grid(row=1, column=4, padx=10)
        
        # Items list
        self.items_listbox = tk.Listbox(items_label_frame, height=8, font=('Arial', 10))
        self.items_listbox.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Remove button
        tk.Button(items_label_frame, text="Remove Selected", command=self.remove_item,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(pady=5)
        
        # Totals display
        self.totals_frame = tk.LabelFrame(items_label_frame, text="Totals", font=('Arial', 12, 'bold'))
        self.totals_frame.pack(fill=tk.X, pady=10)
        
        self.totals_text = tk.Text(self.totals_frame, height=5, font=('Arial', 11), bg='#ecf0f1')
        self.totals_text.pack(fill=tk.X, padx=10, pady=10)
        
        self.update_totals()
    
    def setup_generate_tab(self, parent):
        # Notes section
        tk.Label(parent, text="Notes/Terms & Conditions:", font=('Arial', 12, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        self.notes = tk.Text(parent, height=4, font=('Arial', 11))
        self.notes.pack(fill=tk.X, padx=10, pady=5)
        self.notes.insert('1.0', "Payment due within 30 days. Thank you for your business!")
        
        # Generate button
        generate_btn = tk.Button(parent, text="🚀 GENERATE INVOICE PDF", 
                               command=self.generate_invoice,
                               bg='#27ae60', fg='white', 
                               font=('Arial', 16, 'bold'),
                               height=2)
        generate_btn.pack(pady=30, fill=tk.X, padx=50)
        
        # Status
        self.status_label = tk.Label(parent, text="Ready to generate invoice", 
                                   font=('Arial', 12), fg='#2c3e50')
        self.status_label.pack(pady=10)
    
    def add_item(self):
        desc = self.item_desc.get().strip()
        qty = self.item_qty.get().strip()
        rate = self.item_rate.get().strip()
        gst = self.item_gst.get().strip()
        
        if not all([desc, qty, rate, gst]):
            messagebox.showerror("Error", "Please fill all item fields!")
            return
        
        try:
            qty_float = float(qty)
            rate_float = float(rate)
            gst_float = float(gst)
            
            amount = qty_float * rate_float
            gst_amount = amount * gst_float / 100
            total = amount + gst_amount
            
            item = {
                'description': desc,
                'quantity': qty_float,
                'rate': rate_float,
                'gst_rate': gst_float,
                'amount': amount,
                'gst_amount': gst_amount,
                'total': total
            }
            
            self.items.append(item)
            
            # Add to listbox
            display_text = f"{desc} | Qty: {qty_float} | Rate: Rs.{rate_float:.2f} | GST: {gst_float}% | Total: Rs.{total:.2f}"
            self.items_listbox.insert(tk.END, display_text)
            
            # Clear fields
            self.item_desc.delete(0, tk.END)
            self.item_qty.delete(0, tk.END)
            self.item_rate.delete(0, tk.END)
            self.item_gst.set("18")
            
            self.update_totals()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")
    
    def remove_item(self):
        selection = self.items_listbox.curselection()
        if selection:
            index = selection[0]
            self.items_listbox.delete(index)
            del self.items[index]
            self.update_totals()
    
    def update_totals(self):
        if not self.items:
            totals_text = "Subtotal: Rs. 0.00\nGST: Rs. 0.00\nDiscount: Rs. 0.00\nGrand Total: Rs. 0.00"
        else:
            subtotal = sum(item['amount'] for item in self.items)
            total_gst = sum(item['gst_amount'] for item in self.items)
            
            try:
                discount_rate = float(self.discount.get() or 0)
            except:
                discount_rate = 0
            
            discount_amount = subtotal * discount_rate / 100
            grand_total = subtotal + total_gst - discount_amount
            
            totals_text = f"""Subtotal: Rs. {subtotal:.2f}
GST: Rs. {total_gst:.2f}
Discount ({discount_rate}%): Rs. {discount_amount:.2f}
Grand Total: Rs. {grand_total:.2f}"""
        
        self.totals_text.delete('1.0', tk.END)
        self.totals_text.insert('1.0', totals_text)
    
    def generate_invoice(self):
        # Validate
        if not self.customer_vars['customer_name'].get().strip():
            messagebox.showerror("Error", "Customer name is required!")
            return
        
        if not self.customer_vars['customer_email'].get().strip():
            messagebox.showerror("Error", "Customer email is required!")
            return
        
        if not self.customer_address.get('1.0', tk.END).strip():
            messagebox.showerror("Error", "Customer address is required!")
            return
        
        if not self.items:
            messagebox.showerror("Error", "Please add at least one item!")
            return
        
        try:
            # Ask where to save
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialname=f"invoice_{self.invoice_no.get()}.pdf"
            )
            
            if not filename:
                return
            
            self.status_label.config(text="Generating PDF...", fg='#f39c12')
            self.root.update()
            
            # Create PDF
            self.create_pdf(filename)
            
            self.status_label.config(text=f"Invoice saved: {filename}", fg='#27ae60')
            messagebox.showinfo("Success", f"Invoice PDF generated successfully!\n\nSaved to: {filename}")
            
            # Ask to open
            if messagebox.askyesno("Open PDF", "Would you like to open the PDF now?"):
                os.startfile(filename)
                
        except Exception as e:
            self.status_label.config(text="Error generating PDF", fg='#e74c3c')
            messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")
    
    def create_pdf(self, filename):
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Header
        story.append(Paragraph("TAX INVOICE", styles['Title']))
        story.append(Paragraph(f"Invoice No: {self.invoice_no.get()}", styles['Normal']))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Customer details
        story.append(Paragraph("Bill To:", styles['Heading2']))
        story.append(Paragraph(self.customer_vars['customer_name'].get(), styles['Normal']))
        story.append(Paragraph(self.customer_address.get('1.0', tk.END).strip(), styles['Normal']))
        if self.customer_vars['customer_email'].get():
            story.append(Paragraph(f"Email: {self.customer_vars['customer_email'].get()}", styles['Normal']))
        if self.customer_vars['customer_phone'].get():
            story.append(Paragraph(f"Phone: {self.customer_vars['customer_phone'].get()}", styles['Normal']))
        if self.customer_vars['customer_gstin'].get():
            story.append(Paragraph(f"GSTIN: {self.customer_vars['customer_gstin'].get()}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Items table
        table_data = [['S.No', 'Description', 'Qty', 'Rate', 'Amount', 'GST%', 'GST Amt', 'Total']]
        
        for i, item in enumerate(self.items, 1):
            table_data.append([
                str(i),
                item['description'],
                f"{item['quantity']:.1f}",
                f"Rs.{item['rate']:.2f}",
                f"Rs.{item['amount']:.2f}",
                f"{item['gst_rate']:.0f}%",
                f"Rs.{item['gst_amount']:.2f}",
                f"Rs.{item['total']:.2f}"
            ])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        # Totals
        subtotal = sum(item['amount'] for item in self.items)
        total_gst = sum(item['gst_amount'] for item in self.items)
        discount_rate = float(self.discount.get() or 0)
        discount_amount = subtotal * discount_rate / 100
        grand_total = subtotal + total_gst - discount_amount
        
        totals_data = [
            ['Subtotal:', f"Rs. {subtotal:.2f}"],
            ['Total GST:', f"Rs. {total_gst:.2f}"],
            ['Discount:', f"Rs. {discount_amount:.2f}"],
            ['Grand Total:', f"Rs. {grand_total:.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[4*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
        ]))
        
        story.append(totals_table)
        
        # Notes
        notes_text = self.notes.get('1.0', tk.END).strip()
        if notes_text:
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(f"Notes: {notes_text}", styles['Normal']))
        
        doc.build(story)

def main():
    root = tk.Tk()
    app = InvoiceApp(root)
    
    # Bind discount change to update totals
    app.discount.trace('w', lambda *args: app.update_totals())
    
    root.mainloop()

if __name__ == '__main__':
    main()