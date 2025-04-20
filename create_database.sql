-- Create database
CREATE DATABASE IF NOT EXISTS kamal;

-- Use the database
USE kamal;

-- Create table prod_master
CREATE TABLE IF NOT EXISTS prod_master (
    prod_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    hsn_code VARCHAR(50),
    type VARCHAR(100)
); 