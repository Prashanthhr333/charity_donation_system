DROP DATABASE IF EXISTS charity_db;
CREATE DATABASE charity_db;
USE charity_db;

CREATE TABLE donors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE causes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    amount FLOAT NOT NULL,
    donor_id INT NOT NULL,
    cause_id INT NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    transaction_id VARCHAR(100) UNIQUE,
    status VARCHAR(20) DEFAULT 'completed',
    FOREIGN KEY (donor_id) REFERENCES donors(id),
    FOREIGN KEY (cause_id) REFERENCES causes(id)
);

INSERT INTO causes (name, description) VALUES
    ('Education', 'Support educational programs and scholarships'),
    ('Healthcare', 'Provide medical assistance and healthcare services'),
    ('Environment', 'Environmental conservation and sustainability initiatives'),
    ('Poverty Relief', 'Help families in need with basic necessities');
