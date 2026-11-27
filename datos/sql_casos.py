"""Migraciones SQL de los esquemas publicados en scripts/soluciones.md."""

from dataclasses import dataclass

from datos.generador_sql import escapar, validar_nombre_sql
from datos.propuestas import TABLA_ORIGEN_CASO


@dataclass(frozen=True, slots=True)
class TablaDestinoSQL:
    nombre: str
    columnas: tuple[tuple[str, str], ...]
    pk: tuple[str, ...]
    unicas: tuple[tuple[str, tuple[str, ...]], ...] = ()
    fks: tuple[tuple[str, str, str], ...] = ()


# Los nombres, tipos, claves y relaciones corresponden a los DDL de
# scripts/soluciones.md.
ESQUEMAS_SQL_CASO: dict[str, tuple[TablaDestinoSQL, ...]] = {
    "caso_1_2fn": (
        TablaDestinoSQL(
            "productos",
            (("id_producto", "INT"), ("nombre_producto", "VARCHAR(100)"),
             ("precio", "DECIMAL(10,2)")),
            ("id_producto",),
        ),
        TablaDestinoSQL(
            "pedido_detalles",
            (("id_pedido", "INT"), ("id_producto", "INT"), ("cantidad", "INT")),
            ("id_pedido", "id_producto"),
            fks=(("id_producto", "productos", "id_producto"),),
        ),
    ),
    "caso_2_3fn": (
        TablaDestinoSQL(
            "programas",
            (("programa", "VARCHAR(100)"), ("valor_semestre", "DECIMAL(12,2)")),
            ("programa",),
        ),
        TablaDestinoSQL(
            "estudiantes",
            (("codigo_estudiante", "INT"), ("nombres", "VARCHAR(100)"),
             ("programa", "VARCHAR(100)")),
            ("codigo_estudiante",),
            fks=(("programa", "programas", "programa"),),
        ),
    ),
    "caso_3_bcnf": (
        TablaDestinoSQL(
            "profesores_cursos",
            (("profesor", "VARCHAR(100)"), ("curso", "VARCHAR(50)")),
            ("profesor",),
        ),
        TablaDestinoSQL(
            "alumno_profesor",
            (("alumno", "VARCHAR(50)"), ("profesor", "VARCHAR(100)")),
            ("alumno", "profesor"),
            fks=(("profesor", "profesores_cursos", "profesor"),),
        ),
    ),
    "caso_4_dos_claves": (
        TablaDestinoSQL(
            "personas",
            (("dni", "VARCHAR(20)"), ("email", "VARCHAR(120)"),
             ("nombre", "VARCHAR(100)"), ("ciudad", "VARCHAR(100)")),
            ("dni",),
            unicas=(("uk_persona_email", ("email",)),),
        ),
    ),
    "caso_5_bcnf_ok": (
        TablaDestinoSQL(
            "empleados",
            (("id_empleado", "INT"), ("nombre", "VARCHAR(100)"),
             ("ciudad", "VARCHAR(100)")),
            ("id_empleado",),
        ),
    ),
}


def tablas_destino_caso(nombre_caso: str) -> tuple[str, ...]:
    """Devuelve las tablas destino de un caso en orden de carga."""
    try:
        return tuple(tabla.nombre for tabla in ESQUEMAS_SQL_CASO[nombre_caso])
    except KeyError as error:
        raise ValueError(f"Caso SQL desconocido: {nombre_caso}") from error


def generar_migracion_caso(
    nombre_caso: str,
    tabla_origen: str | None = None,
) -> tuple[str, ...]:
    """Genera DDL y upserts para el caso y su tabla de origen asignados."""
    try:
        esquemas = ESQUEMAS_SQL_CASO[nombre_caso]
        origen_esperado = TABLA_ORIGEN_CASO[nombre_caso]
    except KeyError as error:
        raise ValueError(f"Caso SQL desconocido: {nombre_caso}") from error
    origen = (
        origen_esperado
        if tabla_origen is None
        else validar_nombre_sql(tabla_origen)
    )
    if origen != origen_esperado:
        raise ValueError(
            f"El caso {nombre_caso} requiere la tabla de origen "
            f"{origen_esperado}; se recibió {origen}."
        )
    return (
        tuple(_crear_tabla_destino(esquema) for esquema in esquemas)
        + tuple(_crear_upsert(origen, esquema) for esquema in esquemas)
    )


def _crear_tabla_destino(esquema: TablaDestinoSQL) -> str:
    validar_nombre_sql(esquema.nombre)
    definiciones = [
        f"{escapar(nombre)} {tipo} NOT NULL"
        for nombre, tipo in esquema.columnas
    ]
    definiciones.append(
        "PRIMARY KEY (" + ", ".join(escapar(nombre) for nombre in esquema.pk) + ")"
    )
    for nombre_indice, columnas in esquema.unicas:
        definiciones.append(
            f"CONSTRAINT {escapar(nombre_indice)} UNIQUE "
            f"({', '.join(escapar(nombre) for nombre in columnas)})"
        )
    for local, referida, remota in esquema.fks:
        definiciones.append(
            f"FOREIGN KEY ({escapar(local)}) REFERENCES {escapar(referida)} "
            f"({escapar(remota)}) ON DELETE RESTRICT ON UPDATE CASCADE"
        )
    cuerpo = ",\n".join(f"    {definicion}" for definicion in definiciones)
    return (
        f"CREATE TABLE IF NOT EXISTS {escapar(esquema.nombre)} (\n"
        f"{cuerpo}\n"
        ")"
    )


def _crear_upsert(origen: str, esquema: TablaDestinoSQL) -> str:
    columnas = tuple(nombre for nombre, _ in esquema.columnas)
    lista_columnas = ",\n".join(
        f"    {escapar(nombre)}" for nombre in columnas
    )
    actualizaciones = ",\n".join(
        f"    {escapar(nombre)} = VALUES({escapar(nombre)})"
        for nombre in columnas
    )
    return (
        f"INSERT INTO {escapar(esquema.nombre)} (\n"
        f"{lista_columnas}\n"
        ")\n"
        "SELECT DISTINCT\n"
        f"{lista_columnas}\n"
        f"FROM {escapar(origen)}\n"
        "WHERE 1\n"
        "ON DUPLICATE KEY UPDATE\n"
        f"{actualizaciones}"
    )
