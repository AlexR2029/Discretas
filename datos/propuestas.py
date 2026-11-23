"""Propuestas normalizadas basadas en scripts/soluciones.md."""

from dataclasses import dataclass
from collections.abc import Iterable

from src.dependencias import DF
from src.cierre import implica


@dataclass(frozen=True, slots=True)
class EntidadPropuesta:
    nombre: str
    pk: tuple[str, ...]
    fk: tuple[tuple[str, str, str], ...]
    ak: tuple[str, ...]
    atributos: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RelacionPropuesta:
    origen: str
    destino: str
    atributo_origen: str
    atributo_destino: str


@dataclass(frozen=True, slots=True)
class PropuestaCaso:
    entidades: tuple[EntidadPropuesta, ...]
    relaciones: tuple[RelacionPropuesta, ...]


PROPUESTAS = {
    "caso_1_2fn": PropuestaCaso(
        (
            EntidadPropuesta(
                "PRODUCTO",
                ("id_producto",),
                (),
                (),
                ("id_producto", "nombre_producto", "precio"),
            ),
            EntidadPropuesta(
                "PEDIDO",
                ("id_pedido",),
                (),
                (),
                ("id_pedido",),
            ),
            EntidadPropuesta(
                "DETALLE_PEDIDO",
                ("id_pedido", "id_producto"),
                (
                    ("id_pedido", "PEDIDO", "id_pedido"),
                    ("id_producto", "PRODUCTO", "id_producto"),
                ),
                (),
                ("id_pedido", "id_producto", "cantidad"),
            ),
        ),
        (
            RelacionPropuesta(
                "DETALLE_PEDIDO",
                "PEDIDO",
                "id_pedido",
                "id_pedido",
            ),
            RelacionPropuesta(
                "DETALLE_PEDIDO",
                "PRODUCTO",
                "id_producto",
                "id_producto",
            ),
        ),
    ),
    "caso_2_3fn": PropuestaCaso(
        (
            EntidadPropuesta(
                "PROGRAMA",
                ("programa",),
                (),
                (),
                ("programa", "valor_semestre"),
            ),
            EntidadPropuesta(
                "ESTUDIANTE",
                ("codigo_estudiante",),
                (("programa", "PROGRAMA", "programa"),),
                (),
                ("codigo_estudiante", "nombres", "programa"),
            ),
        ),
        (
            RelacionPropuesta(
                "ESTUDIANTE",
                "PROGRAMA",
                "programa",
                "programa",
            ),
        ),
    ),
    "caso_3_bcnf": PropuestaCaso(
        (
            EntidadPropuesta(
                "PROFESOR_CURSO",
                ("profesor",),
                (),
                (),
                ("profesor", "curso"),
            ),
            EntidadPropuesta(
                "INSCRIPCION_ALUMNO",
                ("alumno", "profesor"),
                (("profesor", "PROFESOR_CURSO", "profesor"),),
                (),
                ("alumno", "profesor"),
            ),
        ),
        (
            RelacionPropuesta(
                "INSCRIPCION_ALUMNO",
                "PROFESOR_CURSO",
                "profesor",
                "profesor",
            ),
        ),
    ),
    "caso_4_dos_claves": PropuestaCaso(
        (
            EntidadPropuesta(
                "PERSONA",
                ("dni",),
                (),
                ("email",),
                ("dni", "email", "nombre", "ciudad"),
            ),
        ),
        (),
    ),
    "caso_5_bcnf_ok": PropuestaCaso(
        (
            EntidadPropuesta(
                "EMPLEADO",
                ("id_empleado",),
                (),
                (),
                ("id_empleado", "nombre", "ciudad"),
            ),
        ),
        (),
    ),
}

DF_REQUERIDAS = {
    "caso_1_2fn": (
        DF("id_pedido,id_producto", "cantidad"),
        DF("id_producto", "nombre_producto,precio"),
    ),
    "caso_2_3fn": (
        DF("codigo_estudiante", "nombres,programa"),
        DF("programa", "valor_semestre"),
    ),
    "caso_3_bcnf": (
        DF("alumno,curso", "profesor"),
        DF("profesor", "curso"),
    ),
    "caso_4_dos_claves": (
        DF("dni", "email,nombre,ciudad"),
        DF("email", "dni,nombre,ciudad"),
    ),
    "caso_5_bcnf_ok": (DF("id_empleado", "nombre,ciudad"),),
}

# Tabla de laboratorio que contiene cada esquema de origen.
TABLA_ORIGEN_CASO = {
    "caso_1_2fn": "caso_1_pedidos",
    "caso_2_3fn": "caso_2_estudiantes",
    "caso_3_bcnf": "caso_3_asignaciones",
    "caso_4_dos_claves": "caso_4_personas",
    "caso_5_bcnf_ok": "caso_5_empleados",
}


def propuesta_para(
    nombre_caso: str,
    atributos: Iterable[str],
    df: Iterable[DF],
) -> PropuestaCaso:
    """Devuelve la propuesta documentada afectada por las DF actuales."""
    esquema = frozenset(atributos)
    dependencias = tuple(df)
    propuesta = PROPUESTAS.get(nombre_caso)

    if propuesta is not None:
        esperados = frozenset(
            atributo
            for entidad in propuesta.entidades
            for atributo in entidad.atributos
        )
        faltantes = esperados - esquema
        adicionales = esquema - esperados
        if faltantes or adicionales:
            raise ValueError(
                f"El esquema no corresponde a {nombre_caso}. "
                f"Faltan: {', '.join(sorted(faltantes)) or 'ninguno'}; "
                f"sobran: {', '.join(sorted(adicionales)) or 'ninguno'}."
            )
        no_satisfechas = tuple(
            dependencia for dependencia in DF_REQUERIDAS[nombre_caso]
            if not implica(dependencias, dependencia.lado_izquierdo,
                           dependencia.lado_derecho)
        )
        if no_satisfechas:
            raise ValueError(
                f"Las DF actuales no justifican la propuesta de {nombre_caso}. "
                "Revise las dependencias requeridas del caso."
            )
        entidades = tuple(
            EntidadPropuesta(
                entidad.nombre,
                tuple(pk for pk in entidad.pk if pk in esquema),
                tuple(fk for fk in entidad.fk if fk[0] in esquema),
                tuple(ak for ak in entidad.ak if ak in esquema),
                tuple(
                    atributo
                    for atributo in entidad.atributos
                    if atributo in esquema
                ),
            )
            for entidad in propuesta.entidades
            if any(atributo in esquema for atributo in entidad.atributos)
        )
        relaciones = tuple(
            relacion
            for relacion in propuesta.relaciones
            if any(entidad.nombre == relacion.origen for entidad in entidades)
            and any(entidad.nombre == relacion.destino for entidad in entidades)
        )
        if entidades:
            return PropuestaCaso(entidades, relaciones)

    raise ValueError(f"No hay propuesta válida para el caso {nombre_caso!r}.")
