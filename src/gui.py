import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta
import threading
from .invoice_generator import InvoiceGenerator
from .models import Invoice, Customer, InvoiceItem
from decimal import Decimal

class InvoiceGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Invoice Generator")
        self.root.geometry("800x600")
        
        self.generator = None
        self.config_path = "config/settings.json"
        
        self.setup_ui()
        self.load_generator()
    
    def setup_ui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Batch Generation Tab
        self.batch_frame = ttk.Frame(notebook)
        notebook.add(self.batch_frame, text="Batch Generation")
        self.setup_batch_tab()
        
        # Single Invoice Tab
        self.single_frame = ttk.Frame(notebook)
        notebook.add(self.single_frame, text="Single Invoice")
        self.setup_single_tab()
        
        # Settings Tab
        self.settings_frame = ttk.Frame(notebook)
        notebook.add(self.settings_frame, text="Settings")
        self.setup_settings_tab()
    
    def setup_batch_tab(self):
        # Date Range Selection
        date_frame = ttk.LabelFrame(self.batch_frame, text="Date Range", padding=10)
        date_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.start_date = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        ttk.Entry(date_frame, textvariable=self.start_date, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(date_frame, text="End Date:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.end_date = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(date_frame, textvariable=self.end_date, width=15).grid(row=0, column=3, padx=5)
        
        # Quick date buttons
        quick_frame = ttk.Frame(date_frame)
        quick_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        ttk.Button(quick_frame, text="Last 7 Days", 
                  command=lambda: self.set_date_range(7)).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="Last 30 Days", 
                  command=lambda: self.set_date_range(30)).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="Last 90 Days", 
                  command=lambda: self.set_date_range(90)).pack(side=tk.LEFT, padx=5)
        
        # Options
        options_frame = ttk.LabelFrame(self.batch_frame, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.send_email_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Send emails automatically", 
                       variable=self.send_email_var).pack(anchor=tk.W)
        
        # Generate Button
        ttk.Button(self.batch_frame, text="Generate Invoices", 
                  command=self.generate_batch_invoices).pack(pady=20)
        
        # Results
        results_frame = ttk.LabelFrame(self.batch_frame, text="Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.results_text = tk.Text(results_frame, height=15)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_single_tab(self):
        # Customer Information
        customer_frame = ttk.LabelFrame(self.single_frame, text="Customer Information", padding=10)
        customer_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(customer_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.customer_name = tk.StringVar()
        ttk.Entry(customer_frame, textvariable=self.customer_name, width=30).grid(row=0, column=1, padx=5)
        
        ttk.Label(customer_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.customer_email = tk.StringVar()
        ttk.Entry(customer_frame, textvariable=self.customer_email, width=30).grid(row=1, column=1, padx=5)
        
        ttk.Label(customer_frame, text="Address:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.customer_address = tk.Text(customer_frame, height=3, width=30)
        self.customer_address.grid(row=2, column=1, padx=5, pady=5)
        
        # Invoice Information
        invoice_frame = ttk.LabelFrame(self.single_frame, text="Invoice Information", padding=10)
        invoice_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(invoice_frame, text="Invoice Number:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.invoice_number = tk.StringVar(value=f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        ttk.Entry(invoice_frame, textvariable=self.invoice_number, width=20).grid(row=0, column=1, padx=5)
        
        # Items
        items_frame = ttk.LabelFrame(self.single_frame, text="Items", padding=10)
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Item entry
        item_entry_frame = ttk.Frame(items_frame)
        item_entry_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(item_entry_frame, text="Description:").grid(row=0, column=0, padx=5)
        self.item_desc = tk.StringVar()
        ttk.Entry(item_entry_frame, textvariable=self.item_desc, width=25).grid(row=0, column=1, padx=5)
        
        ttk.Label(item_entry_frame, text="Qty:").grid(row=0, column=2, padx=5)
        self.item_qty = tk.StringVar(value="1")
        ttk.Entry(item_entry_frame, textvariable=self.item_qty, width=5).grid(row=0, column=3, padx=5)
        
        ttk.Label(item_entry_frame, text="Price:").grid(row=0, column=4, padx=5)
        self.item_price = tk.StringVar()
        ttk.Entry(item_entry_frame, textvariable=self.item_price, width=10).grid(row=0, column=5, padx=5)
        
        ttk.Button(item_entry_frame, text="Add Item", 
                  command=self.add_item).grid(row=0, column=6, padx=5)
        
        # Items list
        self.items_listbox = tk.Listbox(items_frame, height=8)
        self.items_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Generate single invoice button
        single_button_frame = ttk.Frame(self.single_frame)
        single_button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.send_single_email_var = tk.BooleanVar()
        ttk.Checkbutton(single_button_frame, text="Send email", 
                       variable=self.send_single_email_var).pack(side=tk.LEFT)
        
        ttk.Button(single_button_frame, text="Generate Invoice", 
                  command=self.generate_single_invoice).pack(side=tk.RIGHT)
    
    def setup_settings_tab(self):
        settings_frame = ttk.LabelFrame(self.settings_frame, text="Configuration", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(settings_frame, text="Config File:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.config_path_var = tk.StringVar(value=self.config_path)
        ttk.Entry(settings_frame, textvariable=self.config_path_var, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(settings_frame, text="Browse", 
                  command=self.browse_config).grid(row=0, column=2, padx=5)
        
        ttk.Button(settings_frame, text="Reload Configuration", 
                  command=self.load_generator).grid(row=1, column=0, pady=10)
        
        ttk.Button(settings_frame, text="Validate Configuration", 
                  command=self.validate_config).grid(row=1, column=1, pady=10)
        
        ttk.Button(settings_frame, text="Test Email", 
                  command=self.test_email).grid(row=1, column=2, pady=10)
        
        # Status
        self.status_text = tk.Text(self.settings_frame, height=20)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def set_date_range(self, days):
        end = datetime.now()
        start = end - timedelta(days=days)
        self.start_date.set(start.strftime('%Y-%m-%d'))
        self.end_date.set(end.strftime('%Y-%m-%d'))
    
    def load_generator(self):
        try:
            self.config_path = self.config_path_var.get()
            self.generator = InvoiceGenerator(self.config_path)
            self.log_status("Configuration loaded successfully")
        except Exception as e:
            self.log_status(f"Error loading configuration: {e}")
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def browse_config(self):
        filename = filedialog.askopenfilename(
            title="Select Configuration File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.config_path_var.set(filename)
    
    def generate_batch_invoices(self):
        if not self.generator:
            messagebox.showerror("Error", "Please load configuration first")
            return
        
        try:
            start_date = datetime.strptime(self.start_date.get(), '%Y-%m-%d')
            end_date = datetime.strptime(self.end_date.get(), '%Y-%m-%d')
            send_email = self.send_email_var.get()
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Generating invoices...\n")
            self.root.update()
            
            # Run in thread to prevent UI freezing
            thread = threading.Thread(
                target=self._batch_generation_thread,
                args=(start_date, end_date, send_email)
            )
            thread.daemon = True
            thread.start()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date format: {e}")
    
    def _batch_generation_thread(self, start_date, end_date, send_email):
        try:
            successful, errors = self.generator.generate_invoices(start_date, end_date, send_email)
            
            result_text = f"\n✅ Successfully generated {len(successful)} invoices:\n"
            for pdf_path in successful:
                result_text += f"   📄 {pdf_path}\n"
            
            if errors:
                result_text += f"\n❌ {len(errors)} errors occurred:\n"
                for error in errors:
                    result_text += f"   • {error}\n"
            
            self.root.after(0, lambda: self.results_text.insert(tk.END, result_text))
            
        except Exception as e:
            error_text = f"\n❌ Error: {e}\n"
            self.root.after(0, lambda: self.results_text.insert(tk.END, error_text))
    
    def add_item(self):
        desc = self.item_desc.get().strip()
        qty = self.item_qty.get().strip()
        price = self.item_price.get().strip()
        
        if not desc or not qty or not price:
            messagebox.showerror("Error", "Please fill all item fields")
            return
        
        try:
            qty_int = int(qty)
            price_float = float(price)
            total = qty_int * price_float
            
            item_text = f"{desc} | Qty: {qty_int} | Price: Rs.{price_float:.2f} | Total: Rs.{total:.2f}"
            self.items_listbox.insert(tk.END, item_text)
            
            # Clear fields
            self.item_desc.set("")
            self.item_qty.set("1")
            self.item_price.set("")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or price")
    
    def generate_single_invoice(self):
        if not self.generator:
            messagebox.showerror("Error", "Please load configuration first")
            return
        
        try:
            # Validate inputs
            if not self.customer_name.get().strip():
                messagebox.showerror("Error", "Customer name is required")
                return
            
            if not self.customer_email.get().strip():
                messagebox.showerror("Error", "Customer email is required")
                return
            
            if self.items_listbox.size() == 0:
                messagebox.showerror("Error", "At least one item is required")
                return
            
            # Create customer
            customer = Customer(
                name=self.customer_name.get().strip(),
                email=self.customer_email.get().strip(),
                address=self.customer_address.get(1.0, tk.END).strip()
            )
            
            # Create items
            items = []
            for i in range(self.items_listbox.size()):
                item_text = self.items_listbox.get(i)
                # Parse item text (simple parsing)
                parts = item_text.split(" | ")
                desc = parts[0]
                qty = int(parts[1].split(": ")[1])
                price = float(parts[2].split(": Rs.")[1])
                
                items.append(InvoiceItem(
                    description=desc,
                    quantity=qty,
                    unit_price=Decimal(str(price))
                ))
            
            # Create invoice
            invoice = Invoice(
                invoice_number=self.invoice_number.get().strip(),
                customer=customer,
                items=items,
                issue_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=30)
            )
            
            # Generate invoice
            send_email = self.send_single_email_var.get()
            pdf_path = self.generator.generate_single_invoice(invoice, send_email)
            
            messagebox.showinfo("Success", f"Invoice generated: {pdf_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate invoice: {e}")
    
    def validate_config(self):
        if not self.generator:
            messagebox.showerror("Error", "Please load configuration first")
            return
        
        issues = self.generator.validate_configuration()
        if not issues:
            self.log_status("✅ Configuration is valid")
        else:
            self.log_status("❌ Configuration issues found:")
            for issue in issues:
                self.log_status(f"   • {issue}")
    
    def test_email(self):
        if not self.generator:
            messagebox.showerror("Error", "Please load configuration first")
            return
        
        if self.generator.test_email_connection():
            self.log_status("✅ Email connection successful")
        else:
            self.log_status("❌ Email connection failed")
    
    def log_status(self, message):
        self.status_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.status_text.see(tk.END)

def main():
    root = tk.Tk()
    app = InvoiceGeneratorGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()