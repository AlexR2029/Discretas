## Caso 1
===================================================================
1. DEPENDENCIAS FUNCIONALES (DFs) VERDADERAS
===================================================================

DF1: {id_pedido, id_producto} -> cantidad
(La cantidad comprada depende estrictamente de la combinación de ese pedido específico con ese producto específico)

DF2: id_producto -> nombre_producto, precio
(El nombre del artículo y su precio de catálogo dependen únicamente del código del producto, no del pedido)

===================================================================
2. ANÁLISIS FORMAL (CIERRE DE ATRIBUTOS Y CLAVES CANDIDATAS)
===================================================================

Esquema original: R(id_pedido, id_producto, nombre_producto, precio, cantidad)
Clave Primaria Declarada: {id_pedido, id_producto}

Cierre de atributos:
- {id_pedido, id_producto}+ = {id_pedido, id_producto, cantidad, nombre_producto, precio} = R
  --> Superclave y Clave Candidata Única (K1)

Atributos Primos (pertenecen a al menos una clave candidata):
- id_pedido, id_producto

Atributos No Primos:
- nombre_producto, precio, cantidad

===================================================================
3. EVALUACIÓN DE FORMAS NORMALES (2FN, 3FN Y BCNF)
===================================================================

- 1FN: CUMPLE (todos los atributos almacenan valores atómicos).

- 2FN: NO CUMPLE
  * Existe una dependencia parcial (DF2: id_producto -> nombre_producto, precio).
  * Los atributos no primos 'nombre_producto' y 'precio' dependen únicamente de 'id_producto', el cual es solo un subconjunto (una parte) de la clave primaria compuesta {id_pedido, id_producto}.

- 3FN: NO CUMPLE
  * Al no cumplir con la 2FN debido a la presencia de dependencias parciales, la tabla automáticamente tampoco alcanza la 3FN.

- BCNF: NO CUMPLE
  * La regla estricta de BCNF exige que en toda DF no trivial X -> Y, el determinante X sea superclave.
  * En DF2 (id_producto -> nombre_producto, precio), el determinante 'id_producto' NO es Superclave de R.

===================================================================
4. ENTIDADES NORMALIZADAS EN 3FN + BCNF (NOTACIÓN RELACIONAL)
===================================================================

-------------------------------------------------------------------
ENTIDAD 1: PRODUCTO (Catálogo / Entidad Maestra)
-------------------------------------------------------------------
- Llave Primaria (PK) : id_producto
- Atributos No Clave  : nombre_producto, precio

Notación de Esquema:
PRODUCTO ( id_producto [PK], nombre_producto, precio )

Dependencia Funcional:
id_producto -> nombre_producto, precio
(Cumple 3FN y BCNF porque 'id_producto' es la Superclave completa)


-------------------------------------------------------------------
ENTIDAD 2: DETALLE_PEDIDO (Entidad Transaccional / Asociativa)
-------------------------------------------------------------------
- Llave Primaria (PK) : id_pedido, id_producto
- Llave Foránea 1(FK) : id_pedido    --->  Referencia a PEDIDO(id_pedido)
- Llave Foránea 2(FK) : id_producto  --->  Referencia a PRODUCTO(id_producto)
- Atributos No Clave  : cantidad

Notación de Esquema:
DETALLE_PEDIDO ( id_pedido [PK, FK], id_producto [PK, FK], cantidad )

Dependencia Funcional:
{id_pedido, id_producto} -> cantidad
(Cumple 3FN y BCNF porque la PK compuesta es la Superclave completa)

## Caso 2
===================================================================
1. DEPENDENCIAS FUNCIONALES (DFs) VERDADERAS
===================================================================

DF1: codigo_estudiante -> nombres, programa
DF2: programa -> valor_semestre
===================================================================
2. ANÁLISIS FORMAL (3FN Y BCNF)
===================================================================


Esquema original: R(codigo_estudiante, nombres, programa, valor_semestre)
Clave Primaria (PK): {codigo_estudiante}

- 1FN: CUMPLE (valores atómicos).
- 2FN: CUMPLE (clave primaria simple, no existen dependencias parciales).
- 3FN: NO CUMPLE (violado por DF2: programa -> valor_semestre; 'programa' no es superclave ni 'valor_semestre' es atributo primo).
- BCNF: NO CUMPLE (el determinante 'programa' de DF2 no es superclave).

===================================================================
3. ENTIDADES NORMALIZADAS EN 3FN + BCNF (NOTACIÓN RELACIONAL)
===================================================================

