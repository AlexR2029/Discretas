# Trabajo restante

Este documento describe únicamente el porcentaje pendiente de integración.
No redefine el alcance ya implementado del proyecto.

## Prioridad alta

1. Completar las propuestas de los cinco casos SQL en `datos/propuestas.py`.
   - Caso 1: confirmar `PRODUCTO`, `PEDIDO` y `DETALLE_PEDIDO`.
   - Caso 2: confirmar `PROGRAMA` y `ESTUDIANTE`.
   - Caso 3: confirmar `PROFESOR_CURSO` y `INSCRIPCION_ALUMNO`.
   - Caso 4: confirmar que `PERSONA` permanece como una sola entidad.
   - Caso 5: confirmar que `EMPLEADO` permanece como una sola entidad.

2. Completar la aplicación de cada propuesta en MySQL.
   - Crear las entidades normalizadas con sus PK y FK reales.
   - Crear las AK/UNIQUE necesarias.
   - Migrar datos desde la tabla original sin perder filas ni claves.
   - Mantener la tabla original como fuente hasta finalizar la migración.
   - Aplicar cambios dentro de una transacción y mostrar errores reales.

3. Verificar la migración por caso.
   - Comprobar que las propuestas tienen los atributos definidos.
   - Comprobar que las relaciones tienen destinos existentes.
   - Comprobar que el conteo y las asociaciones de datos son correctos.
   - Comprobar que no se crean nombres de entidad incorrectos.

4. Completar la limpieza de memoria compartida.
   - Al cambiar de caso SQL, limpiar tablas, columnas, DF, claves y resultados.
   - Al cambiar de tabla confirmada, limpiar únicamente el estado asociado
     a la tabla anterior.
   - No reutilizar atributos o resultados de una tabla reemplazada.

## Propuesta gráfica

1. Dibujar entidades normalizadas con atributos PK, FK y AK claramente
   identificados.
2. Dibujar flechas reales entre entidades mediante sus atributos FK/PK.
3. Diferenciar visualmente una entidad sin descomposición de una entidad
   descompuesta.
4. Evitar nombres, relaciones o atributos generados por coincidencias
   accidentales de conjuntos.

## DF y análisis

1. Mantener la sintaxis única `X -> Y,Z` sin inferir Y o Z.
2. Cargar las DF del usuario desde la pestaña DF y conservarlas asociadas a
   la tabla confirmada actual.
3. No recalcular validaciones con DF antiguas después de cargar otro caso.
4. Revisar con casos reales que:
   - 2FN detecte dependencias parciales;
   - 3FN permita atributos primos cuando corresponda;
   - BCNF detecte determinantes que no sean superclave;
   - una tabla ya en 3FN/BCNF no requiera descomposición.

## Pruebas mínimas finales

1. Ejecutar los cinco scripts contra la base `pruebas`.
2. Verificar las tablas principales creadas por cada caso.
3. Verificar las propuestas estructuradas de los cinco casos.
4. Ejecutar al menos una prueba real de aplicación por caso.
5. Ejecutar:

```text
python -m unittest discover -s tests -v
```

## Excluido de este porcentaje pendiente

- Diseño manual de tablas desde el Laboratorio.
- Pruebas extremo a extremo completas.
- Empaquetado como `.exe`.
- Implementación de interfaz para fases posteriores.

## Fases faltantes

- 5
- 6