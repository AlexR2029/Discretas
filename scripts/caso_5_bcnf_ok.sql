DROP TABLE IF EXISTS caso_5_empleados;

CREATE TABLE caso_5_empleados (
    id_empleado INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    PRIMARY KEY (id_empleado)
);

INSERT INTO caso_5_empleados
    (id_empleado, nombre, ciudad)
VALUES
    (1, 'Ana', 'Cali'),
    (2, 'Luis', 'Bogota'),
    (3, 'Marta', 'Medellin');
