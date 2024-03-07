CREATE DATABASE BOLO_DE_POTE;

CREATE TABLE produtos (
    codigo INT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    preco DECIMAL(10, 2) NOT NULL
);

CREATE TABLE pedidos (
    numero INT PRIMARY KEY,
    cliente VARCHAR(255) NOT NULL
);

CREATE TABLE produtos_em_pedidos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    numero_pedido INT,
    codigo_produto INT,
    quantidade INT NOT NULL,
    FOREIGN KEY (numero_pedido) REFERENCES pedidos(numero) ON DELETE CASCADE,
    FOREIGN KEY (codigo_produto) REFERENCES produtos(codigo) ON DELETE CASCADE
);

ALTER TABLE produtos_em_pedidos MODIFY COLUMN numero_pedido INT NULL;
