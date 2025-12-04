-- Sample data for MySQL database

-- Insert sample customers
INSERT INTO customers (name, email, address, phone) VALUES
('Acme Corporation', 'billing@acme.com', '123 Business Ave\nNew York, NY 10001', '+1 (555) 123-4567'),
('Tech Solutions Inc', 'accounts@techsolutions.com', '456 Innovation Drive\nSan Francisco, CA 94105', '+1 (555) 987-6543'),
('Global Services LLC', 'finance@globalservices.com', '789 Commerce Street\nChicago, IL 60601', '+1 (555) 456-7890');

-- Insert sample billing records
INSERT INTO billing_records (customer_id, invoice_number, billing_date, issue_date, due_date, tax_rate, discount_rate, notes) VALUES
(1, 'INV-2024-001', '2024-01-15', '2024-01-15', '2024-02-14', 0.08, 0.00, 'Monthly service fee'),
(2, 'INV-2024-002', '2024-01-20', '2024-01-20', '2024-02-19', 0.08, 0.05, 'Bulk discount applied'),
(3, 'INV-2024-003', '2024-01-25', '2024-01-25', '2024-02-24', 0.08, 0.00, 'Consulting services');

-- Insert sample billing items
INSERT INTO billing_items (billing_record_id, description, quantity, unit_price) VALUES
-- Items for invoice 1
(1, 'Web Development Services', 40, 125.00),
(1, 'Domain Registration', 1, 15.99),
(1, 'SSL Certificate', 1, 89.99),

-- Items for invoice 2
(2, 'Software License (Annual)', 5, 299.99),
(2, 'Technical Support', 12, 75.00),
(2, 'Training Sessions', 3, 450.00),

-- Items for invoice 3
(3, 'Business Consultation', 8, 200.00),
(3, 'Market Analysis Report', 1, 1500.00),
(3, 'Strategy Planning', 4, 350.00);