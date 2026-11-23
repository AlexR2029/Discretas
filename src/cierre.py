"""Cálculo del cierre de atributos y funciones relacionadas."""

from collections.abc import Iterable
from src.dependencias import DF


def cierre(X: Iterable[str] | str, F: Iterable[DF]) -> frozenset[str]:
    """Calcula X+ por punto fijo usando las reglas de Armstrong.

    Definición formal: X+ = {A | F implica X -> A}. Se aplica axioma
    reflexivo y axioma transitivo mediante inclusión iterativa.
    parámetros: X es el conjunto inicial y F es la colección de DF.
    retorno: frozenset con todos los atributos implicados por X.
    complejidad: O(|F|·|R|·k), con k iteraciones hasta alcanzar el punto fijo.
    """
    if isinstance(X, str):
        resultado = frozenset(part.strip() for part in X.split(",")
                              if part.strip())
    else:
        resultado = frozenset(X)

    dependencias = tuple(F)
    cambiado = True
    while cambiado:
        cambiado = False
        for df in dependencias:
            if df.lado_izquierdo.issubset(resultado):
                agregado = resultado | df.lado_derecho
                if agregado != resultado:
                    resultado = agregado
                    cambiado = True
    return resultado


def implica(F: Iterable[DF], X: Iterable[str] | str,
            Y: Iterable[str] | str) -> bool:
    """Decide si F implica X -> Y.

    parámetros: F contiene las DF conocidas, X es el lado izquierdo y Y el
    lado derecho que se desea verificar.
    retorno: True cuando Y está incluido en cierre(X,F).
    complejidad: O(|F|·|R|·k), con k iteraciones hasta el punto fijo.
    """
    if isinstance(Y, str):
        objetivo = frozenset(part.strip() for part in Y.split(",")
                             if part.strip())
    else:
        objetivo = frozenset(Y)
    return objetivo.issubset(cierre(X, tuple(F)))


def es_superclave(X: Iterable[str] | str, R: Iterable[str],
                  F: Iterable[DF]) -> bool:
    """Determina si X es una superclave del esquema R bajo F.

    parámetros: X es el candidato, R contiene todos los atributos y F las DF.
    retorno: True cuando el cierre de X contiene a R.
    complejidad: O(|F|·|R|·k).
    """
    esquema = frozenset(R)
    return esquema.issubset(cierre(X, tuple(F)))