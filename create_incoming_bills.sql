USE kamal;

-- Drop existing table if it exists
DROP TABLE IF EXISTS bill_items;
DROP TABLE IF EXISTS incoming_bills;

-- Create incoming bills table
CREATE TABLE IF NOT EXISTS incoming_bills (
    s_no INT AUTO_INCREMENT PRIMARY KEY,
    inv_id VARCHAR(50) NOT NULL,
    party_id INT NOT NULL,
    bill_date DATE NOT NULL,
    final_amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (party_id) REFERENCES party_master(p_id)
);

-- Create bill items table
CREATE TABLE IF NOT EXISTS bill_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_s_no INT NOT NULL,
    product_id INT NOT NULL,
    account_id INT NOT NULL,
    qty DECIMAL(10,2) NOT NULL,
    rate DECIMAL(10,2) NOT NULL,
    sub_total DECIMAL(10,2) NOT NULL,
    gst_percent DECIMAL(5,2) NOT NULL,
    sgst_amount DECIMAL(10,2) NOT NULL,
    cgst_amount DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (bill_s_no) REFERENCES incoming_bills(s_no) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES prod_master(prod_id),
    FOREIGN KEY (account_id) REFERENCES accounts(a_id)
); 