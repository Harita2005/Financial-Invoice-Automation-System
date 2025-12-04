import os
from datetime import datetime
from decimal import Decimal
from typing import Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import logging
from .models import Invoice
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)

class PDFGenerator:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.company_info = config_manager.get_company_info()
        self.invoice_settings = config_manager.get_invoice_settings()
        self.output_settings = config_manager.get_output_settings()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.darkred,
            alignment=TA_RIGHT,
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=6
        ))
    
    def generate_invoice(self, invoice: Invoice, output_path: Optional[str] = None) -> str:
        if not output_path:
            filename = self.output_settings['filename_format'].format(
                invoice_number=invoice.invoice_number,
                date=invoice.issue_date.strftime('%Y%m%d')
            )
            output_path = os.path.join(self.output_settings['folder'], filename)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=0.5*inch)
        story = []
        
        # Company header
        story.extend(self._create_header())
        story.append(Spacer(1, 0.3*inch))
        
        # Invoice title and number
        story.extend(self._create_invoice_title(invoice))
        story.append(Spacer(1, 0.2*inch))
        
        # Customer and invoice info
        story.extend(self._create_info_section(invoice))
        story.append(Spacer(1, 0.3*inch))
        
        # Items table
        story.extend(self._create_items_table(invoice))
        story.append(Spacer(1, 0.2*inch))
        
        # Totals section
        story.extend(self._create_totals_section(invoice))
        
        # Notes
        if invoice.notes:
            story.append(Spacer(1, 0.2*inch))
            story.extend(self._create_notes_section(invoice.notes))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        story.extend(self._create_footer())
        
        doc.build(story)
        logger.info(f"Invoice PDF generated: {output_path}")
        return output_path
    
    def _create_header(self):
        elements = []
        
        # Company logo (if exists)
        logo_path = self.company_info.get('logo_path')
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=2*inch, height=1*inch)
                elements.append(logo)
            except Exception as e:
                logger.warning(f"Could not load logo: {e}")
        
        # Company name
        company_name = Paragraph(self.company_info['name'], self.styles['CompanyName'])
        elements.append(company_name)
        
        # Company info
        company_details = f"""
        {self.company_info['address']}<br/>
        Phone: {self.company_info['phone']}<br/>
        Email: {self.company_info['email']}<br/>
        Website: {self.company_info['website']}
        """
        company_info = Paragraph(company_details, self.styles['CompanyInfo'])
        elements.append(company_info)
        
        return elements
    
    def _create_invoice_title(self, invoice: Invoice):
        elements = []
        title = Paragraph(f"INVOICE #{invoice.invoice_number}", self.styles['InvoiceTitle'])
        elements.append(title)
        return elements
    
    def _create_info_section(self, invoice: Invoice):
        elements = []
        
        # Create two-column layout for customer and invoice info
        data = [
            ['Bill To:', 'Invoice Details:'],
            [
                f"{invoice.customer.name}<br/>{invoice.customer.address}<br/>Email: {invoice.customer.email}" + 
                (f"<br/>Phone: {invoice.customer.phone}" if invoice.customer.phone else ""),
                f"Issue Date: {invoice.issue_date.strftime(self.invoice_settings['date_format'])}<br/>" +
                f"Due Date: {invoice.due_date.strftime(self.invoice_settings['date_format'])}"
            ]
        ]
        
        table = Table(data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        elements.append(table)
        return elements
    
    def _create_items_table(self, invoice: Invoice):
        elements = []
        
        # Table headers
        data = [['Description', 'Qty', 'Unit Price', 'Total']]
        
        # Add items
        currency_symbol = self.invoice_settings['currency_symbol']
        for item in invoice.items:
            data.append([
                item.description,
                str(item.quantity),
                f"{currency_symbol}{item.unit_price:.2f}",
                f"{currency_symbol}{item.total:.2f}"
            ])
        
        table = Table(data, colWidths=[3.5*inch, 0.8*inch, 1.2*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        return elements
    
    def _create_totals_section(self, invoice: Invoice):
        elements = []
        currency_symbol = self.invoice_settings['currency_symbol']
        
        totals_data = [
            ['Subtotal:', f"{currency_symbol}{invoice.subtotal:.2f}"]
        ]
        
        if invoice.discount_rate > 0:
            totals_data.append([
                f'Discount ({invoice.discount_rate*100:.1f}%):',
                f"-{currency_symbol}{invoice.discount_amount:.2f}"
            ])
        
        if invoice.tax_rate > 0:
            totals_data.append([
                f'GST ({invoice.tax_rate*100:.1f}%):',
                f"{currency_symbol}{invoice.tax_amount:.2f}"
            ])
        
        totals_data.append([
            'Total Amount:',
            f"{currency_symbol}{invoice.total_amount:.2f}"
        ])
        
        totals_table = Table(totals_data, colWidths=[4.5*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.darkred),
            ('LINEBELOW', (0, -2), (-1, -2), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(totals_table)
        return elements
    
    def _create_notes_section(self, notes: str):
        elements = []
        notes_title = Paragraph("<b>Notes:</b>", self.styles['Normal'])
        notes_content = Paragraph(notes, self.styles['Normal'])
        elements.extend([notes_title, notes_content])
        return elements
    
    def _create_footer(self):
        elements = []
        footer_text = "Thank you for your business!"
        footer = Paragraph(footer_text, self.styles['CompanyInfo'])
        elements.append(footer)
        return elements