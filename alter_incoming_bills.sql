USE kamal;

-- Add account_id to incoming_bills table
ALTER TABLE incoming_bills
ADD COLUMN account_id INT NULL AFTER party_id;

-- Add foreign key constraint for account_id
ALTER TABLE incoming_bills
ADD CONSTRAINT fk_incoming_bills_account
FOREIGN KEY (account_id) REFERENCES accounts(a_id);

-- Add tds_percentage column to incoming_bills table
ALTER TABLE incoming_bills
ADD COLUMN tds_percentage DECIMAL(5,2) DEFAULT NULL AFTER account_id; 