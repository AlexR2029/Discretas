"""Carga de casos SQL predefinidos sin recrear la base."""

from pathlib import Path


CASOS_SQL = {
    "caso_1_2fn": "caso_1_2fn.sql",
    "caso_2_3fn": "caso_2_3fn.sql",
    "caso_3_bcnf": "caso_3_bcnf.sql",
    "caso_4_dos_claves": "caso_4_dos_claves.sql",
    "caso_5_bcnf_ok": "caso_5_bcnf_ok.sql",
}


def ruta_caso(nombre: str) -> Path:
    """Resuelve el archivo SQL de un caso existente.

    parámetros: nombre lógico del caso.
    retorno: ruta absoluta del script.
    complejidad: O(1).
    """
    if nombre not in CASOS_SQL:
        raise ValueError(f"Caso SQL desconocido: {nombre}")
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    ruta = scripts / CASOS_SQL[nombre]
    if not ruta.is_file():
        raise FileNotFoundError(f"No existe el script SQL: {ruta}")
    return ruta


def leer_caso(nombre: str) -> str:
    """Lee el contenido SQL de un caso.

    parámetros: nombre lógico del caso.
    retorno: contenido SQL.
    complejidad: O(n), n caracteres del script.
    """
    return ruta_caso(nombre).read_text(encoding="utf-8")


def ejecutar_caso(conexion, nombre: str) -> dict:
    """Ejecuta un caso SQL dentro de una transacción.

    parámetros: conexion MySQL abierta y nombre lógico del caso.
    retorno: dict con nombre y número de sentencias ejecutadas.
    complejidad: O(n), n sentencias del script.
    """
    sql = leer_caso(nombre)
    sentencias = tuple(
        bloque.strip()
        for bloque in sql.split(";")
        if bloque.strip()
    )
    cursor = conexion.cursor()
    try:
        conexion.rollback()
        conexion.start_transaction()
        for sentencia in sentencias:
            cursor.execute(sentencia)
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
    return {
        "caso": nombre,
        "sentencias": len(sentencias),
        "mensaje": f"Caso SQL cargado: {nombre}",
    }
