# Financial Invoice Automation System

A complete, production-ready invoice generator system built with Python that creates professional PDF invoices with multiple UI options and GST calculations.

##  Features

✅ **Multiple Professional UIs**: 3 different web interfaces  
✅ **Indian Rupee Support**: Complete Rs. currency integration  
✅ **GST Calculations**: Automatic tax calculations (0%, 5%, 12%, 18%, 28%)  
✅ **Professional PDFs**: Clean, downloadable invoice templates  
✅ **Real-time Calculations**: Live totals and validation  
✅ **Mobile Responsive**: Works on all devices  
✅ **No Database Required**: Works immediately  
✅ **Material Purchase Focus**: Specialized for business invoicing  

##  UI Options

### 1. Professional Colorful UI
```bash
python professional_ui_app.py
```
- Colorful gradient design
- Perfect alignment
- Section-based layout
- Professional icons

### 2. Best UI (Animated)
```bash
python best_ui_app.py
```
- Gradient animations
- Glass morphism effects
- Floating elements
- Modern styling

### 3. Modern Dark UI
```bash
python modern_ui_app.py
```
- Dark theme design
- Neon blue accents
- Card-based layout
- Professional look

## 📱 Quick Start

### 1. Installation
```bash
git clone https://github.com/Harita2005/Financial-Invoice-Automation-System.git
cd Financial-Invoice-Automation-System
pip install -r requirements.txt
```

### 2. Run Web Application
```bash
# Choose your preferred UI:
python professional_ui_app.py    # Colorful professional UI
python best_ui_app.py           # Animated gradient UI  
python modern_ui_app.py         # Dark theme UI
```

### 3. Access Application
Open browser: `http://localhost:5000`

##  Desktop & CLI Options

### Desktop GUI
```bash
python desktop_invoice_app.py
```

### Simple Material Invoice
```bash
python simple_material_invoice.py
```

### Interactive CLI
```bash
python material_invoice_generator.py
```

## 📋 Invoice Features

- **Customer Management**: Name, email, phone, GSTIN, address
- **Multiple Items**: Add/remove items dynamically
- **GST Rates**: 0%, 5%, 12%, 18%, 28% support
- **Automatic Calculations**: Subtotal + GST + Discount = Total
- **Professional PDF**: Downloadable business invoices
- **Indian Format**: Rs. currency, GST compliance
- **Terms & Conditions**: Custom notes support

##  Project Structure

```
Financial-Invoice-Automation-System/
├── Web Applications/
│   ├── professional_ui_app.py     # Colorful professional UI
│   ├── best_ui_app.py            # Animated gradient UI
│   ├── modern_ui_app.py          # Dark theme UI
│   └── templates/                # HTML templates
├── Desktop Applications/
│   ├── desktop_invoice_app.py    # GUI application
│   └── simple_material_invoice.py # CLI generator
├── Core System/
│   ├── src/                      # Core modules
│   ├── config/                   # Configuration
│   └── data/                     # Sample data
├── Documentation/
│   ├── README.md                 # This file
│   ├── CUSTOMIZATION.md          # Customization guide
│   └── RUN_INSTRUCTIONS.md       # Detailed instructions
└── output/                       # Generated PDFs
```

##  Perfect For

- **Material Suppliers**: Construction, hardware, industrial
- **Service Providers**: Consulting, maintenance, repairs  
- **Small Businesses**: Retail, wholesale, trading
- **Freelancers**: Individual service providers
- **Contractors**: Project-based billing

## 🔧 Customization

### Company Details
Edit `config/settings.json`:
```json
{
  "company": {
    "name": "Your Company Name",
    "address": "Your Address",
    "phone": "+91 XXXXX XXXXX",
    "email": "your@email.com"
  }
}
```

### UI Customization
- Modify HTML templates in `templates/`
- Update CSS styles for colors/layout
- Add custom branding elements

##  Sample Invoice Output

- **Invoice Number**: Auto-generated (INV-YYYYMMDD-XXX)
- **Customer Details**: Complete billing information
- **Items Table**: Description, Qty, Rate, GST%, Amount
- **GST Breakdown**: Separate calculation by rate
- **Totals**: Subtotal, GST, Discount, Grand Total
- **Professional Format**: Business-ready PDF

##  Key Benefits

✅ **Immediate Use** - No database setup required  
✅ **Multiple UIs** - Choose your preferred interface  
✅ **GST Compliant** - Indian tax regulations  
✅ **Professional Output** - Business-ready invoices  
✅ **Mobile Friendly** - Responsive design  
✅ **Easy Customization** - Modify for any business  
✅ **Real-time Calculations** - Live totals update  
✅ **Download Ready** - PDF generation guaranteed  

##  Support

- **GitHub Issues**: Report bugs or request features
- **Documentation**: Check included guides
- **Customization**: Follow CUSTOMIZATION.md

##  License

MIT License - Free for commercial and personal use

---

**🎉 Ready to generate professional invoices with beautiful UIs!**

**Repository**: https://github.com/Harita2005/Financial-Invoice-Automation-System
