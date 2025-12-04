import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
import logging
from .models import Invoice
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.email_settings = config_manager.get_email_settings()
        self.company_info = config_manager.get_company_info()
    
    def send_invoice(self, invoice: Invoice, pdf_path: str, 
                    additional_recipients: Optional[List[str]] = None) -> bool:
        if not self.email_settings.get('enabled', False):
            logger.info("Email sending is disabled")
            return False
        
        try:
            # Create message
            msg = self._create_message(invoice, additional_recipients or [])
            
            # Attach PDF
            self._attach_pdf(msg, pdf_path, invoice.invoice_number)
            
            # Send email
            self._send_message(msg)
            
            logger.info(f"Invoice email sent successfully to {invoice.customer.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send invoice email: {e}")
            return False
    
    def _create_message(self, invoice: Invoice, additional_recipients: List[str]) -> MIMEMultipart:
        msg = MIMEMultipart()
        
        # Email headers
        msg['From'] = self.email_settings['from_email']
        msg['To'] = invoice.customer.email
        
        if additional_recipients:
            msg['Cc'] = ', '.join(additional_recipients)
        
        msg['Subject'] = f"Invoice #{invoice.invoice_number} from {self.company_info['name']}"
        
        # Email body
        body = self._create_email_body(invoice)
        msg.attach(MIMEText(body, 'html'))
        
        return msg
    
    def _create_email_body(self, invoice: Invoice) -> str:
        currency_symbol = self.config.get('invoice.currency_symbol', '$')
        
        body = f"""
        <html>
        <body>
            <h2>Invoice from {self.company_info['name']}</h2>
            
            <p>Dear {invoice.customer.name},</p>
            
            <p>Please find attached your invoice #{invoice.invoice_number} for the amount of 
            <strong>{currency_symbol}{invoice.total_amount:.2f}</strong>.</p>
            
            <h3>Invoice Details:</h3>
            <ul>
                <li><strong>Invoice Number:</strong> {invoice.invoice_number}</li>
                <li><strong>Issue Date:</strong> {invoice.issue_date.strftime('%B %d, %Y')}</li>
                <li><strong>Due Date:</strong> {invoice.due_date.strftime('%B %d, %Y')}</li>
                <li><strong>Total Amount:</strong> {currency_symbol}{invoice.total_amount:.2f}</li>
            </ul>
            
            <p>If you have any questions about this invoice, please don't hesitate to contact us:</p>
            <ul>
                <li><strong>Email:</strong> {self.company_info['email']}</li>
                <li><strong>Phone:</strong> {self.company_info['phone']}</li>
            </ul>
            
            <p>Thank you for your business!</p>
            
            <p>Best regards,<br>
            {self.company_info['name']}<br>
            {self.company_info['email']}</p>
        </body>
        </html>
        """
        
        return body
    
    def _attach_pdf(self, msg: MIMEMultipart, pdf_path: str, invoice_number: str):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        with open(pdf_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        
        filename = f"invoice_{invoice_number}.pdf"
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}'
        )
        
        msg.attach(part)
    
    def _send_message(self, msg: MIMEMultipart):
        # Create SMTP session
        server = smtplib.SMTP(
            self.email_settings['smtp_server'], 
            self.email_settings['smtp_port']
        )
        
        # Enable security
        server.starttls()
        
        # Login
        server.login(
            self.email_settings['username'], 
            self.email_settings['password']
        )
        
        # Send email
        text = msg.as_string()
        recipients = [msg['To']]
        
        if msg['Cc']:
            recipients.extend(msg['Cc'].split(', '))
        
        server.sendmail(msg['From'], recipients, text)
        server.quit()
    
    def test_connection(self) -> bool:
        """Test email server connection"""
        try:
            server = smtplib.SMTP(
                self.email_settings['smtp_server'], 
                self.email_settings['smtp_port']
            )
            server.starttls()
            server.login(
                self.email_settings['username'], 
                self.email_settings['password']
            )
            server.quit()
            logger.info("Email connection test successful")
            return True
        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return False