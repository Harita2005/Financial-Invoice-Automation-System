import mysql.connector
import pymongo
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
import logging
from .models import Invoice, Customer, InvoiceItem
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.db_config = config_manager.get_database_config()
        self.db_type = self.db_config.get('type', 'mysql')
        self.connection = None
        
    def connect(self):
        if self.db_type == 'mysql':
            self._connect_mysql()
        elif self.db_type == 'mongodb':
            self._connect_mongodb()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def _connect_mysql(self):
        mysql_config = self.db_config['mysql']
        try:
            self.connection = mysql.connector.connect(
                host=mysql_config['host'],
                port=mysql_config['port'],
                database=mysql_config['database'],
                user=mysql_config['username'],
                password=mysql_config['password']
            )
            logger.info("Connected to MySQL database")
        except mysql.connector.Error as e:
            logger.error(f"MySQL connection error: {e}")
            raise
    
    def _connect_mongodb(self):
        mongo_config = self.db_config['mongodb']
        try:
            client = pymongo.MongoClient(
                host=mongo_config['host'],
                port=mongo_config['port']
            )
            self.connection = client[mongo_config['database']]
            logger.info("Connected to MongoDB database")
        except pymongo.errors.ConnectionFailure as e:
            logger.error(f"MongoDB connection error: {e}")
            raise
    
    def get_billing_records(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        if self.db_type == 'mysql':
            return self._get_mysql_records(start_date, end_date)
        else:
            return self._get_mongodb_records(start_date, end_date)
    
    def _get_mysql_records(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        cursor = self.connection.cursor(dictionary=True)
        query = """
        SELECT b.*, c.name, c.email, c.address, c.phone,
               bi.description, bi.quantity, bi.unit_price
        FROM billing_records b
        JOIN customers c ON b.customer_id = c.id
        JOIN billing_items bi ON b.id = bi.billing_record_id
        WHERE b.billing_date BETWEEN %s AND %s
        ORDER BY b.id, bi.id
        """
        cursor.execute(query, (start_date, end_date))
        return cursor.fetchall()
    
    def _get_mongodb_records(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        collection = self.connection['billing_records']
        pipeline = [
            {
                "$match": {
                    "billing_date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$lookup": {
                    "from": "customers",
                    "localField": "customer_id",
                    "foreignField": "_id",
                    "as": "customer"
                }
            },
            {"$unwind": "$customer"},
            {
                "$lookup": {
                    "from": "billing_items",
                    "localField": "_id",
                    "foreignField": "billing_record_id",
                    "as": "items"
                }
            }
        ]
        return list(collection.aggregate(pipeline))
    
    def save_invoice_metadata(self, invoice: Invoice, pdf_path: str):
        metadata = {
            'invoice_number': invoice.invoice_number,
            'customer_name': invoice.customer.name,
            'customer_email': invoice.customer.email,
            'issue_date': invoice.issue_date,
            'due_date': invoice.due_date,
            'total_amount': float(invoice.total_amount),
            'pdf_path': pdf_path,
            'created_at': datetime.now()
        }
        
        if self.db_type == 'mysql':
            self._save_mysql_metadata(metadata)
        else:
            self._save_mongodb_metadata(metadata)
    
    def _save_mysql_metadata(self, metadata: Dict[str, Any]):
        cursor = self.connection.cursor()
        query = """
        INSERT INTO invoice_metadata 
        (invoice_number, customer_name, customer_email, issue_date, due_date, 
         total_amount, pdf_path, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, tuple(metadata.values()))
        self.connection.commit()
    
    def _save_mongodb_metadata(self, metadata: Dict[str, Any]):
        collection = self.connection['invoice_metadata']
        collection.insert_one(metadata)
    
    def close(self):
        if self.connection:
            if self.db_type == 'mysql':
                self.connection.close()
            logger.info("Database connection closed")