-------------------------------------------------------------------
ENTIDAD 1: PROGRAMA (Tabla Maestra / Catálogo)
-------------------------------------------------------------------
- Llave Primaria (PK) : programa
- Atributos No Clave  : valor_semestre

Notación de Esquema:
PROGRAMA ( programa [PK], valor_semestre )

Dependencia Funcional:
programa -> valor_semestre
(Cumple 3FN y BCNF porque 'programa' es Superclave)


-------------------------------------------------------------------
ENTIDAD 2: ESTUDIANTE (Entidad de Negocio)
-------------------------------------------------------------------
- Llave Primaria (PK) : codigo_estudiante
- Llave Foránea (FK)  : programa  --->  Referencia a PROGRAMA(programa)
- Atributos No Clave  : nombres

Notación de Esquema:
ESTUDIANTE ( codigo_estudiante [PK], nombres, programa [FK] )

Dependencia Funcional:
codigo_estudiante -> nombres, programa
(Cumple 3FN y BCNF porque 'codigo_estudiante' es Superclave)
## Caso 3
===================================================================
1. DEPENDENCIAS FUNCIONALES (DFs) VERDADERAS
===================================================================

DF1: {alumno, curso} -> profesor
(Un alumno inscrito en un curso específico tiene un único profesor asignado)

DF2: profesor -> curso
(Un profesor imparte únicamente un asignatura/curso específico)

===================================================================
2. ANÁLISIS FORMAL (CIERRE DE ATRIBUTOS Y CLAVES CANDIDATAS)
===================================================================

Esquema original: R(alumno, curso, profesor)
Clave Primaria Declarada: {alumno, curso}

Cierre de atributos:
- {alumno, curso}+    = {alumno, curso, profesor} = R  -->  Clave Candidata 1 (K1)
- {alumno, profesor}+ = {alumno, profesor, curso} = R  -->  Clave Candidata 2 (K2) 
  (Gracias a que DF2 establece que profesor -> curso)

Atributos Primos (pertenecen a al menos una clave candidata):
- alumno, curso, profesor  (¡TODOS los atributos del esquema son primos!)

Atributos No Primos:
- Ninguno.

===================================================================
3. EVALUACIÓN DE FORMAS NORMALES (3FN VS BCNF)
===================================================================

- 1FN: CUMPLE (todos los valores son atómicos).
- 2FN: CUMPLE (al no haber atributos no primos, no existen dependencias parciales).

- 3FN: CUMPLE
  * Para DF1: {alumno, curso} es Superclave (Cumple regla de BCNF/3FN).
  * Para DF2: 'profesor' NO es superclave, PERO el consecuente 'curso' ES UN ATRIBUTO PRIMO (pertenece a K1). 
  * La 3FN permite explícitamente esta excepción para atributos primos.

- BCNF: NO CUMPLE
  * La regla de BCNF es absoluta: para TODA DF no trivial X -> Y, el determinante X DEBE ser obligatoriamente Superclave.
  * En DF2 (profesor -> curso), 'profesor' NO es superclave de R (su cierre no produce 'alumno').
  * Por lo tanto, la tabla genera redundancia y anomalías de actualización/borrado.

===================================================================
4. ENTIDADES NORMALIZADAS EN BCNF (NOTACIÓN RELACIONAL)
===================================================================

-------------------------------------------------------------------
ENTIDAD 1: PROFESOR_CURSO (Catálogo / Asignación Docente)
-------------------------------------------------------------------
- Llave Primaria (PK) : profesor
- Atributos No Clave  : curso

Notación de Esquema:
PROFESOR_CURSO ( profesor [PK], curso )

Dependencia Funcional:
profesor -> curso
(Cumple BCNF porque 'profesor' es la Superclave completa)


-------------------------------------------------------------------
ENTIDAD 2: INSCRIPCION_ALUMNO (Registro de Matrícula)
-------------------------------------------------------------------
- Llave Primaria (PK) : alumno, profesor
- Llave Foránea (FK)  : profesor  --->  Referencia a PROFESOR_CURSO(profesor)

Notación de Esquema:
INSCRIPCION_ALUMNO ( alumno [PK], profesor [PK, FK] )

Dependencia Funcional:
{alumno, profesor} -> (Ningún atributo no clave)
(Cumple BCNF porque la PK compuesta cubre la totalidad de la entidad)

## Caso 4
===================================================================
1. DEPENDENCIAS FUNCIONALES (DFs) VERDADERAS
===================================================================

DF1: dni -> email, nombre, ciudad
(El DNI identifica de forma única a una persona, su correo, nombre y ciudad)

DF2: email -> dni, nombre, ciudad
(Al ser UNIQUE, el correo electrónico también identifica de forma única a una persona)

===================================================================
2. ANÁLISIS FORMAL (CIERRE DE ATRIBUTOS Y CLAVES CANDIDATAS)
===================================================================

Esquema original: R(dni, email, nombre, ciudad)
Clave Primaria Declarada: {dni}
Clave Única (Alternate Key): {email}

Cierre de atributos:
- {dni}+   = {dni, email, nombre, ciudad} = R   -->  Clave Candidata 1 (K1)
- {email}+ = {email, dni, nombre, ciudad} = R   -->  Clave Candidata 2 (K2)

Atributos Primos (pertenecen a al menos una clave candidata):
- dni, email

Atributos No Primos:
- nombre, ciudad

===================================================================
3. EVALUACIÓN DE FORMAS NORMALES (3FN Y BCNF)
===================================================================

- 1FN: CUMPLE (todos los atributos almacenan valores atómicos).
- 2FN: CUMPLE (las claves candidatas son simples de un solo atributo, no existen dependencias parciales).

- 3FN: CUMPLE
  * Para DF1 (dni -> ...), el determinante 'dni' es Superclave.
  * Para DF2 (email -> ...), el determinante 'email' es Superclave.
  * No existen dependencias transitivas entre atributos no primos.

- BCNF: CUMPLE
  * Para TODA dependencia funcional no trivial X -> Y en la tabla, el determinante X ('dni' en DF1 y 'email' en DF2) es estrictamente una Superclave.

===================================================================
4. DIAGNÓSTICO Y NOTACIÓN RELACIONAL FINAL
===================================================================

-------------------------------------------------------------------
ENTIDAD: PERSONA (Ya se encuentra en 3FN y BCNF)
-------------------------------------------------------------------
- Llave Primaria (PK)     : dni
- Llave Alternativa (AK)  : email (UNIQUE)
- Atributos No Clave      : nombre, ciudad

Notación de Esquema:
PERSONA ( dni [PK], email [AK], nombre, ciudad )

Conclusión:
Esta tabla NO REQUIERE DESCOMPOSICIÓN. Tener múltiples llaves candidatas 
simples (como DNI y Email) no viola la Forma Normal de Boyce-Codd 
siempre y cuando cada determinante sea una superclave por sí solo.

## Caso 5
===================================================================
1. DEPENDENCIAS FUNCIONALES (DFs) VERDADERAS
===================================================================

DF1: id_empleado -> nombre, ciudad
(El identificador de empleado determina de manera única a la persona y su ciudad)

===================================================================
2. ANÁLISIS FORMAL (CIERRE DE ATRIBUTOS Y CLAVES CANDIDATAS)
===================================================================

Esquema original: R(id_empleado, nombre, ciudad)
Clave Primaria Declarada: {id_empleado}

Cierre de atributos:
- {id_empleado}+ = {id_empleado, nombre, ciudad} = R   -->  Superclave y Clave Candidata Única (K1)

Atributos Primos (pertenecen a al menos una clave candidata):
- id_empleado

Atributos No Primos:
- nombre, ciudad

===================================================================
3. EVALUACIÓN DE FORMAS NORMALES (3FN Y BCNF)
===================================================================

- 1FN: CUMPLE (todos los atributos almacenan valores atómicos).
- 2FN: CUMPLE (la clave primaria es simple de un solo atributo, imposibilitando dependencias parciales).

- 3FN: CUMPLE
  * Para la dependencia DF1 (id_empleado -> nombre, ciudad), el determinante 'id_empleado' es la Superclave completa.
  * No existen dependencias transitivas entre los atributos no primos ('nombre' y 'ciudad' son independientes entre sí).

- BCNF: CUMPLE
  * La única dependencia funcional no trivial del esquema tiene como determinante a 'id_empleado', el cual es estrictamente una Superclave.

===================================================================
4. DIAGNÓSTICO Y NOTACIÓN RELACIONAL FINAL
===================================================================

-------------------------------------------------------------------
ENTIDAD: EMPLEADO (Ya se encuentra en 3FN y BCNF)
-------------------------------------------------------------------
- Llave Primaria (PK) : id_empleado
- Atributos No Clave  : nombre, ciudad

Notación de Esquema:
EMPLEADO ( id_empleado [PK], nombre, ciudad )

Conclusión:
Esta tabla NO REQUIERE DESCOMPOSICIÓN. Posee un diseño relacional atómico, 
sin dependencias parciales ni transitivas, cumpliendo de forma natural 
con los criterios de BCNF.