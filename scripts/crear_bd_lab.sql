CREATE TABLE IF NOT EXISTS pedidos_planos (
    id_pedido INT NOT NULL,
    id_cliente INT NOT NULL,
    nombre_cliente VARCHAR(100) NOT NULL,
    ciudad_cliente VARCHAR(100) NOT NULL,
    id_producto INT NOT NULL,
    nombre_producto VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    cantidad INT NOT NULL,
    PRIMARY KEY (id_pedido, id_producto)
);

DELETE FROM pedidos_planos;

INSERT INTO pedidos_planos
    (id_pedido, id_cliente, nombre_cliente, ciudad_cliente,
     id_producto, nombre_producto, precio, cantidad)
VALUES
    (1, 10, 'Ana', 'Cali', 100, 'Lapiz', 1500.00, 2),
    (1, 10, 'Ana', 'Cali', 101, 'Cuaderno', 5000.00, 1),
    (2, 20, 'Luis', 'Bogota', 100, 'Lapiz', 1500.00, 3);