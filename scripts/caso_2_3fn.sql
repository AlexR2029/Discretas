DROP TABLE IF EXISTS caso_2_estudiantes;

CREATE TABLE caso_2_estudiantes (
    codigo_estudiante INT NOT NULL,
    programa VARCHAR(100) NOT NULL,
    valor_semestre DECIMAL(12,2) NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    PRIMARY KEY (codigo_estudiante)
);

INSERT INTO caso_2_estudiantes
    (codigo_estudiante, programa, valor_semestre, nombres)
VALUES
    (1, 'Sistemas', 3200000.00, 'Ana Perez'),
    (2, 'Sistemas', 3200000.00, 'Luis Ruiz'),
    (3, 'Industrial', 3000000.00, 'Marta Diaz');
