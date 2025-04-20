USE kamal;

-- First, remove the account_id column from bill_items
ALTER TABLE bill_items
DROP COLUMN account_id;

-- Add account_id to incoming_bills table as nullable first
ALTER TABLE incoming_bills
ADD COLUMN account_id INT NULL AFTER party_id;

-- Set a default value for existing rows (you'll need to update this with a valid account_id)
UPDATE incoming_bills
SET account_id = (SELECT MIN(a_id) FROM accounts)
WHERE account_id IS NULL;

-- Now make it NOT NULL and add the foreign key constraint
ALTER TABLE incoming_bills
MODIFY COLUMN account_id INT NOT NULL,
ADD CONSTRAINT fk_incoming_bills_account
FOREIGN KEY (account_id) REFERENCES accounts(a_id); 