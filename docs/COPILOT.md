# Contexto del proyecto
Aplicación en Python 3.11+ con Tkinter y MySQL 8 en localhost que normaliza
esquemas relacionales con dependencias funcionales (proyecto de Matemática Discreta).
La especificación completa está en docs/. Léela antes de escribir código.

# Reglas obligatorias
- Núcleo (nucleo/) en Python puro con frozenset. Sin MySQL ni Tkinter dentro.
- Prohibido usar librerías que resuelvan cierre, claves, formas normales,
  cobertura mínima, descomposición, tableau o join. Todo es código propio.
- Prohibido Java o dependencias que lo requieran.
- Dependencias permitidas: mysql-connector-python, pyinstaller (y matplotlib/networkx solo para dibujar).
- Cada función del núcleo lleva docstring con la definición formal que implementa
  y su complejidad.
- Pruebas con unittest en tests/.
- Credenciales por archivo `.env` con HOST, DB_PORT, USER, PASSWORD y DATABASE,
  nunca en el código.
- Código y comentarios en español, nombres de módulos según el README.

# Forma de trabajar
- Trabaja solo la fase que se te pida. Al terminar, detente,
  resume qué hiciste y cómo verificarlo.
- No modifiques archivos de docs/ sin avisar.

# Fuentes (docs/)

- Matemática Discreta: Conjuntos, Relaciones, Funciones, Bases de datos relacionales.
- Bases de datos: BD1_MER_Normalización.
- Usa la notación y las definiciones de estos PDFs como referencia principal.
- Cuando un docstring o un texto cite un concepto, indica el PDF y la página
  (por ejemplo: "Relaciones.pdf, pág. 12").
- No inventes definiciones: si un concepto no está en las fuentes, dilo
  y márcalo como "requiere fuente externa".
- No copies texto largo de los PDFs; parafrasea y cita.