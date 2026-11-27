## Estado de avance

- Fase 4 (Interfaz): completada, según confirmación del equipo.
- Fase 5 (Pruebas de extremo a extremo): completada, según confirmación del
  equipo.
- Fase 6 (Empaquetado y entrega): iniciada.
- Preparado en esta fase: guía de salida limpia en
  `docs/fase6_entrega.md` y flujo de compilación en
  `scripts/build_release.ps1`.
- Pendiente para cerrar fase 6: congelar versiones reales, compilar y probar
  el `.exe` en Windows limpio, actualizar el README con versiones verificadas,
  preparar capturas y respaldo de sustentación, y etiquetar v1.0.

Para ejecutar las pruebas puras de fase 5:

```powershell
python -m unittest discover -s src -p "test_fase5*.py" -v
```

La prueba MySQL es opcional y solo se habilita contra `DATABASE=pruebas`:

```powershell
$env:RUN_MYSQL_E2E = "1"
python -m unittest discover -s src -p "test_fase5*.py" -v
```

## 1. Núcleo
Referencias en docs/info/: todas
Objetivo: tener todo el análisis matemático funcionando en memoria, sin base de datos ni interfaz.
Funcionalidades cubiertas: 3 (cierre y claves) y 4 (formas normales).

Qué se construye

nucleo/dependencias.py: clase DF inmutable con lado izquierdo y derecho como frozenset, y un parser de texto ("A, B -> C, D"). El parser valida que los atributos existan en el esquema y da mensajes de error claros.
nucleo/cierre.py: cierre(X, F) por punto fijo, implica(F, X, Y) y es_superclave(X, R, F).
nucleo/claves.py: claves_candidatas(R, F) con la optimización de atributos esenciales, y atributos_primos.
nucleo/formas_normales.py: es_2fn, es_3fn, es_bcnf, y 1FN como una verificación sobre el tipo de dato o un indicador de atomicidad.

Reglas de diseño

Los verificadores de formas normales devuelven un reporte, no un booleano. Por ejemplo: "viola 2FN porque nombre_cliente depende de id_cliente, que es parte de la clave". Ese texto alimenta la interfaz y el informe.
Las DF triviales se manejan explícitamente.
Ninguna importación de MySQL ni de Tkinter.

Criterio de cierre: 5 ejemplos de libro, con resultado calculado a mano por ustedes, pasan en unittest. Esos ejemplos deben incluir una tabla con una sola clave, una con varias claves candidatas y una ya en BCNF.

## 2. MySQL
Referencias en docs/info/: Bases de datos relacionales
Objetivo: que el programa lea esquemas reales del servidor y compruebe DF contra datos reales.
Funcionalidades cubiertas: 1 (conectar y listar) y 7 (verificar DF con datos).

Qué se construye

scripts/crear_bd_lab.sql: crea el esquema aislado pruebas, el usuario dedicado y la tabla de demostración pedidos_planos.
datos/conexion_mysql.py: lee HOST, DB_PORT, USER, PASSWORD y DATABASE del archivo `.env`, maneja errores (servidor apagado, credenciales erradas, base inexistente) y cierra conexiones bien.
datos/lector_esquema.py: consulta INFORMATION_SCHEMA y entrega tablas, columnas, tipos y claves primarias. Incluye un puente que convierte esa lectura en el objeto de esquema del núcleo.
datos/verificador_df.py: ejecuta GROUP BY X HAVING COUNT(DISTINCT Y) > 1 y devuelve las filas conflictivas.

Reglas de diseño

Los valores van en consultas parametrizadas. Los nombres de tabla y columna no se pueden parametrizar, así que se validan contra el INFORMATION_SCHEMA y se escapan con comillas invertidas.
Hay que definir qué se hace con los NULL en el verificador (se documenta la decisión, porque afecta el resultado de una DF).
Todo ocurre dentro de pruebas, nunca en otras bases.

Criterio de cierre: el programa lista las tablas de pruebas, y el verificador reporta como cumplida una DF correcta y como violada una DF falsa, mostrando las filas que la rompen.

## 3. Funcionalidades
Referencias en docs/info/: Relaciones, Bases de datos relacionales, BD1_MER_Normalización
Objetivo: implementar todo el resto de la lógica del programa.
Funcionalidades cubiertas: 2, 3 (cobertura mínima), 5, 6 y 8.

Es la fase más grande. Se divide en cuatro bloques, cada uno con su propia sesión y sus pruebas.

3a. Cobertura mínima y gestión de DF (nucleo/cobertura.py)

