"""Generación y ejecución de SQL de migración."""

import re
from collections.abc import Iterable, Mapping


IDENTIFICADOR = re.compile(r"^[A-Za-z_][A-Za-z0-9_$]*$")


def validar_nombre_sql(nombre: str) -> str:
    """Valida y devuelve un identificador MySQL seguro."""
    if not isinstance(nombre, str) or not IDENTIFICADOR.fullmatch(nombre):
        raise ValueError(f"Identificador SQL inválido: {nombre!r}")
    return nombre


def escapar(nombre: str) -> str:
    """Escapa un identificador validado con comillas invertidas."""
    return f"`{validar_nombre_sql(nombre)}`"


def relaciones_demo() -> dict[str, frozenset[str]]:
    """Devuelve la descomposición demostrativa de pedidos_planos."""
    return {
        "clientes": frozenset({"id_cliente", "nombre_cliente", "ciudad_cliente"}),
        "productos": frozenset({"id_producto", "nombre_producto", "precio"}),
        "pedidos": frozenset({"id_pedido", "id_cliente"}),
        "detalle_pedido": frozenset({"id_pedido", "id_producto", "cantidad"}),
    }


def claves_demo() -> dict[str, tuple[str, ...]]:
    """Devuelve las claves primarias de la descomposición demostrativa."""
    return {
        "clientes": ("id_cliente",),
        "productos": ("id_producto",),
        "pedidos": ("id_pedido",),
        "detalle_pedido": ("id_pedido", "id_producto"),
    }


def generar_ddl(
    relaciones: Mapping[str, Iterable[str]],
    claves: Mapping[str, Iterable[str]],
    tipos: Mapping[str, str] | None = None,
    claves_foraneas: Iterable[tuple[str, tuple[str, ...], str, tuple[str, ...]]] = (),
) -> tuple[str, ...]:
    """Genera CREATE TABLE IF NOT EXISTS para relaciones propuestas.

    Definición formal: cada relación R_i se convierte en una tabla con los
    atributos declarados, su clave primaria y FK opcionales.
    parámetros: relaciones, claves, tipos SQL opcionales y FK como tuplas.
    retorno: tupla de sentencias CREATE TABLE.
    complejidad: O(sum(|R_i|)).
    """
    tipos = {} if tipos is None else dict(tipos)
    fk_por_tabla: dict[str, list[tuple[str, tuple[str, ...], str, tuple[str, ...]]]] = {}
    for fk in claves_foraneas:
        fk_por_tabla.setdefault(fk[0], []).append(fk)

    sentencias: list[str] = []
    for tabla, atributos in relaciones.items():
        validar_nombre_sql(tabla)
        nombres = tuple(sorted(frozenset(atributos)))
        primario = tuple(claves.get(tabla, ()))
        if not primario:
            raise ValueError(f"La relación {tabla} no tiene clave primaria.")

        columnas = [
            f"{escapar(nombre)} {tipos.get(nombre, 'VARCHAR(255)')} "
            f"{'NOT NULL' if nombre in primario else ''}".strip()
            for nombre in nombres
        ]
        columnas.append(
            f"PRIMARY KEY ({', '.join(escapar(nombre) for nombre in primario)})"
        )
        for _, locales, referencia, remotas in fk_por_tabla.get(tabla, []):
            columnas.append(
                f"FOREIGN KEY ({', '.join(escapar(nombre) for nombre in locales)}) "
                f"REFERENCES {escapar(referencia)} "
                f"({', '.join(escapar(nombre) for nombre in remotas)})"
            )
        sentencias.append(
            f"CREATE TABLE IF NOT EXISTS {escapar(tabla)} "
            f"({', '.join(columnas)})"
        )
    return tuple(sentencias)


def generar_insertar_desde(
    tabla_origen: str,
    relaciones: Mapping[str, Iterable[str]],
) -> tuple[str, ...]:
    """Genera INSERT INTO SELECT DISTINCT para migrar una tabla plana.

    parámetros: tabla_origen y mapa tabla->atributos.
    retorno: tupla de sentencias.
    complejidad: O(sum(|R_i|)).
    """
    validar_nombre_sql(tabla_origen)
    sentencias: list[str] = []
    for tabla, atributos in relaciones.items():
        nombres = tuple(sorted(frozenset(atributos)))
        columnas = ", ".join(escapar(nombre) for nombre in nombres)
        sentencias.append(
            f"INSERT INTO {escapar(tabla)} ({columnas}) "
            f"SELECT DISTINCT {columnas} FROM {escapar(tabla_origen)}"
        )
    return tuple(sentencias)


def generar_migracion_demo(tabla_origen: str = "pedidos_planos",
                           tipos: Mapping[str, str] | None = None) -> tuple[str, ...]:
    """Genera DDL e inserción completa para el caso demostrativo."""
    relaciones = relaciones_demo()
    claves = claves_demo()
    fks = (
        ("pedidos", ("id_cliente",), "clientes", ("id_cliente",)),
        ("detalle_pedido", ("id_pedido",), "pedidos", ("id_pedido",)),
        ("detalle_pedido", ("id_producto",), "productos", ("id_producto",)),
    )
    ddl = generar_ddl(relaciones, claves, tipos, fks)
    borrados = (
        "DELETE FROM `detalle_pedido`",
        "DELETE FROM `pedidos`",
        "DELETE FROM `productos`",
        "DELETE FROM `clientes`",
    )
    inserts = generar_insertar_desde(tabla_origen, relaciones)
    return ddl + borrados + inserts


def ejecutar_migracion(conexion, sentencias: Iterable[str],
                       solo_mostrar: bool = False) -> dict:
    """Ejecuta sentencias MySQL dentro de una transacción.

    parámetros: conexion abierta, sentencias SQL y modo solo_mostrar.
    retorno: dict con ejecutadas, modo y mensaje.
    complejidad: O(n), n sentencias.
    """
    lista = tuple(sentencias)
    if solo_mostrar:
        return {
            "ejecutadas": 0,
            "sentencias": lista,
            "mensaje": "Modo solo mostrar: no se ejecutó SQL.",
        }

    cursor = conexion.cursor()
    try:
        conexion.start_transaction()
        for sentencia in lista:
            cursor.execute(sentencia)
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
    return {
        "ejecutadas": len(lista),
        "sentencias": lista,
        "mensaje": "Migración ejecutada y confirmada.",
    }