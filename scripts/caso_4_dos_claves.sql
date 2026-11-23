DROP TABLE IF EXISTS caso_4_personas;

CREATE TABLE caso_4_personas (
    dni VARCHAR(20) NOT NULL,
    email VARCHAR(120) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    PRIMARY KEY (dni),
    UNIQUE KEY uk_persona_email (email)
);

INSERT INTO caso_4_personas
    (dni, email, nombre, ciudad)
VALUES
    ('1001', 'ana@ejemplo.com', 'Ana', 'Cali'),
    ('1002', 'luis@ejemplo.com', 'Luis', 'Bogota'),
    ('1003', 'marta@ejemplo.com', 'Marta', 'Medellin');
