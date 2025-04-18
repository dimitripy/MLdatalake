-- mysql/init.sql
CREATE DATABASE IF NOT EXISTS mldatalake;
USE mldatalake;


CREATE TABLE IF NOT EXISTS security (
    sec_id INT AUTO_INCREMENT PRIMARY KEY,
    exchange VARCHAR(100) NOT NULL,
    category VARCHAR(200) NOT NULL,
    sector VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS symbol (
    sy_id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    market ENUM('crypto', 'stock', 'forex', 'futures') NOT NULL,
    active BOOLEAN NOT NULL,
    sec_id INT NOT NULL,
    FOREIGN KEY (sec_id) REFERENCES security(sec_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    UNIQUE (ticker, sec_id)
);

CREATE TABLE IF NOT EXISTS minute_bar (
    b_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME NOT NULL,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT,
    sy_id INT NOT NULL,
    FOREIGN KEY (sy_id) REFERENCES symbol(sy_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    UNIQUE (sy_id, date)
);


