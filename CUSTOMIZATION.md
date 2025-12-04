# Customization Guide

This guide explains how to customize the Invoice Generator System for your specific company needs.

## 1. Company Information

### Update Basic Details
Edit `config/settings.json`:

```json
{
  "company": {
    "name": "Your Company Name",
    "address": "Your Address\nCity, State ZIP",
    "phone": "+1 (XXX) XXX-XXXX",
    "email": "billing@yourcompany.com",
    "website": "www.yourcompany.com",
    "logo_path": "templates/logo.png"
  }
}
```

### Add Company Logo
1. Replace `templates/logo.png` with your company logo
2. Recommended size: 200x100 pixels
3. Supported formats: PNG, JPG
4. Update `logo_path` in config if using different filename

## 2. Invoice Customization

### Currency and Rates
```json
{
  "invoice": {
    "tax_rate": 0.08,        // 8% tax rate
    "discount_rate": 0.05,   // 5% default discount
    "currency": "USD",
    "currency_symbol": "$",
    "invoice_prefix": "INV",
    "date_format": "%Y-%m-%d"
  }
}
```

### PDF Template Styling
Edit `src/pdf_generator.py`:

#### Colors
```python
# Change company name color
self.styles.add(ParagraphStyle(
    name='CompanyName',
    textColor=colors.darkblue,  # Change to your brand color
    # ... other properties
))

# Change invoice title color
self.styles.add(ParagraphStyle(
    name='InvoiceTitle', 
    textColor=colors.darkred,   # Change to your brand color
    # ... other properties
))
```

#### Fonts and Sizes
```python
# Update font sizes
self.styles.add(ParagraphStyle(
    name='CompanyName',
    fontSize=24,  # Adjust size
    # ... other properties
))
```

#### Layout Modifications
```python
# Modify header layout in _create_header method
def _create_header(self):
    elements = []
    
    # Add additional company information
    company_details = f"""
    {self.company_info['address']}<br/>
    Phone: {self.company_info['phone']}<br/>
    Email: {self.company_info['email']}<br/>
    Website: {self.company_info['website']}<br/>
    Tax ID: YOUR-TAX-ID<br/>          # Add tax ID
    License: YOUR-LICENSE-NUMBER      # Add license number
    """
    # ... rest of method
```

## 3. Database Customization

### MySQL Schema Modifications
If your existing database has different table names or fields:

Edit `src/database.py`:

```python
def _get_mysql_records(self, start_date, end_date):
    cursor = self.connection.cursor(dictionary=True)
    
    # Modify query to match your schema
    query = """
    SELECT b.*, c.customer_name as name, c.customer_email as email, 
           c.customer_address as address, c.customer_phone as phone,
           bi.item_description as description, bi.qty as quantity, 
           bi.price as unit_price
    FROM your_billing_table b          -- Change table name
    JOIN your_customers_table c ON b.customer_id = c.customer_id
    JOIN your_items_table bi ON b.billing_id = bi.billing_id
    WHERE b.billing_date BETWEEN %s AND %s
    ORDER BY b.billing_id, bi.item_id
    """
    # ... rest of method
```

### MongoDB Collection Names
```python
def _get_mongodb_records(self, start_date, end_date):
    collection = self.connection['your_billing_collection']  # Change collection name
    # ... rest of method
```

## 4. Validation Rules

### Custom Business Rules
Edit `src/data_validator.py`:

```python
def _validate_customer(self, record):
    # Add custom validation rules
    required_fields = ['name', 'email', 'address', 'tax_id']  # Add tax_id
    
    # Custom email domain validation
    email = record['email'].strip().lower()
    if not email.endswith(('@company.com', '@business.org')):
        raise ValueError(f"Email must be from approved domains: {email}")
    
    # Custom phone format validation
    phone = record.get('phone', '')
    if phone and not re.match(r'^\+1 \(\d{3}\) \d{3}-\d{4}$', phone):
        raise ValueError(f"Phone must be in format: +1 (XXX) XXX-XXXX")
    
    # ... rest of validation
```

### Item Validation
```python
def _validate_items(self, record_data):
    # Add minimum/maximum price validation
    for record in record_data:
        unit_price = Decimal(str(record.get('unit_price', 0)))
        
        # Custom price range validation
        if unit_price < Decimal('1.00'):
            raise ValueError(f"Unit price too low: {unit_price}")
        if unit_price > Decimal('10000.00'):
            raise ValueError(f"Unit price too high: {unit_price}")
    
    # ... rest of validation
```

## 5. Email Templates

### Custom Email Content
Edit `src/email_sender.py`:

```python
def _create_email_body(self, invoice):
    # Customize email template
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background-color: #your-brand-color; color: white; padding: 20px; }}
            .content {{ padding: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{self.company_info['name']}</h1>
        </div>
        
        <div class="content">
            <h2>Invoice #{invoice.invoice_number}</h2>
            
            <p>Dear {invoice.customer.name},</p>
            
            <p>Your custom message here...</p>
            
            <!-- Add custom sections -->
            <h3>Payment Instructions:</h3>
            <p>Please pay via:</p>
            <ul>
                <li>Bank Transfer: Account XXX-XXX-XXXX</li>
                <li>Check: Mail to our address</li>
                <li>Online: www.yourcompany.com/pay</li>
            </ul>
            
            <!-- ... rest of template -->
        </div>
    </body>
    </html>
    """
    return body
```

