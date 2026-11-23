# Extracto: BD1 MER Normalización

Fuente: `BD1_MER_Normalizacion_Vr20250311.pdf`; páginas del PDF.

## Definiciones y criterios

- **Normalización (p. 3):** proceso de depurar y afinar un modelo entidad-
  relación mediante formas normales para reducir redundancia y anomalías de
  inserción, actualización y borrado.
- **1FN (p. 8):** una entidad no tiene grupos repetitivos ni atributos
  multivaluados o compuestos; cada atributo contiene un valor atómico o
  indivisible. Es obligatoria para el modelo según la fuente.
- **2FN (p. 16):** la entidad está en 1FN y cada atributo no clave depende
  funcionalmente de toda la clave principal. Una clave principal de un solo
  atributo satisface automáticamente la condición de dependencia parcial.
- **3FN (p. 23):** la entidad está en 2FN y no contiene dependencias
  transitivas entre atributos no clave; la fuente ilustra `A→B`, `B→C`, por lo
  que `A→C` indirectamente.
- **Clave principal y claves candidatas (pp. 16, 23):** se usan como
  identificadores del modelo y como referencia para evaluar dependencias, pero
  el PDF no ofrece una definición formal independiente de clave candidata.

## Ejemplos y análisis resueltos

- **Anomalías en EMPLEADO (p. 6):** datos repetidos producen anomalía de
  actualización (cambia un oficio), de borrado (se pierde información del
  empleado al quitar edificios) y de inserción (no se puede registrar un
  empleado sin edificio).
- **1FN y USUARIO (pp. 8--11):** se identifica un atributo multivaluado
  `perfil`; la solución consiste en separarlo para dejar valores atómicos.
- **2FN en una venta (pp. 17--20):** `venta_no,cod_prod→cantidad` y
  `venta_no,cod_prod→precio_prod`, mientras `cod_prod→nombre_prod`; como el
  nombre depende de una parte de la clave compuesta, la entidad no está en 2FN.
  La solución es llevar esos atributos a una entidad cuya clave los determine
  completamente.
- **3FN en ESTUDIANTE (pp. 24--26):** `código→programa` y
  `programa→valor_semestre`, luego `código→valor_semestre` de forma transitiva.
  Se separa `valor_semestre` en una entidad asociada al programa.
- **3FN y cargo/salario (pp. 27--28):** si cada cargo tiene un único salario,
  `código→cargo`, `cargo→salario` y `código→salario` exhiben una transitividad;
  si no existe esa dependencia, no hay esa redundancia transitiva.

## Ausencias importantes

El PDF no contiene una definición ni un procedimiento de **BCNF**, ni desarrolla
algoritmos formales de **cierre de atributos**, **cobertura mínima**,
**descomposición**, **preservación de dependencias**, **join sin pérdida** o
**tableau/chase**. Esos temas requieren fuente externa.