Lado derecho unitario, eliminación de atributos extraños, eliminación de DF redundantes.
Modelo para agregar, editar y eliminar DF, con guardado y carga en JSON.
Prueba clave: la cobertura calculada es equivalente al conjunto original (cada una implica a la otra).

3b. Síntesis a 3FN (nucleo/descomposicion.py)

Una relación por DF de la cobertura mínima, agrupando por lado izquierdo, más una relación con la clave si ninguna la contiene, y eliminando relaciones contenidas en otras.
Prueba clave: el resultado está en 3FN y preserva las dependencias.

3c. Descomposición BCNF y tableau (nucleo/descomposicion.py, nucleo/tableau.py)

División recursiva por DF violadora X→Y en (X∪Y) y (R−(Y−X)).
Prueba de sin pérdida por tableau (chase) y verificación de preservación de dependencias.
Debe informar cuando BCNF pierde alguna dependencia, que es un resultado teórico legítimo y bueno para el informe.

3d. SQL de migración y casos

datos/generador_sql.py: CREATE TABLE para cada relación resultante e INSERT INTO ... SELECT DISTINCT para migrar. La ejecución es transaccional, con un modo "solo mostrar" antes de ejecutar.

Criterio de cierre: pedidos_planos se descompone en clientes, productos, pedidos y detalle_pedido, el tableau confirma que no hay pérdida, y el SQL generado se ejecuta en localhost sin errores.

## 4. Interfaz
Referencias en docs/info/: BD1_MER_Normalización
Objetivo: que todo el flujo se use sin consola.

Qué se construye (interfaz/app_tk.py y main.py)

Pestaña	Función
Conexión	Host, puerto, usuario, estado de la conexión, lista de tablas y columnas
DF	Tabla editable de dependencias, botón de verificar contra datos
Análisis	Cierre de un conjunto, claves candidatas, cobertura mínima y reporte de formas normales por tabla
SQL	Descomposición propuesta, SQL generado, ejecución y resultado

Reglas de diseño

Cero lógica matemática dentro de la interfaz. Solo llama a funciones de nucleo/, laboratorio/ y datos/. Así la interfaz se puede rehacer sin tocar nada probado.
Un objeto de estado compartido (esquema actual, DF, resultados) que todas las pestañas leen.
Los errores se muestran en cuadros de mensaje, nunca solo en consola.
Con Tkinter conviene evitar bloquear la ventana en consultas largas; basta con avisar "procesando" en operaciones pesadas.

Criterio de cierre: el caso de demostración completo se ejecuta de principio a fin usando solo la interfaz.

## 5. Pruebas de extremo a extremo
Referencias en docs/info/: BD1_MER_Normalización
Objetivo: demostrar con evidencia que el programa es correcto y robusto.

Qué se prueba

Ida y vuelta: se parte de un diseño bien normalizado conocido, se desnormaliza con el join propio, se crea la tabla plana en MySQL, el normalizador la analiza sin conocer el diseño original, y el join de las partes resultantes debe reproducir exactamente el conjunto de filas original (igualdad de conjuntos).
Casos límite: tabla ya en BCNF (el programa debe decir que no hay nada que hacer), clave única, varias claves candidatas, DF triviales y DF mal escritas.
Errores: servidor MySQL apagado, credenciales erradas, tabla inexistente.
Reproducibilidad: la misma semilla produce los mismos datos en otra máquina.
Rendimiento: claves candidatas con 10 a 14 atributos, para medir el crecimiento exponencial. Esos tiempos van como tabla en el informe.
Revisión cruzada: cada integrante revisa y explica el módulo de otro.

Criterio de cierre: las pruebas de ida y vuelta pasan, y la lista de control de robustez de la guía (sección 6.3) está completamente marcada.

## 6. Empaquetado y entrega
Referencias en docs/info/: todas
Objetivo: que el docente pueda ejecutar el proyecto sin fallos.

Qué se hace

Congelar versiones exactas en requirements.txt y completar la sección 3 del README (Python, MySQL, conector).
Generar el .exe con PyInstaller y probarlo en un equipo sin Python instalado.
Seguir el README al pie de la letra en una máquina limpia. Si algo falla, el error está en el README, no en la máquina.
Tomar las capturas para el manual de usuario con el caso de demostración y la semilla fija.
Preparar un plan de respaldo para la sustentación: capturas y un video corto por si MySQL falla.
Etiquetar la versión final (v1.0).

Criterio de cierre: una persona ajena al equipo instala y ejecuta el programa solo con el README.

