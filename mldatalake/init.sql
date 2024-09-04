
-- mysql/init.sql
CREATE DATABASE IF NOT EXISTS mydatabase;
USE mydatabase;

CREATE TABLE IF NOT EXISTS symbol (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    market ENUM('crypto', 'stock', 'forex', 'futures') NOT NULL,
    active BOOLEAN NOT NULL
);