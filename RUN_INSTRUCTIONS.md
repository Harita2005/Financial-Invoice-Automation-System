# Invoice Generator - Run Instructions

## Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup System
```bash
python setup.py
```

### 3. Create Sample Invoice
```bash
python create_sample_invoice.py
```

### 4. View Generated Invoice
Check the `output/preview/` folder for your sample PDF invoice.

---

## Detailed Setup Instructions

### Step 1: Environment Setup

**Option A: Using Virtual Environment (Recommended)**
```bash
# Create virtual environment
python -m venv invoice_env

# Activate virtual environment
# Windows:
invoice_env\Scripts\activate
# macOS/Linux:
source invoice_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Option B: Global Installation**
```bash
pip install -r requirements.txt
```

### Step 2: Configuration

1. **Update Company Information**
   ```bash
   # Edit config/settings.json
   notepad config/settings.json  # Windows
   nano config/settings.json     # Linux/macOS
   ```

2. **Add Your Logo**
   - Replace `templates/logo.png` with your company logo
   - Recommended size: 200x100 pixels

3. **Configure Database** (Optional for testing)
   - For MySQL: Update database credentials in config
   - For MongoDB: Update connection settings

### Step 3: Database Setup (Optional)

**For MySQL:**
```bash
# Get database schema
python main.py setup

# Execute the provided SQL commands in your MySQL database
mysql -u root -p your_database < schema.sql
```

**For MongoDB:**
```bash
# Import sample data
mongoimport --db invoice_db --collection customers --file data/sample_data.json --jsonArray
```

### Step 4: Test the System

1. **Validate Configuration**
   ```bash
   python main.py validate
   ```

2. **Create Sample Invoice**
   ```bash
   python create_sample_invoice.py
   ```

3. **Test Email (Optional)**
   ```bash
   python main.py test-email
   ```

---

## Usage Examples

### GUI Mode (Easiest)
```bash
python main.py
```
- Use the graphical interface to generate invoices
- Select date ranges, configure options
- View results in real-time

### CLI Mode (Advanced)

**Generate invoices for last 30 days:**
```bash
python main.py generate --days 30
```

**Generate with email sending:**
```bash
python main.py generate --days 7 --send-email
```

**Generate for specific date range:**
```bash
python main.py generate --start-date 2024-01-01 --end-date 2024-01-31
```

**Create single sample invoice:**
```bash
python main.py create-sample \
  --invoice-number "INV-001" \
  --customer-name "Test Customer" \
  --customer-email "test@example.com" \
  --customer-address "123 Test Street" \
  --item-desc "Consulting Services" \
  --unit-price 150.00 \
  --send-email
```

### Programmatic Usage

```python
from src.invoice_generator import InvoiceGenerator
from src.models import Invoice, Customer, InvoiceItem
from datetime import datetime, timedelta
from decimal import Decimal

# Initialize
generator = InvoiceGenerator('config/settings.json')

# Create invoice
customer = Customer(
    name="Acme Corp",
    email="billing@acme.com",
    address="123 Business Ave"
)

item = InvoiceItem(
    description="Web Development",
    quantity=10,
    unit_price=Decimal('125.00')
)

invoice = Invoice(
    invoice_number="INV-001",
    customer=customer,
    items=[item],
    issue_date=datetime.now(),
    due_date=datetime.now() + timedelta(days=30)
)

# Generate PDF
pdf_path = generator.generate_single_invoice(invoice)
print(f"Invoice generated: {pdf_path}")
```

---

## File Structure After Setup

```
invoice-generator/
├── config/
│   └── settings.json          ✅ Your company settings
├── src/                       ✅ Source code
├── templates/
│   └── logo.png              ✅ Your company logo
├── output/
│   ├── preview/              ✅ Sample invoices
│   └── invoice_*.pdf         ✅ Generated invoices
├── logs/
│   └── invoice_generator.log ✅ System logs
├── data/                     ✅ Sample data
├── main.py                   ✅ Main application
├── create_sample_invoice.py  ✅ Sample generator
└── setup.py                  ✅ Setup script
```

---

## Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Solution: Install missing packages
pip install -r requirements.txt

# Or install individually:
pip install reportlab pymongo mysql-connector-python
```

**2. Configuration File Not Found**
```bash
# Solution: Run setup first
python setup.py
```

**3. Database Connection Failed**
```bash
# Solution: Check database settings in config/settings.json
# For testing, you can skip database setup and use sample invoice creation
```

**4. PDF Generation Error**
```bash
# Solution: Check output directory permissions
mkdir output
chmod 755 output
```

**5. Email Sending Failed**
```bash
# Solution: Update email settings in config/settings.json
# For Gmail, use app-specific password
# Enable "Less secure app access" if needed
```

### Getting Help

1. **Check Logs**
   ```bash
   tail -f logs/invoice_generator.log
   ```

2. **Validate Configuration**
   ```bash
   python main.py validate
   ```

3. **Test Individual Components**
   ```bash
   python main.py test-email
   python create_sample_invoice.py
   ```

---

## Production Deployment

### 1. Security Considerations
- Use environment variables for sensitive data
- Enable database SSL connections
- Use app-specific passwords for email
- Restrict file system permissions

### 2. Performance Optimization
- Use connection pooling for databases
- Enable PDF compression
- Implement batch processing limits
- Add caching for templates

### 3. Monitoring
- Set up log rotation
- Monitor disk space for output folder
- Track email delivery rates
- Monitor database performance

### 4. Backup Strategy
- Regular database backups
- Configuration file backups
- Generated invoice archives
- Log file retention policy

---

## Next Steps

1. **Customize for Your Business**
   - Update company information
   - Modify PDF templates
   - Adjust validation rules
   - Configure email templates

2. **Integrate with Your Systems**
   - Connect to existing database
   - Set up automated scheduling
   - Integrate with accounting software
   - Add API endpoints if needed

3. **Scale for Production**
   - Set up proper database
   - Configure email server
   - Implement monitoring
   - Add error handling

---

## Support

- 📖 Read the full README.md
- 🔧 Check CUSTOMIZATION.md for advanced setup
- 🐛 Create GitHub issues for bugs
- 💡 Submit feature requests

**Happy Invoicing! 🧾✨**