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