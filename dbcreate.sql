-- Create the database
CREATE DATABASE IF NOT EXISTS kamal;
USE kamal;

-- Create product master table
CREATE TABLE IF NOT EXISTS prod_master (
    prod_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    hsn_code VARCHAR(20),
    type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create party master table
CREATE TABLE IF NOT EXISTS party_master (
    p_id INT AUTO_INCREMENT PRIMARY KEY,
    party VARCHAR(100) NOT NULL,
    gstin VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create accounts table
CREATE TABLE IF NOT EXISTS accounts (
    a_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create incoming bills table
CREATE TABLE IF NOT EXISTS incoming_bills (
    s_no INT AUTO_INCREMENT PRIMARY KEY,
    inv_id VARCHAR(50) NOT NULL,
    party_id INT NOT NULL,
    bill_date DATE NOT NULL,
    account_id INT,
    tds_percent DECIMAL(5,2),
    tds_amount DECIMAL(10,2),
    final_amount DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (party_id) REFERENCES party_master(p_id),
    FOREIGN KEY (account_id) REFERENCES accounts(a_id)
);

-- Create bill items table (for incoming bills)
CREATE TABLE IF NOT EXISTS bill_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_s_no INT NOT NULL,
    product_id INT NOT NULL,
    qty DECIMAL(10,2) NOT NULL,
    rate DECIMAL(10,2) NOT NULL,
    sub_total DECIMAL(10,2) NOT NULL,
    gst_percent DECIMAL(5,2) NOT NULL,
    sgst_amount DECIMAL(10,2) NOT NULL,
    cgst_amount DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_s_no) REFERENCES incoming_bills(s_no) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES prod_master(prod_id)
);

-- Create outgoing bills table
CREATE TABLE IF NOT EXISTS outgoing_bills (
    s_no INT AUTO_INCREMENT PRIMARY KEY,
    bill_no VARCHAR(50) NOT NULL,
    party_id INT NOT NULL,
    bill_date DATE NOT NULL,
    account_id INT,
    tds_percent DECIMAL(5,2),
    tds_amount DECIMAL(10,2),
    final_amount DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (party_id) REFERENCES party_master(p_id),
    FOREIGN KEY (account_id) REFERENCES accounts(a_id)
);

-- Create outgoing bill items table
CREATE TABLE IF NOT EXISTS outgoing_bill_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_s_no INT NOT NULL,
    product_id INT NOT NULL,
    qty DECIMAL(10,2) NOT NULL,
    rate DECIMAL(10,2) NOT NULL,
    sub_total DECIMAL(10,2) NOT NULL,
    gst_percent DECIMAL(5,2) NOT NULL,
    sgst_amount DECIMAL(10,2) NOT NULL,
    cgst_amount DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_s_no) REFERENCES outgoing_bills(s_no) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES prod_master(prod_id)
);

-- Create indexes for better performance
CREATE INDEX idx_incoming_bills_party ON incoming_bills(party_id);
CREATE INDEX idx_incoming_bills_date ON incoming_bills(bill_date);
CREATE INDEX idx_outgoing_bills_party ON outgoing_bills(party_id);
CREATE INDEX idx_outgoing_bills_date ON outgoing_bills(bill_date);
CREATE INDEX idx_bill_items_bill ON bill_items(bill_s_no);
CREATE INDEX idx_outgoing_bill_items_bill ON outgoing_bill_items(bill_s_no);

-- Add unique constraints
ALTER TABLE incoming_bills ADD UNIQUE INDEX idx_inv_id (inv_id);
ALTER TABLE outgoing_bills ADD UNIQUE INDEX idx_bill_no (bill_no);
ALTER TABLE prod_master ADD UNIQUE INDEX idx_product_name (name);
ALTER TABLE party_master ADD UNIQUE INDEX idx_party_name (party);
ALTER TABLE accounts ADD UNIQUE INDEX idx_account_name (name); 