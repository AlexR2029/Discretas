"""Lectura de tablas y columnas desde INFORMATION_SCHEMA."""

import re
from collections.abc import Iterable


IDENTIFICADOR = re.compile(r"^[A-Za-z_][A-Za-z0-9_$]*$")


def escapar_identificador(nombre: str) -> str:
    """Escapa un identificador SQL después de validar su forma.

    parámetros: nombre es el nombre de tabla o columna.
    retorno: nombre entre comillas invertidas.
    complejidad: O(|nombre|).
    """
    if not isinstance(nombre, str) or not IDENTIFICADOR.fullmatch(nombre):
        raise ValueError(f"Identificador SQL inválido: {nombre!r}")
    return f"`{nombre}`"


def listar_tablas(conexion) -> tuple[str, ...]:
    """Lista las tablas visibles del esquema configurado.

    parámetros: conexion es una conexión MySQL abierta.
    retorno: tupla de nombres de tabla ordenada.
    complejidad: O(n log n), donde n es la cantidad de tablas.
    """
    consulta = (
        "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE' "
        "ORDER BY TABLE_NAME"
    )
    cursor = conexion.cursor()
    try:
        cursor.execute(consulta, (conexion.database,))
        return tuple(fila[0] for fila in cursor.fetchall())
    finally:
        cursor.close()


def listar_columnas(conexion, tabla: str) -> tuple[dict, ...]:
    """Lista los atributos de una tabla y sus metadatos básicos.

    parámetros: conexion abierta y nombre validado de tabla.
    retorno: tupla de diccionarios con nombre, tipo, nulabilidad y clave primaria.
    complejidad: O(n log n), donde n es el número de columnas.
    """
    validar_tabla(conexion, tabla)
    consulta = (
        "SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, "
        "COLUMN_KEY, ORDINAL_POSITION "
        "FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
        "ORDER BY ORDINAL_POSITION"
    )
    cursor = conexion.cursor()
    try:
        cursor.execute(consulta, (conexion.database, tabla))
        return tuple({
            "nombre": fila[0],
            "tipo": fila[1],
            "permite_nulos": fila[2] == "YES",
            "clave_primaria": fila[3] == "PRI",
        } for fila in cursor.fetchall())
    finally:
        cursor.close()


def validar_tabla(conexion, tabla: str) -> None:
    """Comprueba que una tabla existe dentro del esquema activo.

    parámetros: conexion abierta y nombre de tabla.
    retorno: None o ValueError si no existe.
    complejidad: O(n), donde n es la cantidad de tablas del esquema.
    """
    escapar_identificador(tabla)
    if tabla not in listar_tablas(conexion):
        raise ValueError(
            f"La tabla {tabla!r} no existe en el esquema configurado "
            f"{conexion.database!r}."
        )


def validar_columnas(conexion, tabla: str,
                     columnas: Iterable[str]) -> frozenset[str]:
    """Valida atributos contra INFORMATION_SCHEMA.

    parámetros: conexion, tabla y nombres de atributos.
    retorno: frozenset con los nombres validados.
    complejidad: O(n+m), n columnas declaradas y m atributos pedidos.
    """
    validar_tabla(conexion, tabla)
    disponibles = frozenset(
        columna["nombre"] for columna in listar_columnas(conexion, tabla)
    )
    solicitadas = frozenset(columnas)
    desconocidas = solicitadas - disponibles
    if desconocidas:
        raise ValueError(
            "Atributos inexistentes en la tabla "
            f"{tabla}: {', '.join(sorted(desconocidas))}"
        )
    return solicitadas


def listar_claves(conexion, tabla: str) -> dict:
    """Lee PK, FK y AK declaradas en INFORMATION_SCHEMA.

    Definición formal: PK es la clave primaria de la tabla; FK representa
    atributos que referencian otra tabla; AK agrupa columnas con índice UNIQUE
    que no sea la clave primaria.
    parámetros: conexion abierta y nombre de tabla válido.
    retorno: diccionario con pk, fk y aks como conjuntos.
    complejidad: O(n log n), n columnas o índices consultados.
    """
    validar_tabla(conexion, tabla)
    columnas = listar_columnas(conexion, tabla)
    pk = frozenset(
        columna["nombre"] for columna in columnas
        if columna["clave_primaria"]
    )

    cursor = conexion.cursor()
    try:
        cursor.execute(
            "SELECT COLUMN_NAME "
            "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
            "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
            "AND REFERENCED_TABLE_NAME IS NOT NULL "
            "ORDER BY ORDINAL_POSITION",
            (conexion.database, tabla),
        )
        fk = frozenset(fila[0] for fila in cursor.fetchall())

        cursor.execute(
            "SELECT INDEX_NAME, COLUMN_NAME, SEQ_IN_INDEX "
            "FROM INFORMATION_SCHEMA.STATISTICS "
            "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
            "AND NON_UNIQUE = 0 "
            "ORDER BY INDEX_NAME, SEQ_IN_INDEX",
            (conexion.database, tabla),
        )
        grupos: dict[str, set[str]] = {}
        for indice, columna, _ in cursor.fetchall():
            if indice != "PRIMARY":
                grupos.setdefault(indice, set()).add(columna)
        aks = tuple(
            frozenset(grupos[indice])
            for indice in sorted(grupos)
        )
    finally:
        cursor.close()

    return {"pk": pk, "fk": fk, "aks": aks}


def esquema_para_nucleo(conexion, tabla: str) -> dict:
    """Convierte la lectura de información a estructuras del núcleo.

    parámetros: conexion abierta y nombre de tabla.
    retorno: diccionario con atributos como frozenset y tipos por atributo.
    complejidad: O(n), n columnas de la tabla.
    """
    columnas = listar_columnas(conexion, tabla)
    atributos = frozenset(columna["nombre"] for columna in columnas)
    tipos = {columna["nombre"]: columna["tipo"] for columna in columnas}
    atomicos = {
        columna["nombre"]: columna["tipo"].split("(", 1)[0].lower()
        not in {"json", "array", "set", "struct", "list", "map"}
        for columna in columnas
    }
    return {
        "tabla": tabla,
        "atributos": atributos,
        "tipos": tipos,
        "atomicos": atomicos,
    }