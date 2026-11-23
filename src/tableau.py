"""Tableau/chase para verificar descomposición sin pérdida."""

from collections.abc import Iterable, Mapping
from src.cierre import cierre
from src.dependencias import DF


def _nuevo_simbolo(contador: list[int]) -> str:
    contador[0] += 1
    return f"b{contador[0]}"


def construir_tableau(R: Iterable[str],
                     relaciones: Iterable[frozenset[str]]) -> list[dict[str, str]]:
    """Construye el tableau inicial de una descomposición.

    parámetros: R esquema completo y relaciones participantes.
    retorno: lista de filas simbolizadas; '1' distingue atributos originales.
    complejidad: O(|rel|·|R|).
    """
    esquema = frozenset(R)
    contador = [0]
    tableau: list[dict[str, str]] = []
    for indice, relacion in enumerate(relaciones):
        fila: dict[str, str] = {}
        for atributo in sorted(esquema):
            fila[atributo] = (
                f"a_{atributo}"
                if atributo in relacion
                else _nuevo_simbolo(contador)
            )
        tableau.append(fila)
    return tableau


def _unificar_tabla(tableau: list[dict[str, str]],
                    origen: str, destino: str) -> None:
    """Sustituye un símbolo por otro evitando símbolos distinguidos no elegidos.

    parámetros: tableau y símbolos origen/destino.
    retorno: None.
    complejidad: O(|tabla|·|R|).
    """
    reemplazo = destino
    if origen.startswith("a_") and not destino.startswith("a_"):
        reemplazo = origen
    for fila in tableau:
        for atributo, valor in fila.items():
            if valor == origen:
                fila[atributo] = reemplazo


def chase_tableau(R: Iterable[str],
                 relaciones: Iterable[frozenset[str]],
                 F: Iterable[DF] = ()) -> list[dict[str, str]]:
    """Aplica chase con las DF sobre el tableau inicial.

    parámetros: R esquema, relaciones de la descomposición y DF originales.
    retorno: tableau final.
    complejidad: O(k·|F|·|tabla|·|R|), k iteraciones hasta punto fijo.
    """
    esquema = frozenset(R)
    partes = tuple(frozenset(relacion) for relacion in relaciones)
    tableau = construir_tableau(esquema, partes)
    dependencias = tuple(F)
    cambio = True
    for _ in range(1000):
        if not cambio:
            break
        cambio = False
        for df in dependencias:
            grupos: dict[tuple[str, ...], list[dict[str, str]]] = {}
            for fila in tableau:
                clave = tuple(fila[atributo]
                              for atributo in sorted(df.lado_izquierdo))
                grupos.setdefault(clave, []).append(fila)
            for filas in grupos.values():
                if len(filas) < 2:
                    continue
                base = filas[0]
                for fila in filas[1:]:
                    for atributo in sorted(df.lado_derecho):
                        izquierdo = base[atributo]
                        derecho = fila[atributo]
                        if izquierdo != derecho:
                            if izquierdo.startswith("a_") and not derecho.startswith("a_"):
                                _unificar_tabla(tableau, derecho, izquierdo)
                            elif derecho.startswith("a_") and not izquierdo.startswith("a_"):
                                _unificar_tabla(tableau, izquierdo, derecho)
                            else:
                                _unificar_tabla(tableau, derecho, izquierdo)
                            cambio = True
                            base = fila
    return tableau


def verificar_sin_perdida(R: Iterable[str],
                          relaciones: Iterable[frozenset[str]],
                          F: Iterable[DF] = ()) -> dict:
    """Verifica si una descomposición es sin pérdida.

    Definición formal: en el tableau inicial existe una fila formada por
    símbolos distinguidos para todos los atributos.
    parámetros: R esquema, relaciones y DF opcionales.
    retorno: dict con cumple y tableau final.
    complejidad: O(k·|F|·|rel|·|R|).
    """
    esquema = frozenset(R)
    partes = tuple(frozenset(relacion) for relacion in relaciones)
    tableau = chase_tableau(esquema, partes, F)
    fila_completa = next(
        (fila for fila in tableau
         if all(valor.startswith("a_") for valor in fila.values())),
        None,
    )
    cumple = fila_completa is not None
    return {
        "cumple": cumple,
        "tableau": tableau,
        "mensaje": (
            "La descomposición es sin pérdida."
            if cumple
            else "El tableau no contiene una fila formada solo por símbolos distinguidos."
        ),
    }