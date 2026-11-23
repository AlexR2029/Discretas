DROP TABLE IF EXISTS caso_1_pedidos;

CREATE TABLE caso_1_pedidos (
    id_pedido INT NOT NULL,
    id_producto INT NOT NULL,
    nombre_producto VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    cantidad INT NOT NULL,
    PRIMARY KEY (id_pedido, id_producto)
);

INSERT INTO caso_1_pedidos
    (id_pedido, id_producto, nombre_producto, precio, cantidad)
VALUES
    (1, 10, 'Lapiz', 1500.00, 2),
    (1, 11, 'Cuaderno', 5000.00, 1),
    (2, 10, 'Lapiz', 1500.00, 3);
