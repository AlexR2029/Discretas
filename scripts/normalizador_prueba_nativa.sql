-- Dataset autónomo para probar el análisis nativo del normalizador.
-- Cárgalo desde el selector, confirma normalizador_prueba_nativa y escribe
-- manualmente las DF que quieras comprobar en la pestaña DF.
-- Cada carga actualiza las mismas filas de prueba sin duplicarlas.

CREATE TABLE IF NOT EXISTS normalizador_prueba_nativa (
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    id_cliente INT NOT NULL,
    nombre_cliente VARCHAR(100) NOT NULL,
    nombre_producto VARCHAR(100) NOT NULL,
    precio DECIMAL(12,2) NOT NULL,
    cantidad INT NOT NULL,
    PRIMARY KEY (id_venta, id_producto)
);

INSERT INTO normalizador_prueba_nativa
    (id_venta, id_producto, id_cliente, nombre_cliente,
     nombre_producto, precio, cantidad)
SELECT
    7000 + FLOOR((numero - 1) / 4),
    500 + MOD(numero - 1, 4),
    300 + MOD(FLOOR((numero - 1) / 4), 4),
    ELT(
        1 + MOD(FLOOR((numero - 1) / 4), 4),
        'Ana Ruiz', 'Luis Perez', 'Marta Diaz', 'Juan Rojas'
    ),
    ELT(
        1 + MOD(numero - 1, 4),
        'Teclado', 'Mouse', 'Monitor', 'Webcam'
    ),
    CASE MOD(numero - 1, 4)
        WHEN 0 THEN 79900.00
        WHEN 1 THEN 45900.00
        WHEN 2 THEN 599900.00
        ELSE 129900.00
    END,
    1 + FLOOR(RAND() * 6)
FROM (
    SELECT 1 AS numero UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL
    SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL
    SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10 UNION ALL
    SELECT 11 UNION ALL SELECT 12 UNION ALL SELECT 13 UNION ALL SELECT 14 UNION ALL
    SELECT 15 UNION ALL SELECT 16 UNION ALL SELECT 17 UNION ALL SELECT 18 UNION ALL
    SELECT 19 UNION ALL SELECT 20 UNION ALL SELECT 21 UNION ALL SELECT 22 UNION ALL
    SELECT 23 UNION ALL SELECT 24
) AS numeros
ON DUPLICATE KEY UPDATE
    id_cliente = VALUES(id_cliente),
    nombre_cliente = VALUES(nombre_cliente),
    nombre_producto = VALUES(nombre_producto),
    precio = VALUES(precio),
    cantidad = VALUES(cantidad);
