# Invoice Generator System

A complete, production-ready invoice generator system built with Python that creates professional PDF invoices from database records.

## Features

✅ **Database Integration**: Supports both MySQL and MongoDB  
✅ **Data Validation**: Comprehensive validation with error handling  
✅ **Professional PDFs**: Clean, customizable invoice templates  
✅ **Batch Processing**: Generate multiple invoices at once  
✅ **Email Support**: Automatic email delivery with PDF attachments  
✅ **CLI & GUI**: Command-line and graphical user interfaces  
✅ **Configurable**: Easy customization via JSON configuration  
✅ **Logging**: Comprehensive logging and error tracking  

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd invoice-generator

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Edit `config/settings.json` to customize:
- Company information
- Database connection
- Tax rates and currency
- Email settings
- Output preferences

### 3. Database Setup

**For MySQL:**
```bash
python main.py setup
# Then execute the provided SQL commands in your MySQL database
```

**For MongoDB:**
```bash
# Import sample data
mongoimport --db invoice_db --collection customers --file data/sample_data.json --jsonArray
```

### 4. Run the Application

**GUI Mode:**
```bash
python main.py
```

**CLI Mode:**
```bash
# Generate invoices for last 30 days
python main.py generate --days 30

# Generate with email sending
python main.py generate --days 7 --send-email

# Create a sample invoice
python main.py create-sample --invoice-number "INV-001" --customer-name "Test Customer" --customer-email "test@example.com" --customer-address "123 Test St" --item-desc "Consulting" --unit-price 100.00
```

## Project Structure

```
invoice-generator/
├── src/                    # Source code
│   ├── config_manager.py   # Configuration management
│   ├── models.py          # Data models with validation
│   ├── database.py        # Database connections (MySQL/MongoDB)
│   ├── data_validator.py  # Data validation logic
│   ├── pdf_generator.py   # PDF generation with templates
│   ├── email_sender.py    # Email functionality
│   ├── invoice_generator.py # Main orchestrator
│   ├── cli.py            # Command-line interface
│   └── gui.py            # Graphical user interface
├── config/
│   └── settings.json     # Configuration file
├── templates/
│   └── logo.png         # Company logo placeholder
├── data/                # Sample data
├── output/              # Generated PDFs
├── logs/               # Log files
├── requirements.txt    # Python dependencies
├── main.py            # Main entry point
└── README.md          # This file
```

## Configuration

### Company Settings
```json
{
  "company": {
    "name": "Your Company Name",
    "address": "123 Business Street\nCity, State 12345",
    "phone": "+1 (555) 123-4567",
    "email": "billing@yourcompany.com",
    "website": "www.yourcompany.com",
    "logo_path": "templates/logo.png"
  }
}
```

### Invoice Settings
```json
{
  "invoice": {
    "tax_rate": 0.08,
    "discount_rate": 0.05,
    "currency": "USD",
    "currency_symbol": "$",
    "invoice_prefix": "INV",
    "date_format": "%Y-%m-%d"
  }
}
```

### Database Configuration
```json
{
  "database": {
    "type": "mysql",
    "mysql": {
      "host": "localhost",
      "port": 3306,
      "database": "invoice_db",
      "username": "root",
      "password": "password"
    }
  }
}
```

## Usage Examples

### CLI Commands

```bash
# Validate configuration
python main.py validate

# Test email connection
python main.py test-email

# Generate invoices for date range
python main.py generate --start-date 2024-01-01 --end-date 2024-01-31

# Generate with email sending
python main.py generate --days 30 --send-email
```

### Programmatic Usage

```python
from src.invoice_generator import InvoiceGenerator
from src.models import Invoice, Customer, InvoiceItem
from datetime import datetime, timedelta
from decimal import Decimal

# Initialize generator
generator = InvoiceGenerator('config/settings.json')

# Create a sample invoice
customer = Customer(
    name="Acme Corp",
    email="billing@acme.com", 
    address="123 Business Ave\nNew York, NY 10001"
)

item = InvoiceItem(
    description="Consulting Services",
    quantity=10,
    unit_price=Decimal('150.00')
)

invoice = Invoice(
    invoice_number="INV-001",
    customer=customer,
    items=[item],
    issue_date=datetime.now(),
    due_date=datetime.now() + timedelta(days=30)
)

# Generate PDF
pdf_path = generator.generate_single_invoice(invoice, send_email=True)
print(f"Invoice generated: {pdf_path}")
```

## Customization for Other Companies

### 1. Update Company Information
Edit `config/settings.json`:
- Change company name, address, contact info
- Update logo path to your company logo
- Adjust tax rates and currency

### 2. Customize PDF Template
Modify `src/pdf_generator.py`:
- Update colors and fonts
- Change layout and styling
- Add additional fields or sections

### 3. Database Schema
Adapt database queries in `src/database.py` to match your existing schema:
- Update table/collection names
- Modify field mappings
- Adjust query logic

### 4. Validation Rules
Customize validation in `src/data_validator.py`:
- Add business-specific validation rules
- Modify required fields
- Update data formats

### 5. Email Templates
Modify email templates in `src/email_sender.py`:
- Update email subject and body
- Add company branding
- Include additional information

## Database Schema

### MySQL Tables
```sql
-- Customers table
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(50)
);

-- Billing records table  
CREATE TABLE billing_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    invoice_number VARCHAR(100),
    billing_date DATE NOT NULL,
    issue_date DATE,
    due_date DATE,
    tax_rate DECIMAL(5,4) DEFAULT 0.08,
    discount_rate DECIMAL(5,4) DEFAULT 0.00,
    notes TEXT
);

-- Billing items table
CREATE TABLE billing_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    billing_record_id INT NOT NULL,
    description VARCHAR(500) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);
```

### MongoDB Collections
- `customers`: Customer information
- `billing_records`: Invoice header data
- `billing_items`: Line items for each invoice
- `invoice_metadata`: Generated invoice tracking

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check database credentials in config
   - Ensure database server is running
   - Verify network connectivity

2. **PDF Generation Error**
   - Check output directory permissions
   - Verify ReportLab installation
   - Ensure logo file exists and is readable

3. **Email Sending Failed**
   - Verify SMTP settings
   - Check email credentials
   - Enable "Less secure app access" for Gmail

4. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path configuration
   - Verify virtual environment activation

### Logging

Check log files in the `logs/` directory for detailed error information:
```bash
tail -f logs/invoice_generator.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the configuration documentation

---

**Note**: This system is designed to be production-ready but should be tested thoroughly in your specific environment before deployment.