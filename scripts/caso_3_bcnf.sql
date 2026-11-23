DROP TABLE IF EXISTS caso_3_asignaciones;

CREATE TABLE caso_3_asignaciones (
    alumno VARCHAR(50) NOT NULL,
    curso VARCHAR(50) NOT NULL,
    profesor VARCHAR(100) NOT NULL,
    PRIMARY KEY (alumno, curso)
);

INSERT INTO caso_3_asignaciones
    (alumno, curso, profesor)
VALUES
    ('Ana', 'Matematicas', 'Gomez'),
    ('Luis', 'Matematicas', 'Gomez'),
    ('Marta', 'Fisica', 'Lopez');
