USE kamal;

CREATE TABLE IF NOT EXISTS party_master (
    p_id INT AUTO_INCREMENT PRIMARY KEY,
    party VARCHAR(255) NOT NULL,
    gstin VARCHAR(15),
    address TEXT
); 