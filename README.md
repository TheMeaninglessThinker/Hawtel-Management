# Hawtel-Management
We manage hotels. 
CREATE DATABASE IF NOT EXISTS hotel_db;
USE hotel_db;

CREATE TABLE rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    status ENUM('available', 'occupied') DEFAULT 'available',
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE guests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(20),
    id_proof VARCHAR(50),
    preferences TEXT
);

CREATE TABLE reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    guest_id INT,
    room_id INT,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    status ENUM('booked', 'cancelled') DEFAULT 'booked',
    FOREIGN KEY (guest_id) REFERENCES guests(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

CREATE TABLE staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50),
    schedule TEXT
);

CREATE TABLE billings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reservation_id INT,
    amount DECIMAL(10, 2),
    status ENUM('pending', 'paid') DEFAULT 'pending',
    details TEXT,
    FOREIGN KEY (reservation_id) REFERENCES reservations(id)
);

-- Sample Data
INSERT INTO rooms (type, status, price) VALUES 
('Single', 'available', 100.00),
('Double', 'available', 150.00);

INSERT INTO guests (name, contact, id_proof, preferences) VALUES 
('John Doe', '1234567890', 'Aadhar123', 'Non-smoking');
