"""Representación y análisis textual de dependencias funcionales."""

from dataclasses import dataclass
from collections.abc import Iterable, Mapping


@dataclass(frozen=True, slots=True)
class DF:
    """Representa una dependencia funcional X -> Y como conjuntos inmutables.

    Definición formal: X -> Y indica que para toda tupla los valores de los
    atributos de X determinan un único valor para cada atributo de Y.
    parámetros: lado_izquierdo y lado_derecho reciben atributos como cadenas
    o iterables de cadenas.
    retorno: una instancia inmutable cuyo lado derecho y izquierdo son
    frozenset[str].
    complejidad: O(|X| + |Y|) por normalización de los conjuntos.

    Cite: BD1_MER_Normalizacion_Vr20250311.pdf, pág. 18.
    """

    lado_izquierdo: frozenset[str]
    lado_derecho: frozenset[str]

    def __init__(self, lado_izquierdo: Iterable[str] | str,
                 lado_derecho: Iterable[str] | str) -> None:
        izquierdo = _normalizar_atributos(lado_izquierdo)
        derecho = _normalizar_atributos(lado_derecho)
        if not izquierdo:
            raise ValueError("El lado izquierdo de una DF no puede estar vacío.")
        if not derecho:
            raise ValueError("El lado derecho de una DF no puede estar vacío.")
        object.__setattr__(self, "lado_izquierdo", izquierdo)
        object.__setattr__(self, "lado_derecho", derecho)

    @property
    def izquierdo(self) -> frozenset[str]:
        """Alias breve compatible con la representación base del proyecto."""
        return self.lado_izquierdo

    @property
    def derecho(self) -> frozenset[str]:
        """Alias breve compatible con la representación base del proyecto."""
        return self.lado_derecho

    def es_trivial(self) -> bool:
        """Indica si Y está contenido en X, es decir, si X -> Y es trivial.

        parámetros: ninguno.
        retorno: True cuando lado_derecho ⊆ lado_izquierdo.
        complejidad: O(|Y|).
        """
        return self.lado_derecho.issubset(self.lado_izquierdo)

    def __str__(self) -> str:
        """Devuelve la DF en una forma legible usando el formato del proyecto."""
        izquierdo = ", ".join(sorted(self.lado_izquierdo))
        derecho = ", ".join(sorted(self.lado_derecho))
        return f"{izquierdo} -> {derecho}"


def _normalizar_atributos(valor: Iterable[str] | str) -> frozenset[str]:
    """Normaliza nombres de atributos, separando una cadena por comas.

    parámetros: una cadena o iterable de cadenas.
    retorno: frozenset[str] sin espacios alrededor y sin nombres vacíos.
    complejidad: O(n), donde n es la cantidad de nombres recibidos.
    """
    if isinstance(valor, str):
        partes = valor.split(",")
    else:
        partes = list(valor)
    nombres = frozenset(parte.strip() for parte in partes
                        if isinstance(parte, str) and parte.strip())
    return nombres


def validar_atributos(atributos: Iterable[str],
                      esquema: Iterable[str]) -> frozenset[str]:
    """Valida que los atributos pertenecen al esquema.

    parámetros: atributos por validar y conjunto de atributos del esquema.
    retorno: frozenset de atributos validados.
    complejidad: O(n), donde n es la cantidad de atributos recibidos.
    """
    esquema_set = frozenset(esquema)
    atributos_set = _normalizar_atributos(atributos)
    desconocidos = atributos_set - esquema_set
    if desconocidos:
        nombres = ", ".join(sorted(desconocidos))
        raise ValueError(f"Atributos inexistentes en el esquema: {nombres}")
    return atributos_set


def parsear_df(texto: str, esquema: Iterable[str]) -> DF:
    """Parsea una dependencia con la sintaxis \"A, B -> C, D\".

    parámetros: texto de la DF y conjunto de atributos válidos.
    retorno: una DF validada e inmutable.
    complejidad: O(n + m), donde n es la longitud del texto y m el esquema.
    """
    if "->" not in texto:
        raise ValueError("Se esperaba una dependencia con el formato 'A, B -> C, D'.")
    partes = texto.split("->")
    if len(partes) != 2:
        raise ValueError("Una dependencia solo puede contener una flecha '->'.")
    izquierdo = validar_atributos(_normalizar_atributos(partes[0]), esquema)
    derecho = validar_atributos(_normalizar_atributos(partes[1]), esquema)
    if not izquierdo or not derecho:
        raise ValueError("Ambos lados de la dependencia deben contener atributos.")
    return DF(izquierdo, derecho)


def parsear_dependencias(texto: str,
                         esquema: Iterable[str]) -> tuple[DF, ...]:
    """Parsea varias DF separadas por líneas o punto y coma.

    parámetros: texto con una DF por línea o separado por punto y coma.
    retorno: tupla de DF validadas.
    complejidad: O(n·m), donde n es el número de DF y m el tamaño del esquema.
    """
    texto = texto.replace("\n", ";")
    candidatos = [parte.strip() for parte in texto.split(";") if parte.strip()]
    if not candidatos:
        return ()
    return tuple(parsear_df(candidato, esquema) for candidato in candidatos)