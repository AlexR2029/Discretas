"""Conexión administrada con MySQL para los casos SQL."""

import os
from collections.abc import Mapping
from pathlib import Path

import mysql.connector
from mysql.connector import Error as MySQLError


class ErrorConexionMySQL(Exception):
    """Error seguro para fallos de conexión o configuración MySQL."""


def cargar_archivo_env(ruta: str | Path | None = None) -> dict[str, str]:
    """Carga variables simples desde un archivo .env sin mostrar secretos.

    Definición formal: se transforma cada línea KEY=VALUE en una entrada.
    Los valores ya presentes en el entorno del sistema tienen prioridad.
    parámetros: ruta opcional del archivo .env.
    retorno: diccionario con las variables reconocidas.
    complejidad: O(n), n líneas del archivo.
    """
    ruta_env = (Path(__file__).resolve().parents[1] / ".env"
                if ruta is None else Path(ruta))
    valores: dict[str, str] = {}
    if not ruta_env.is_file():
        return valores

    for linea in ruta_env.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        clave = clave.strip()
        valor = valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in {'"', "'"}:
            valor = valor[1:-1]
        if clave:
            valores[clave] = valor
    return valores


def leer_configuracion_mysql(entorno: Mapping[str, str] | None = None) -> dict:
    """Lee la configuración MySQL desde variables de entorno.

    Definición formal: este adaptador transforma variables externas en
    parámetros de conexión sin almacenar credenciales en el código.
    parámetros: entorno es un mapeo opcional compatible con os.environ.
    retorno: diccionario con host, puerto, usuario, contraseña y base.
    complejidad: O(1).
    """
    archivo_env = cargar_archivo_env()
    fuente: Mapping[str, str]
    if entorno is None:
        fuente = os.environ
    else:
        fuente = entorno

    def valor(clave: str, defecto: str = "") -> str:
        if clave in fuente:
            return fuente[clave]
        return archivo_env.get(clave, defecto)

    return {
        "host": valor("HOST", ""),
        "port": valor("DB_PORT", ""),
        "user": valor("USER", ""),
        "password": valor("PASSWORD", ""),
        "database": valor("DATABASE", ""),
    }


def abrir_conexion(configuracion: Mapping[str, object] | None = None):
    """Abre una conexión MySQL hacia el esquema indicado.

    parámetros: configuracion usa las claves devueltas por
    leer_configuracion_mysql; si se omite, lee las variables de entorno.
    retorno: objeto de conexión de mysql-connector-python.
    complejidad: O(1) de código, más la latencia del servidor.
    """
    config = leer_configuracion_mysql() if configuracion is None else dict(configuracion)
    try:
        faltantes = [
            clave for clave in ("host", "port", "user", "database")
            if not str(config.get(clave, "")).strip()
        ]
        if faltantes:
            nombres = {
                "host": "HOST",
                "port": "DB_PORT",
                "user": "USER",
                "database": "DATABASE",
            }
            raise ErrorConexionMySQL(
                "Faltan variables MySQL en .env: "
                + ", ".join(nombres[clave] for clave in faltantes)
            )
        parametros = {
            "host": config["host"],
            "port": int(config["port"]),
            "user": config["user"],
            "password": config["password"],
        }
        if config.get("database"):
            parametros["database"] = config["database"]
        conexion = mysql.connector.connect(**parametros)
        if not conexion.is_connected():
            raise ErrorConexionMySQL("MySQL no aceptó la conexión.")
        return conexion
    except MySQLError as error:
        raise ErrorConexionMySQL(
            f"No fue posible conectar a MySQL: {error}"
        ) from error


def cerrar_conexion(conexion) -> None:
    """Cierra una conexión MySQL si todavía está abierta.

    parámetros: conexion es un objeto de mysql-connector-python.
    retorno: None.
    complejidad: O(1).
    """
    if conexion is not None and getattr(conexion, "is_connected", lambda: False)():
        conexion.close()