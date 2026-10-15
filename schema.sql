CREATE DATABASE my_crud_demo_db;
USE my_crud_demo_db;
CREATE TABLE equipment_service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_type VARCHAR(100) NOT NULL,
    brand VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100) UNIQUE,
    issue_reported TEXT,
    service_date DATE,
    technician VARCHAR(100),
    status ENUM('Pending','In Progress','Completed') DEFAULT 'Pending'
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    user_name VARCHAR(50) NOT NULL UNIQUE, 
    email VARCHAR(50) NOT NULL UNIQUE, 
    password_hash VARCHAR(50) NOT NULL
);
