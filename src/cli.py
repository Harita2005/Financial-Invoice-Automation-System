import click
import os
from datetime import datetime, timedelta
from .invoice_generator import InvoiceGenerator
from .models import Invoice, Customer, InvoiceItem
from decimal import Decimal

@click.group()
def cli():
    """Invoice Generator CLI - Generate professional PDF invoices"""
    pass

@cli.command()
@click.option('--start-date', type=click.DateTime(formats=['%Y-%m-%d']), 
              help='Start date (YYYY-MM-DD)')
@click.option('--end-date', type=click.DateTime(formats=['%Y-%m-%d']), 
              help='End date (YYYY-MM-DD)')
@click.option('--days', type=int, help='Generate invoices for last N days')
@click.option('--send-email', is_flag=True, help='Send invoices via email')
@click.option('--config', default='config/settings.json', help='Configuration file path')
def generate(start_date, end_date, days, send_email, config):
    """Generate invoices for a date range"""
    
    # Determine date range
    if days:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
    elif not start_date or not end_date:
        click.echo("Please specify either --start-date and --end-date, or --days")
        return
    
    click.echo(f"Generating invoices from {start_date.date()} to {end_date.date()}")
    
    try:
        generator = InvoiceGenerator(config)
        successful, errors = generator.generate_invoices(start_date, end_date, send_email)
        
        click.echo(f"\nSuccessfully generated {len(successful)} invoices")
        for pdf_path in successful:
            click.echo(f"   {pdf_path}")
        
        if errors:
            click.echo(f"\n{len(errors)} errors occurred:")
            for error in errors:
                click.echo(f"   - {error}")
        
        if send_email:
            click.echo(f"\nEmail sending {'enabled' if send_email else 'disabled'}")
            
    except Exception as e:
        click.echo(f"Error: {e}")

@cli.command()
@click.option('--config', default='config/settings.json', help='Configuration file path')
def validate(config):
    """Validate system configuration"""
    try:
        generator = InvoiceGenerator(config)
        issues = generator.validate_configuration()
        
        if not issues:
            click.echo("Configuration is valid")
        else:
            click.echo("Configuration issues found:")
            for issue in issues:
                click.echo(f"   - {issue}")
                
    except Exception as e:
        click.echo(f"Error: {e}")

@cli.command()
@click.option('--config', default='config/settings.json', help='Configuration file path')
def test_email(config):
    """Test email server connection"""
    try:
        generator = InvoiceGenerator(config)
        
        if generator.test_email_connection():
            click.echo("Email connection successful")
        else:
            click.echo("Email connection failed")
            
    except Exception as e:
        click.echo(f"Error: {e}")

@cli.command()
@click.option('--invoice-number', required=True, help='Invoice number')
@click.option('--customer-name', required=True, help='Customer name')
@click.option('--customer-email', required=True, help='Customer email')
@click.option('--customer-address', required=True, help='Customer address')
@click.option('--item-desc', required=True, help='Item description')
@click.option('--quantity', type=int, default=1, help='Item quantity')
@click.option('--unit-price', type=float, required=True, help='Unit price')
@click.option('--send-email', is_flag=True, help='Send invoice via email')
@click.option('--config', default='config/settings.json', help='Configuration file path')
def create_sample(invoice_number, customer_name, customer_email, customer_address,
                 item_desc, quantity, unit_price, send_email, config):
    """Create a sample invoice"""
    try:
        # Create sample invoice
        customer = Customer(
            name=customer_name,
            email=customer_email,
            address=customer_address
        )
        
        item = InvoiceItem(
            description=item_desc,
            quantity=quantity,
            unit_price=Decimal(str(unit_price))
        )
        
        invoice = Invoice(
            invoice_number=invoice_number,
            customer=customer,
            items=[item],
            issue_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30)
        )
        
        generator = InvoiceGenerator(config)
        pdf_path = generator.generate_single_invoice(invoice, send_email)
        
        click.echo(f"Sample invoice created: {pdf_path}")
        
        if send_email:
            click.echo("Email sent successfully")
            
    except Exception as e:
        click.echo(f"Error: {e}")

@cli.command()
def setup():
    """Setup initial database tables (MySQL only)"""
    click.echo("Setting up database tables...")
    
    mysql_setup = """
    -- Create customers table
    CREATE TABLE IF NOT EXISTS customers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        address TEXT NOT NULL,
        phone VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create billing_records table
    CREATE TABLE IF NOT EXISTS billing_records (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NOT NULL,
        invoice_number VARCHAR(100),
        billing_date DATE NOT NULL,
        issue_date DATE,
        due_date DATE,
        tax_rate DECIMAL(5,4) DEFAULT 0.08,
        discount_rate DECIMAL(5,4) DEFAULT 0.00,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    );
    
    -- Create billing_items table
    CREATE TABLE IF NOT EXISTS billing_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        billing_record_id INT NOT NULL,
        description VARCHAR(500) NOT NULL,
        quantity INT NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (billing_record_id) REFERENCES billing_records(id)
    );
    
    -- Create invoice_metadata table
    CREATE TABLE IF NOT EXISTS invoice_metadata (
        id INT AUTO_INCREMENT PRIMARY KEY,
        invoice_number VARCHAR(100) NOT NULL,
        customer_name VARCHAR(255) NOT NULL,
        customer_email VARCHAR(255) NOT NULL,
        issue_date DATE NOT NULL,
        due_date DATE NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        pdf_path VARCHAR(500) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    click.echo("Execute the following SQL commands in your MySQL database:")
    click.echo("=" * 60)
    click.echo(mysql_setup)
    click.echo("=" * 60)

if __name__ == '__main__':
    cli()