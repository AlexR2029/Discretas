"""Verificación de dependencias funcionales contra datos MySQL."""

from collections.abc import Iterable

from src.dependencias import DF
from datos.lector_esquema import (
    escapar_identificador,
    validar_columnas,
    validar_tabla,
)


def verificar_df(conexion, tabla: str, df: DF) -> dict:
    """Verifica X -> Y comparando valores agrupados por X.

    Definición formal: X -> Y se cumple si para dos tuplas con el mismo valor
    de X, los valores de Y son iguales. Bajo semántica SQL, NULL solo es igual
    a NULL.
    parámetros: conexion abierta, tabla válida y DF con atributos válidos.
    retorno: dict con cumple, df, grupos_conflictivos y filas_conflictivas.
    complejidad: O(r·|X| + r·|Y|), r filas.
    """
    validar_tabla(conexion, tabla)
    validar_columnas(conexion, tabla, df.lado_izquierdo)
    validar_columnas(conexion, tabla, df.lado_derecho)

    x_columnas = sorted(df.lado_izquierdo)
    y_columnas = sorted(df.lado_derecho)
    x_sql = ", ".join(escapar_identificador(columna) for columna in x_columnas)
    y_sql = ", ".join(escapar_identificador(columna) for columna in y_columnas)

    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(
            f"SELECT {x_sql}, {y_sql} FROM {escapar_identificador(tabla)}"
        )
        filas = cursor.fetchall()
    finally:
        cursor.close()

    grupos: dict[tuple, set[tuple]] = {}
    for fila in filas:
        x = tuple(fila[columna] for columna in x_columnas)
        y = tuple(fila[columna] for columna in y_columnas)
        grupos.setdefault(x, set()).add(y)

    conflictos_por_grupo = [
        (x, sorted(valores, key=repr))
        for x, valores in sorted(grupos.items(), key=lambda item: repr(item[0]))
        if len(valores) > 1
    ]

    filas_conflictivas = []
    if conflictos_por_grupo:
        conflictivos = {x for x, _ in conflictos_por_grupo}
        for fila in filas:
            x = tuple(fila[columna] for columna in x_columnas)
            if x in conflictivos:
                filas_conflictivas.append(dict(fila))

    cumple = not conflictos_por_grupo
    mensaje = (
        f"Cumple {df}: para cada valor de X las tuplas tienen el mismo Y."
        if cumple
        else f"Viola {df}: se encontraron valores distintos de Y para el mismo X."
    )
    return {
        "cumple": cumple,
        "df": str(df),
        "tabla": tabla,
        "grupos_conflictivos": [
            {
                "X": dict(zip(x_columnas, x)),
                "valores_Y": [
                    dict(zip(y_columnas, valor)) for valor in valores
                ],
            }
            for x, valores in conflictos_por_grupo
        ],
        "filas_conflictivas": filas_conflictivas,
        "mensaje": mensaje,
    }


def verificar_dependencias(conexion, tabla: str,
                           dependencias: Iterable[DF]) -> tuple[dict, ...]:
    """Verifica varias DF y devuelve sus reportes individuales.

    parámetros: conexion, tabla y colección de DF.
    retorno: tupla de resultados de verificar_df.
    complejidad: O(d·r·(|X|+|Y|)), d DF y r filas.
    """
    return tuple(verificar_df(conexion, tabla, df) for df in dependencias)