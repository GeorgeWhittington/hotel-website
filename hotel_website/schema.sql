-- Make id random, consecutive = security flaw
CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(20) UNIQUE NOT NULL,
  password CHAR(102) NOT NULL,
  admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS locations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    location_name VARCHAR(100) UNIQUE NOT NULL
);

-- conversion rate is (GBP * conversion_rate) = amt in other currency
-- so GBP's conversion_rate *must* be 1.0
-- Acronym's are in ISO 4217 format
CREATE TABLE IF NOT EXISTS currencies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(50) UNIQUE NOT NULL,
    acronym CHAR(3) UNIQUE NOT NULL,
    conversion_rate DECIMAL(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS hotels (
    id INT PRIMARY KEY AUTO_INCREMENT,
    location_id INT NOT NULL,
    base_currency_id INT NOT NULL,
    peak_price DECIMAL(10, 2) NOT NULL,
    off_peak_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (location_id) REFERENCES locations(id),
    FOREIGN KEY (base_currency_id) REFERENCES currencies(id)
);

CREATE TABLE IF NOT EXISTS room_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type CHAR(1) UNIQUE NOT NULL,
    max_occupants INT NOT NULL
);

CREATE TABLE IF NOT EXISTS rooms (
    id INT PRIMARY KEY AUTO_INCREMENT,
    hotel_id INT NOT NULL,
    type_id INT NOT NULL,
    FOREIGN KEY (hotel_id) REFERENCES hotels(id),
    FOREIGN KEY (type_id) REFERENCES room_types(id)
);

-- Make id random, consecutive = security flaw
-- Ensure time_zone sys variable is set to UTC for TIMESTAMP
-- Maybe make date_booked a DATE, and add created+updated fields (those should be TIMESTAMPS tho)
CREATE TABLE IF NOT EXISTS bookings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    room_id INT NOT NULL,
    user_id INT NOT NULL,
    occupants INT NOT NULL,
    date_booked TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);