CREATE DATABASE IF NOT EXISTS wallstreet_db;
USE wallstreet_db;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    telefono VARCHAR(20) NOT NULL,
    fecha_nac DATE NOT NULL,
    rol VARCHAR(20) DEFAULT 'usuario' CHECK (rol IN ('usuario', 'admin')),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);