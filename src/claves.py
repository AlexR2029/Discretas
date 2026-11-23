"""Cálculo de claves candidatas y atributos primos."""

from itertools import combinations
from collections.abc import Iterable
from src.cierre import cierre
from src.dependencias import DF


def claves_candidatas(R: Iterable[str], F: Iterable[DF]) -> tuple[frozenset[str], ...]:
    """Calcula todas las claves candidatas minimales.

    Definición formal: K es clave candidata si cierre(K,F)=R y ningún
    subconjunto propio K' cumple cierre(K',F)=R.
    parámetros: R es el esquema y F la colección de DF.
    retorno: tupla ordenada de claves candidatas.
    complejidad: O(2^n · |F| · |R| · k) en el peor caso, n=|R|;
    los atributos esenciales reducen el espacio de búsqueda.
    """
    esquema = frozenset(R)
    dependencias = tuple(F)
    if not esquema:
        return (frozenset(),)

    esenciales: set[str] = set()
    for atributo in esquema:
        resto = esquema - frozenset({atributo})
        if atributo not in cierre(resto, dependencias):
            esenciales.add(atributo)

    if cierre(esenciales, dependencias) == esquema:
        candidatos_superiores = (frozenset(esenciales),)
    else:
        candidatos_superiores = tuple(
            frozenset(esenciales) | frozenset(combinacion)
            for tamanio in range(len(esenciales), len(esquema) + 1)
            for combinacion in combinations(sorted(esquema - esenciales), tamanio - len(esenciales))
        )

    claves: list[frozenset[str]] = []
    for candidato in candidatos_superiores:
        if cierre(candidato, dependencias) != esquema:
            continue
        if any(clave < candidato for clave in claves):
            continue
        if not any(otro < candidato for otro in candidatos_superiores
                   if cierre(otro, dependencias) == esquema):
            claves.append(candidato)
    claves.sort(key=lambda clave: (len(clave), sorted(clave)))
    return tuple(claves)


def claves_candidatas_declaradas(
    R: Iterable[str],
    F: Iterable[DF],
    pk: Iterable[str] = (),
    aks: Iterable[Iterable[str]] = (),
) -> tuple[frozenset[str], ...]:
    """Filtra claves candidatas por PK y AK declaradas.

    Definición formal: una clave candidata declarada es una PK o AK que
    determina todo R bajo F y no contiene otra PK/AK candidata propia.
    Una FK no forma clave candidata solo por ser FK.
    parámetros: R esquema, F DF, pk PK declarada y aks claves alternativas.
    retorno: tupla de claves candidatas válidas.
    complejidad: O(k·|F|·|R|·n), k número de PK/AK declaradas.
    """
    esquema = frozenset(R)
    dependencias = tuple(F)
    candidatos = []
    pk_set = frozenset(pk)
    if pk_set:
        candidatos.append(pk_set)
    for ak in aks:
        ak_set = frozenset(ak)
        if ak_set:
            candidatos.append(ak_set)

    validas: list[frozenset[str]] = []
    for candidato in dict.fromkeys(candidatos):
        if not candidato.issubset(esquema):
            continue
        if cierre(candidato, dependencias) != esquema:
            continue
        if any(
            otra < candidato
            and otra.issubset(esquema)
            and cierre(otra, dependencias) == esquema
            for otra in candidatos
        ):
            continue
        validas.append(candidato)
    validas.sort(key=lambda clave: (len(clave), sorted(clave)))
    return tuple(validas)


def atributos_primos(R: Iterable[str], F: Iterable[DF]) -> frozenset[str]:
    """Obtiene los atributos que pertenecen al menos a una clave candidata.

    parámetros: R es el esquema y F las DF.
    retorno: unión de todas las claves candidatas.
    complejidad: O(k·n + costo de claves_candidatas), k=|claves|.
    """
    esquema = frozenset(R)
    claves = claves_candidatas(esquema, F)
    primos: set[str] = set()
    for clave in claves:
        primos.update(clave)
    return frozenset(primos)