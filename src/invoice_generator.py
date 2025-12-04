import os
import logging
from datetime import datetime
from typing import List, Optional, Tuple
from .config_manager import ConfigManager
from .database import DatabaseManager
from .data_validator import DataValidator
from .pdf_generator import PDFGenerator
from .email_sender import EmailSender
from .models import Invoice

class InvoiceGenerator:
    def __init__(self, config_path: str = "config/settings.json"):
        self.config_manager = ConfigManager(config_path)
        self.db_manager = DatabaseManager(self.config_manager)
        self.validator = DataValidator()
        self.pdf_generator = PDFGenerator(self.config_manager)
        self.email_sender = EmailSender(self.config_manager)
        self._setup_logging()
        
    def _setup_logging(self):
        log_config = self.config_manager.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'logs/invoice_generator.log')
        
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def generate_invoices(self, start_date: datetime, end_date: datetime, 
                         send_email: bool = False) -> Tuple[List[str], List[str]]:
        """
        Generate invoices for billing records within date range
        Returns: (successful_invoices, errors)
        """
        successful_invoices = []
        errors = []
        
        try:
            # Connect to database
            self.db_manager.connect()
            
            # Retrieve billing records
            self.logger.info(f"Retrieving billing records from {start_date} to {end_date}")
            records = self.db_manager.get_billing_records(start_date, end_date)
            
            if not records:
                self.logger.warning("No billing records found for the specified date range")
                return [], ["No billing records found for the specified date range"]
            
            # Validate data and create invoices
            self.logger.info(f"Validating {len(records)} billing records")
            invoices, validation_errors = self.validator.validate_billing_records(records)
            errors.extend(validation_errors)
            
            # Generate PDFs for valid invoices
            for invoice in invoices:
                try:
                    pdf_path = self._process_single_invoice(invoice, send_email)
                    successful_invoices.append(pdf_path)
                    self.logger.info(f"Successfully processed invoice {invoice.invoice_number}")
                    
                except Exception as e:
                    error_msg = f"Failed to process invoice {invoice.invoice_number}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
            
            self.logger.info(f"Batch processing complete. Success: {len(successful_invoices)}, Errors: {len(errors)}")
            
        except Exception as e:
            error_msg = f"Batch processing failed: {str(e)}"
            errors.append(error_msg)
            self.logger.error(error_msg)
            
        finally:
            self.db_manager.close()
        
        return successful_invoices, errors
    
    def _process_single_invoice(self, invoice: Invoice, send_email: bool = False) -> str:
        """Process a single invoice: generate PDF, save metadata, optionally send email"""
        
        # Generate PDF
        pdf_path = self.pdf_generator.generate_invoice(invoice)
        
        # Save metadata to database
        self.db_manager.save_invoice_metadata(invoice, pdf_path)
        
        # Send email if requested
        if send_email:
            email_sent = self.email_sender.send_invoice(invoice, pdf_path)
            if email_sent:
                self.logger.info(f"Email sent for invoice {invoice.invoice_number}")
            else:
                self.logger.warning(f"Failed to send email for invoice {invoice.invoice_number}")
        
        return pdf_path
    
    def generate_single_invoice(self, invoice: Invoice, send_email: bool = False) -> str:
        """Generate a single invoice from Invoice object"""
        try:
            self.db_manager.connect()
            pdf_path = self._process_single_invoice(invoice, send_email)
            self.logger.info(f"Single invoice generated: {pdf_path}")
            return pdf_path
        finally:
            self.db_manager.close()
    
    def test_email_connection(self) -> bool:
        """Test email server connection"""
        return self.email_sender.test_connection()
    
    def get_invoice_preview(self, invoice: Invoice) -> str:
        """Generate invoice preview without saving to database"""
        preview_path = os.path.join("output", "preview", f"preview_{invoice.invoice_number}.pdf")
        return self.pdf_generator.generate_invoice(invoice, preview_path)
    
    def validate_configuration(self) -> List[str]:
        """Validate system configuration"""
        issues = []
        
        # Check required directories
        required_dirs = ['output', 'logs', 'templates']
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                try:
                    os.makedirs(dir_name, exist_ok=True)
                except Exception as e:
                    issues.append(f"Cannot create directory {dir_name}: {e}")
        
        # Check database connection
        try:
            self.db_manager.connect()
            self.db_manager.close()
        except Exception as e:
            issues.append(f"Database connection failed: {e}")
        
        # Check email configuration if enabled
        if self.config_manager.get('email.enabled', False):
            if not self.email_sender.test_connection():
                issues.append("Email server connection failed")
        
        return issues