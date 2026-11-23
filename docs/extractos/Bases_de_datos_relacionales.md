# Extracto: Bases de datos relacionales

Fuente: `Bases de datos relacionales.pdf`; páginas del PDF.

## Definiciones y conceptos

- **Base de datos relacional (p. 1):** conjunto de tablas con filas
  (registros/tuplas) y columnas (campos/atributos); tablas distintas pueden
  compartir campos para relacionarse.
- **Entidad y atributo (p. 1):** cada fila representa una entidad y cada
  columna una característica de las entidades del mismo tipo.
- **Tipos atómicos (p. 1):** enteros, reales y cadenas de longitud variable se
  presentan como tipos simples que favorecen el manejo de datos.
- **Cardinalidades entre tablas (p. 2):** uno-a-uno, uno-a-varios y
  varios-a-varios.
- **SQL (p. 2):** lenguaje declarativo que especifica el resultado de una
  consulta; incluye creación, inserción, modificación, borrado y selección.
- **Tupla y resultado de consulta (p. 3):** una consulta puede devolver
  valores, tuplas o tablas filtradas por condiciones.
- **Modelo geo-relacional (pp. 4--6):** enlaza tablas temáticas y objetos
  espaciales por identificadores comunes.

## Ejemplos desarrollados

- **Esquema municipal (p. 1):** tres tablas comparten `ident`, que identifica
  municipios y permite relacionar nombres, usos del suelo y población.
- **Consulta SQL (p. 3):** `SELECT id, nombre, pob1991 ... WHERE pob1991>20000`
  devuelve las columnas y filas que cumplen el filtro; seleccionar solo
  `pob1991` devuelve un valor por municipio coincidente.
- **Consulta geo-relacional (p. 4):** un filtro de crecimiento poblacional
  selecciona identificadores y nombres para representarlos espacialmente.
- **Consulta por ubicación (p. 6):** un clic dentro de un polígono se traduce
  en una condición como `id=17`, y el resultado se postprocesa en el SIG.

El PDF no define formalmente dependencias funcionales, claves, cierre,
normalización, descomposición ni la operación `JOIN`.
