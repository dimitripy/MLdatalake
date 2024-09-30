-- mysql/init.sql
CREATE DATABASE IF NOT EXISTS mldatalake;
USE mldatalake;

CREATE TABLE IF NOT EXISTS symbol (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    market ENUM('crypto', 'stock', 'forex', 'futures') NOT NULL,
    active BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS minute_bar (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME NOT NULL,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT,
    symbol_id INT NOT NULL,
    FOREIGN KEY (symbol_id) REFERENCES symbol(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    UNIQUE (symbol_id, date)
);

CREATE TABLE IF NOT EXISTS five_minute_bar (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME NOT NULL,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT,
    symbol_id INT NOT NULL,
    FOREIGN KEY (symbol_id) REFERENCES symbol(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    UNIQUE (symbol_id, date)
);

CREATE TABLE IF NOT EXISTS thirty_minute_bar (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME NOT NULL,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT,
    symbol_id INT NOT NULL,
    FOREIGN KEY (symbol_id) REFERENCES symbol(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    UNIQUE (symbol_id, date)
);