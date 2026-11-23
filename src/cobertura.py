"""Cobertura mínima y gestión de dependencias funcionales."""

import json
from collections.abc import Iterable
from pathlib import Path
from src.cierre import cierre
from src.dependencias import DF


def lado_derecho_unitario(F: Iterable[DF]) -> tuple[DF, ...]:
    """Descompone los lados derechos de las DF en atributos unitarios.

    Definición formal: cada X -> Y se reemplaza por X -> A para todo
    A perteneciente a Y.
    parámetros: F colección de dependencias.
    retorno: tupla de DF con lado derecho unitario.
    complejidad: O(sum(|Y|)).
    """
    resultado: list[DF] = []
    for df in tuple(F):
        if df.es_trivial():
            resultado.append(df)
        else:
            for atributo in sorted(df.lado_derecho):
                resultado.append(DF(df.lado_izquierdo, frozenset({atributo})))
    return tuple(resultado)


def eliminar_atributos_extranos(R: Iterable[str],
                                F: Iterable[DF]) -> tuple[DF, ...]:
    """Elimina atributos redundantes de los lados izquierdos.

    Definición formal: A es extraño en X -> Y si
    (F - {X -> Y}) implica (X - {A}) -> Y.
    parámetros: R esquema y F conjunto de dependencias.
    retorno: tupla de DF minimizadas por lados izquierdos.
    complejidad: O(|F|·|R|·costo_cierre).
    """
    esquema = frozenset(R)
    actuales = list(dict.fromkeys(lado_derecho_unitario(F)))
    for indice, df in enumerate(list(actuales)):
        resto = tuple(actual for actual in actuales if actual is not df)
        candidatos = sorted(df.lado_izquierdo)
        izquierdo = df.lado_izquierdo
        for atributo in candidatos:
            prueba = izquierdo - frozenset({atributo})
            if not prueba:
                continue
            cierre_prueba = cierre(prueba, resto)
            if df.lado_derecho.issubset(cierre_prueba):
                izquierdo = prueba
        actuales[indice] = DF(izquierdo, df.lado_derecho)
    return tuple(actuales)


def eliminar_dependencias_redundantes(R: Iterable[str],
                                      F: Iterable[DF]) -> tuple[DF, ...]:
    """Elimina DF implicadas por las restantes.

    Definición formal: X -> Y es redundante si Y está en el cierre de X
    calculado sin esa DF.
    parámetros: R esquema reservado para validar el alcance y F dependencias.
    retorno: tupla de DF irredundantes.
    complejidad: O(|F|·costo_cierre).
    """
    frozenset(R)
    actuales = list(dict.fromkeys(F))
    resultado: list[DF] = []
    for df in actuales:
        resto = tuple(actual for actual in actuales if actual is not df)
        if df.lado_derecho.issubset(cierre(df.lado_izquierdo, resto)):
            continue
        resultado.append(df)
    return tuple(resultado)


def cobertura_minima(R: Iterable[str], F: Iterable[DF]) -> tuple[DF, ...]:
    """Calcula una cobertura mínima equivalente a F.

    parámetros: R esquema y F conjunto de DF.
    retorno: tupla de DF unitarias, mínimas por lado izquierdo y redundancia.
    complejidad: polinomio sobre la representación iterativa usada por cierre.
    """
    unidad = lado_derecho_unitario(F)
    extraños = eliminar_atributos_extranos(R, unidad)
    return eliminar_dependencias_redundantes(R, extraños)


def agregar_df(F: Iterable[DF], df: DF) -> tuple[DF, ...]:
    """Agrega una DF si todavía no está representada."""
    actuales = tuple(F)
    return actuales if df in actuales else actuales + (df,)


def editar_df(F: Iterable[DF], indice: int, df: DF) -> tuple[DF, ...]:
    """Reemplaza una DF por índice."""
    actuales = list(F)
    if indice < 0 or indice >= len(actuales):
        raise IndexError("El índice de la dependencia no existe.")
    actuales[indice] = df
    return tuple(actuales)


def eliminar_df(F: Iterable[DF], indice: int) -> tuple[DF, ...]:
    """Elimina una DF por índice."""
    actuales = list(F)
    if indice < 0 or indice >= len(actuales):
        raise IndexError("El índice de la dependencia no existe.")
    actuales.pop(indice)
    return tuple(actuales)


def guardar_dependencias(ruta: str | Path, F: Iterable[DF]) -> None:
    """Guarda DF en JSON como pares de listas de atributos.

    parámetros: ruta destino y colección de DF.
    retorno: None.
    complejidad: O(sum(|X|+|Y|)).
    """
    destino = Path(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    datos = [
        {
            "izquierdo": sorted(df.lado_izquierdo),
            "derecho": sorted(df.lado_derecho),
        }
        for df in F
    ]
    destino.write_text(json.dumps(datos, ensure_ascii=False, indent=2),
                       encoding="utf-8")


def cargar_dependencias(ruta: str | Path) -> tuple[DF, ...]:
    """Carga DF desde el formato JSON creado por guardar_dependencias.

    parámetros: ruta del archivo.
    retorno: tupla de DF.
    complejidad: O(n), n entradas del JSON.
    """
    origen = Path(ruta)
    datos = json.loads(origen.read_text(encoding="utf-8"))
    if not isinstance(datos, list):
        raise ValueError("El archivo de dependencias debe contener una lista.")
    return tuple(
        DF(frozenset(item["izquierdo"]), frozenset(item["derecho"]))
        for item in datos
    )