### Email Settings
```json
{
  "email": {
    "enabled": true,
    "smtp_server": "smtp.yourcompany.com",  // Use your SMTP server
    "smtp_port": 587,
    "username": "invoices@yourcompany.com",
    "password": "your-app-password",
    "from_email": "invoices@yourcompany.com"
  }
}
```

## 6. Additional Fields

### Add Custom Invoice Fields
Edit `src/models.py`:

```python
class Invoice(BaseModel):
    # Existing fields...
    
    # Add custom fields
    project_code: Optional[str] = None
    purchase_order: Optional[str] = None
    payment_terms: str = "Net 30"
    sales_rep: Optional[str] = None
    
    # Custom validation for new fields
    @validator('project_code')
    def validate_project_code(cls, v):
        if v and not re.match(r'^PROJ-\d{4}-\d{3}$', v):
            raise ValueError('Project code must be in format: PROJ-YYYY-XXX')
        return v
```

### Update PDF Template for New Fields
Edit `src/pdf_generator.py`:

```python
def _create_info_section(self, invoice):
    # Add custom fields to invoice details
    invoice_details = f"""
    Issue Date: {invoice.issue_date.strftime(self.invoice_settings['date_format'])}<br/>
    Due Date: {invoice.due_date.strftime(self.invoice_settings['date_format'])}<br/>
    Payment Terms: {invoice.payment_terms}<br/>
    """
    
    # Add project code if present
    if invoice.project_code:
        invoice_details += f"Project Code: {invoice.project_code}<br/>"
    
    # Add purchase order if present
    if invoice.purchase_order:
        invoice_details += f"PO Number: {invoice.purchase_order}<br/>"
    
    # ... rest of method
```

## 7. Multi-Language Support

### Add Language Configuration
```json
{
  "localization": {
    "language": "en",
    "currency_position": "before",  // "before" or "after"
    "date_format": "%Y-%m-%d",
    "number_format": "US"  // "US", "EU", etc.
  }
}
```

### Language Templates
Create language files in `config/languages/`:

`config/languages/en.json`:
```json
{
  "invoice_title": "INVOICE",
  "bill_to": "Bill To:",
  "invoice_details": "Invoice Details:",
  "description": "Description",
  "quantity": "Qty",
  "unit_price": "Unit Price",
  "total": "Total",
  "subtotal": "Subtotal:",
  "tax": "Tax",
  "discount": "Discount",
  "total_amount": "Total Amount:",
  "thank_you": "Thank you for your business!"
}
```

## 8. Integration with Existing Systems

### API Integration
Create `src/api_integration.py`:

```python
import requests
from typing import List, Dict, Any

class ERPIntegration:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
    
    def fetch_billing_data(self, start_date, end_date) -> List[Dict[str, Any]]:
        """Fetch billing data from your ERP system"""
        headers = {'Authorization': f'Bearer {self.api_key}'}
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
        
        response = requests.get(
            f"{self.api_url}/billing-records",
            headers=headers,
            params=params
        )
        
        return response.json()
    
    def update_invoice_status(self, invoice_number: str, status: str):
        """Update invoice status in ERP system"""
        headers = {'Authorization': f'Bearer {self.api_key}'}
        data = {'status': status}
        
        response = requests.put(
            f"{self.api_url}/invoices/{invoice_number}/status",
            headers=headers,
            json=data
        )
        
        return response.status_code == 200
```

## 9. Performance Optimization

### Batch Processing Configuration
```json
{
  "performance": {
    "batch_size": 100,           // Process invoices in batches
    "max_concurrent_emails": 5,  // Limit concurrent email sending
    "pdf_compression": true,     // Enable PDF compression
    "cache_templates": true      // Cache PDF templates
  }
}
```

### Database Connection Pooling
Edit `src/database.py`:

```python
import mysql.connector.pooling

class DatabaseManager:
    def __init__(self, config_manager):
        # ... existing code ...
        
        # Add connection pooling
        if self.db_type == 'mysql':
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="invoice_pool",
                pool_size=5,
                **mysql_config
            )
    
    def get_connection(self):
        if self.db_type == 'mysql':
            return self.pool.get_connection()
        # ... rest of method
```

## 10. Testing Your Customizations

### Create Test Configuration
Create `config/test_settings.json` with test database settings.

### Run Tests
```bash
# Test configuration
python main.py validate --config config/test_settings.json

# Test with sample data
python create_sample_invoice.py

# Test email functionality
python main.py test-email --config config/test_settings.json
```

### Validation Checklist
- [ ] Company information displays correctly
- [ ] Logo appears in PDF
- [ ] Tax calculations are accurate
- [ ] Email templates render properly
- [ ] Database queries return expected data
- [ ] Custom validation rules work
- [ ] PDF styling matches requirements
- [ ] All custom fields appear correctly

## Support

For additional customization help:
1. Check the main README.md
2. Review the source code comments
3. Create an issue on GitHub
4. Test changes in a development environment first

Remember to backup your configuration and customizations before making major changes!