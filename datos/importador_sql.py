"""Lectura controlada de scripts SQL seleccionados por el usuario."""

from dataclasses import dataclass
from pathlib import Path
import re


_COMANDOS_PELIGROSOS = re.compile(
    r"^\s*(?:DROP\s+(?:TABLE|VIEW)|TRUNCATE\s+TABLE|DELETE\s+FROM|"
    r"ALTER\s+TABLE|RENAME\s+TABLE)\b",
    re.IGNORECASE,
)
_COMANDOS_BLOQUEADOS = re.compile(
    r"^\s*(?:DROP\s+(?:DATABASE|SCHEMA)|"
    r"CREATE\s+USER|DROP\s+USER|ALTER\s+USER|"
    r"GRANT|REVOKE|SET\s+(?:GLOBAL|PERSIST))\b",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class ArchivoSQL:
    """Sentencias listas para ejecutarse en la base activa."""

    ruta: Path
    sentencias: tuple[str, ...]
    directivas_omitidas: int
    sentencias_peligrosas: tuple[str, ...]


def separar_sentencias(sql: str) -> tuple[str, ...]:
    """Separa instrucciones por punto y coma respetando cadenas y comentarios."""
    sentencias: list[str] = []
    actual: list[str] = []
    estado = "normal"
    indice = 0

    while indice < len(sql):
        caracter = sql[indice]
        siguiente = sql[indice + 1] if indice + 1 < len(sql) else ""

        if estado == "normal":
            if caracter in ("'", '"', chr(96)):
                estado = caracter
                actual.append(caracter)
            elif caracter == "#" or (
                caracter == "-"
                and siguiente == "-"
                and (indice + 2 == len(sql) or sql[indice + 2].isspace())
            ):
                estado = "comentario_linea"
                actual.append(" ")
                if caracter == "-":
                    indice += 1
            elif caracter == "/" and siguiente == "*":
                estado = "comentario_bloque"
                actual.append(" ")
                indice += 1
            elif caracter == ";":
                sentencia = "".join(actual).strip()
                if sentencia:
                    sentencias.append(sentencia)
                actual.clear()
            else:
                actual.append(caracter)
        elif estado == "comentario_linea":
            if caracter in "\r\n":
                estado = "normal"
                actual.append(" ")
        elif estado == "comentario_bloque":
            if caracter == "*" and siguiente == "/":
                estado = "normal"
                indice += 1
        else:
            actual.append(caracter)
            if caracter == "\\" and siguiente:
                indice += 1
                actual.append(sql[indice])
            elif caracter == estado:
                if siguiente == estado:
                    indice += 1
                    actual.append(sql[indice])
                else:
                    estado = "normal"
        indice += 1

    if estado in ("comentario_bloque", "'", '"', chr(96)):
        raise ValueError("El archivo SQL termina con una cadena o comentario sin cerrar.")
    sentencia = "".join(actual).strip()
    if sentencia:
        sentencias.append(sentencia)
    return tuple(sentencias)


def preparar_archivo_sql(ruta: str | Path) -> ArchivoSQL:
    """Lee un archivo y mantiene la base elegida por la conexión actual."""
    archivo = Path(ruta)
    sql = archivo.read_text(encoding="utf-8-sig")
    instrucciones = separar_sentencias(sql)
    preparadas: list[str] = []
    omitidas = 0
    peligrosas: list[str] = []

    for sentencia in instrucciones:
        if re.match(r"^\s*DELIMITER\b", sentencia, re.IGNORECASE):
            raise ValueError(
                "Este archivo define DELIMITER o rutinas SQL; la importación "
                "admite sentencias SQL estándar, pero no procedimientos ni triggers."
            )
        if re.match(
            r"^\s*CREATE\s+(?:OR\s+REPLACE\s+)?"
            r"(?:DEFINER\s*=\s*\S+\s+)?"
            r"(?:PROCEDURE|FUNCTION|TRIGGER|EVENT)\b",
            sentencia,
            re.IGNORECASE,
        ):
            raise ValueError(
                "Los archivos con procedimientos, funciones, eventos o triggers "
                "no son compatibles con la importación."
            )
        if re.match(r"^\s*CREATE\s+DATABASE\b", sentencia, re.IGNORECASE):
            omitidas += 1
            continue
        if re.match(r"^\s*CREATE\s+SCHEMA\b", sentencia, re.IGNORECASE):
            omitidas += 1
            continue
        if re.match(r"^\s*USE\b", sentencia, re.IGNORECASE):
            omitidas += 1
            continue
        if _COMANDOS_BLOQUEADOS.match(sentencia):
            raise ValueError(
                "El archivo contiene una instrucción de administración del servidor "
                "que la aplicación no permite importar."
            )
        if re.match(r"^\s*(?:LOCK\s+TABLES|UNLOCK\s+TABLES)\b", sentencia,
                    re.IGNORECASE):
            omitidas += 1
            continue
        if re.match(r"^\s*SET\b", sentencia, re.IGNORECASE):
            omitidas += 1
            continue
        if _COMANDOS_PELIGROSOS.match(sentencia):
            peligrosas.append(sentencia)
        preparadas.append(sentencia)

    if not preparadas:
        raise ValueError("El archivo no contiene instrucciones SQL para importar.")
    return ArchivoSQL(
        archivo,
        tuple(preparadas),
        omitidas,
        tuple(peligrosas),
    )


def ejecutar_archivo_sql(conexion, archivo: ArchivoSQL) -> dict:
    """Ejecuta el script en la base de datos de la conexión activa."""
    cursor = conexion.cursor()
    ejecutadas = 0
    try:
        for sentencia in archivo.sentencias:
            cursor.execute(sentencia)
            ejecutadas += 1
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
    return {"ejecutadas": ejecutadas, "omitidas": archivo.directivas_omitidas}
