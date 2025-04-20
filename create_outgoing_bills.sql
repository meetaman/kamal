USE kamal;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS outgoing_bill_items;
DROP TABLE IF EXISTS outgoing_bills;

-- Create outgoing bills table
CREATE TABLE IF NOT EXISTS outgoing_bills (
    s_no INT AUTO_INCREMENT PRIMARY KEY,
    bill_no VARCHAR(50) NOT NULL,
    party_id INT NOT NULL,
    bill_date DATE NOT NULL,
    account_id INT NULL,
    tds_percent DECIMAL(5,2) DEFAULT NULL,
    tds_amount DECIMAL(10,2) DEFAULT NULL,
    final_amount DECIMAL(10,2) NOT NULL,
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
    FOREIGN KEY (bill_s_no) REFERENCES outgoing_bills(s_no) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES prod_master(prod_id)
); 