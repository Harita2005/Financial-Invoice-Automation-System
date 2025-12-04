from typing import List, Dict, Any, Tuple
from datetime import datetime
from decimal import Decimal, InvalidOperation
import logging
from .models import Invoice, Customer, InvoiceItem

logger = logging.getLogger(__name__)

class DataValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_billing_records(self, records: List[Dict[str, Any]]) -> Tuple[List[Invoice], List[str]]:
        validated_invoices = []
        all_errors = []
        
        # Group records by billing record ID
        grouped_records = self._group_records(records)
        
        for record_id, record_data in grouped_records.items():
            try:
                invoice = self._validate_single_record(record_data)
                if invoice:
                    validated_invoices.append(invoice)
            except Exception as e:
                error_msg = f"Record {record_id}: {str(e)}"
                all_errors.append(error_msg)
                logger.error(error_msg)
        
        return validated_invoices, all_errors
    
    def _group_records(self, records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        grouped = {}
        for record in records:
            record_id = record.get('id') or record.get('_id')
            if record_id not in grouped:
                grouped[record_id] = []
            grouped[record_id].append(record)
        return grouped
    
    def _validate_single_record(self, record_data: List[Dict[str, Any]]) -> Invoice:
        if not record_data:
            raise ValueError("Empty record data")
        
        # Get the first record for main invoice data
        main_record = record_data[0]
        
        # Validate and create customer
        customer = self._validate_customer(main_record)
        
        # Validate and create items
        items = self._validate_items(record_data)
        
        # Validate dates
        issue_date, due_date = self._validate_dates(main_record)
        
        # Create invoice
        invoice_number = self._validate_invoice_number(main_record)
        
        # Get tax and discount rates
        tax_rate = self._validate_decimal(main_record.get('tax_rate', 0.08), 'tax_rate')
        discount_rate = self._validate_decimal(main_record.get('discount_rate', 0.00), 'discount_rate')
        
        invoice = Invoice(
            invoice_number=invoice_number,
            customer=customer,
            items=items,
            issue_date=issue_date,
            due_date=due_date,
            tax_rate=tax_rate,
            discount_rate=discount_rate,
            notes=main_record.get('notes')
        )
        
        return invoice
    
    def _validate_customer(self, record: Dict[str, Any]) -> Customer:
        required_fields = ['name', 'email', 'address']
        for field in required_fields:
            if not record.get(field):
                raise ValueError(f"Missing required customer field: {field}")
        
        # Clean and validate email
        email = record['email'].strip().lower()
        if '@' not in email or '.' not in email.split('@')[1]:
            raise ValueError(f"Invalid email format: {email}")
        
        return Customer(
            name=record['name'].strip(),
            email=email,
            address=record['address'].strip(),
            phone=record.get('phone', '').strip() or None
        )
    
    def _validate_items(self, record_data: List[Dict[str, Any]]) -> List[InvoiceItem]:
        items = []
        
        for record in record_data:
            description = record.get('description', '').strip()
            if not description:
                raise ValueError("Missing item description")
            
            try:
                quantity = int(record.get('quantity', 0))
                if quantity <= 0:
                    raise ValueError(f"Invalid quantity: {quantity}")
            except (ValueError, TypeError):
                raise ValueError(f"Invalid quantity format: {record.get('quantity')}")
            
            try:
                unit_price = Decimal(str(record.get('unit_price', 0)))
                if unit_price < 0:
                    raise ValueError(f"Negative unit price: {unit_price}")
            except (InvalidOperation, TypeError):
                raise ValueError(f"Invalid unit price format: {record.get('unit_price')}")
            
            items.append(InvoiceItem(
                description=description,
                quantity=quantity,
                unit_price=unit_price
            ))
        
        if not items:
            raise ValueError("No valid items found")
        
        return items
    
    def _validate_dates(self, record: Dict[str, Any]) -> Tuple[datetime, datetime]:
        issue_date = self._parse_date(record.get('issue_date') or record.get('billing_date'))
        due_date = self._parse_date(record.get('due_date'))
        
        if not issue_date:
            raise ValueError("Missing or invalid issue date")
        
        if not due_date:
            # Default to 30 days after issue date
            from datetime import timedelta
            due_date = issue_date + timedelta(days=30)
        
        if due_date < issue_date:
            raise ValueError("Due date cannot be before issue date")
        
        return issue_date, due_date
    
    def _parse_date(self, date_value) -> datetime:
        if isinstance(date_value, datetime):
            return date_value
        
        if isinstance(date_value, str):
            # Try common date formats
            formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y', '%d/%m/%Y']
            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt)
                except ValueError:
                    continue
        
        return None
    
    def _validate_invoice_number(self, record: Dict[str, Any]) -> str:
        invoice_number = record.get('invoice_number', '').strip()
        if not invoice_number:
            # Generate invoice number from record ID and timestamp
            record_id = record.get('id') or record.get('_id', 'UNK')
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            invoice_number = f"INV-{record_id}-{timestamp}"
        
        return invoice_number
    
    def _validate_decimal(self, value, field_name: str) -> Decimal:
        try:
            decimal_value = Decimal(str(value))
            if decimal_value < 0:
                raise ValueError(f"Negative value for {field_name}: {value}")
            return decimal_value
        except (InvalidOperation, TypeError):
            raise ValueError(f"Invalid decimal format for {field_name}: {value}")
    
    def get_validation_summary(self) -> Dict[str, Any]:
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }