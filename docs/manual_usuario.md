# Manual de usuario

## Normalizador de Esquemas Relacionales

Herramienta académica para revisar dependencias funcionales, claves y formas
normales de tablas MySQL. La aplicación propone y, cuando se solicita, aplica
una descomposición conservando la tabla de origen.

## 1. Antes de empezar

- Windows 10 u 11.
- MySQL Server 8.x encendido.
- Base de datos `pruebas` creada en el servidor.
- Usuario MySQL con permisos para consultar tablas y crear tablas en `pruebas`.
- Para ejecutar el `.exe`, no hace falta instalar Python.

La interfaz se conecta a MySQL local por el puerto `3306` de forma
predeterminada. El puerto puede cambiarse si la instalación de MySQL usa otro.

## 2. Abrir y conectar

1. Abre `NormalizadorBD.exe`.
2. En la pestaña **Conexión**, completa **HOST**, **PORT**, **USER**,
   **PASSWORD** y **DATABASE**. Para una instalación local normal, el host
   suele ser `127.0.0.1`, el puerto `3306` y la base `pruebas`.
3. Escribe la contraseña del usuario MySQL que tienes autorizado a usar. La
   aplicación la oculta mientras la escribes.
4. Pulsa **Conectar**. Cuando se conecte, podrás listar tablas y columnas.

No compartas la contraseña ni la guardes en una captura. Si aparece
`Access denied`, revisa el usuario y su contraseña. Si aparece `Can't connect`,
comprueba que MySQL esté iniciado y que el host y el puerto sean correctos.

## 3. Cargar un caso SQL

En **Conexión**, elige uno de los cinco casos y pulsa **Cargar caso**. La
aplicación crea la tabla de ejemplo en la base conectada, limpia el estado
anterior, selecciona la tabla correspondiente y carga sus columnas. Puedes
establecer las DF antes de confirmar la tabla en **Análisis**.

| Caso | Tabla de origen | Tema |
| --- | --- | --- |
| `caso_1_2fn` | `caso_1_pedidos` | Dependencia parcial y 2FN |
| `caso_2_3fn` | `caso_2_estudiantes` | Dependencia transitiva y 3FN |
| `caso_3_bcnf` | `caso_3_asignaciones` | Diferencia entre 3FN y BCNF |
| `caso_4_dos_claves` | `caso_4_personas` | DNI y correo como claves |
| `caso_5_bcnf_ok` | `caso_5_empleados` | Tabla que ya cumple BCNF |

## 4. Declarar dependencias funcionales

Abre la pestaña **DF**. Escribe todas las dependencias para la tabla
confirmada, usando una flecha `->`. Separa atributos con comas y dependencias
con punto y coma. Pulsa **Agregar/establecer**.

Ejemplo para el caso 1:

```text
id_pedido,id_producto -> cantidad; id_producto -> nombre_producto,precio
```

Las dependencias de los demás casos son:

```text
Caso 2: codigo_estudiante -> nombres,programa; programa -> valor_semestre
Caso 3: alumno,curso -> profesor; profesor -> curso
Caso 4: dni -> email,nombre,ciudad; email -> dni,nombre,ciudad
Caso 5: id_empleado -> nombre,ciudad
```

**Verificar contra datos** comprueba las dependencias con las filas actuales de
MySQL y muestra conflictos cuando encuentra valores incompatibles.

## 5. Analizar una tabla

1. En **Análisis**, escribe o selecciona la tabla y pulsa **Confirmar Tabla**.
2. En el campo **X**, escribe los atributos iniciales separados por comas.
   También puedes escribir `X -> Y` para preguntar si X determina Y.
3. Pulsa **Calcular**.

El panel izquierdo organiza el resultado por secciones: cierre e implicación,
claves, formas normales y conclusión. **Calcular** solo actualiza este
resultado. La propuesta de la derecha se muestra cuando eliges **Dibujar
propuesta**.

### Formas normales en pocas palabras

- **1FN:** cada casilla guarda un solo valor.
- **2FN:** los datos no clave dependen de la clave completa, no de una parte.
- **3FN:** cada dependencia la determina una superclave o determina atributos
  que forman parte de claves candidatas.
- **BCNF:** todo determinante de una dependencia no trivial es una superclave.

## 6. Ver o ejecutar una propuesta

- Pulsa **Dibujar propuesta** para ver entidades, claves y relaciones sin
  modificar MySQL.
- Para crear las tablas normalizadas y migrar los datos, abre la pestaña
  **SQL**, genera el SQL del caso y revísalo antes de ejecutarlo.

La tabla original se conserva como fuente. Las sentencias de carga usan la
clave primaria o una clave UNIQUE para actualizar filas existentes y evitar
duplicados al ejecutar de nuevo.

## 7. Pestaña SQL

La pestaña **SQL** genera los esquemas del caso SQL que está confirmado en
**Análisis**, según `scripts/soluciones.md`. **Generar propuesta** prepara los
`CREATE TABLE` y las cargas desde la tabla de origen; **Solo mostrar** permite
revisarlos sin ejecutarlos y **Ejecutar** los aplica en la base configurada.
Las cargas usan `ON DUPLICATE KEY UPDATE` para actualizar las filas existentes
en vez de agregar duplicados.

## 8. Problemas frecuentes

| Mensaje o situación | Qué revisar |
| --- | --- |
| `Access denied (1045)` | Usuario, contraseña y permisos en MySQL. No es un problema de puerto. |
| `Can't connect` o `2003` | Servicio MySQL, host y puerto. |
| `Unknown database` | Que exista la base `pruebas` antes de conectarse. |
| No aparece la propuesta esperada | Confirma la tabla correcta y carga las DF completas del caso en la pestaña DF. |
| Se analizan atributos anteriores | Selecciona y confirma la nueva tabla; carga de nuevo sus DF. |

## 9. Flujo recomendado

Conectar a la base → cargar un caso → establecer las DF del caso si quieres →
confirmar la tabla → calcular → revisar el resumen → dibujar la propuesta →
generar y revisar el SQL → ejecutarlo solo cuando quieras migrar los datos.
