-- Tabla original que INCUMPLE BCNF
CREATE TABLE IF NOT EXISTS caso_6_consultas (
    paciente_id INT NOT NULL,
    especialidad VARCHAR(50) NOT NULL,
    medico VARCHAR(100) NOT NULL,

    PRIMARY KEY (paciente_id, especialidad)
);

-- Inserción de datos demostrativos (se evidencia la redundancia)
INSERT INTO caso_6_consultas (
    paciente_id,
    especialidad,
    medico
)
VALUES
    (101, 'Cardiología', 'Dr. Carlos Mendoza'),
    (102, 'Cardiología', 'Dr. Carlos Mendoza'),
    (103, 'Neurología', 'Dra. Elena Rostova'),
    (104, 'Cardiología', 'Dr. Carlos Mendoza'),
    (105, 'Neurología', 'Dra. Elena Rostova')
ON DUPLICATE KEY UPDATE
    medico = VALUES(medico);
