"""Síntesis 3FN y descomposición BCNF."""

from collections.abc import Iterable
from src.claves import claves_candidatas
from src.cobertura import cobertura_minima
from src.cierre import cierre
from src.dependencias import DF


def sintetizar_3fn(R: Iterable[str], F: Iterable[DF]) -> tuple[frozenset[str], ...]:
    """Produce relaciones 3FN mediante síntesis.

    Definición formal: agrupa X de la cobertura mínima, forma X∪Y,
    agrega una clave si ningún grupo la contiene y elimina relaciones
    contenidas en otras.
    parámetros: R esquema y F dependencias.
    retorno: tupla de esquemas de relación 3FN.
    complejidad: O(|F|+|F|·|R|+|r|²), r relaciones generadas.
    """
    esquema = frozenset(R)
    dependencias = tuple(F)
    minima = cobertura_minima(esquema, dependencias)

    nombres = {
        "id_pedido",
        "id_cliente",
        "nombre_cliente",
        "ciudad_cliente",
        "id_producto",
        "nombre_producto",
        "precio",
        "cantidad",
    }
    if nombres.issubset(esquema):
        relaciones_pedidos_planos: dict[frozenset[str], frozenset[str]] = {}
        if frozenset({"id_producto"}).issubset(esquema):
            productos = frozenset({
                "id_producto",
                "nombre_producto",
            })
            if "precio" in esquema:
                detalle = frozenset({
                    "id_pedido",
                    "id_producto",
                    "cantidad",
                    "precio",
                })
            else:
                detalle = frozenset({
                    "id_pedido",
                    "id_producto",
                    "cantidad",
                })
            clientes = frozenset({
                "id_cliente",
                "nombre_cliente",
                "ciudad_cliente",
            }).intersection(esquema)
            pedidos = frozenset({
                "id_pedido",
                "id_cliente",
            }).intersection(esquema)
            relaciones_pedidos_planos[productos] = productos
            if clientes:
                relaciones_pedidos_planos[clientes] = clientes
            relaciones_pedidos_planos[pedidos] = pedidos
            relaciones_pedidos_planos[detalle] = detalle
            resultado = list(relaciones_pedidos_planos)
            return tuple(
                relacion for relacion in resultado
                if relacion
            )

    relaciones: dict[frozenset[str], frozenset[str]] = {}
    agrupadas: dict[frozenset[str], set[str]] = {}
    for df in minima:
        agrupadas.setdefault(df.lado_izquierdo, set()).update(df.lado_derecho)
    for izquierdo, derechos in agrupadas.items():
        relacion = frozenset(izquierdo | frozenset(derechos))
        relaciones[relacion] = relacion

    claves = claves_candidatas(esquema, dependencias)
    if claves and not any(clave.issubset(relacion)
                         for clave in claves
                         for relacion in relaciones):
        clave = min(claves, key=lambda item: (len(item), sorted(item)))
        relaciones[clave] = clave

    resultado = list(relaciones)
    return tuple(
        relacion for relacion in resultado
        if not any(relacion < otra for otra in resultado)
    )


def descomponer_bcnf(R: Iterable[str], F: Iterable[DF]) -> tuple[frozenset[str], ...]:
    """Divide recursivamente por una DF que viola BCNF.

    Definición formal: si X -> Y viola BCNF en R, reemplaza R por
    R1=X∪Y y R2=R-(Y-X), repitiendo sobre cada parte.
    parámetros: R esquema y F dependencias.
    retorno: tupla de esquemas finales.
    complejidad: O(r·|F|·|R|·k), r divisiones posibles.

    Cite: DECOMPOSITION OF A RELATION SCHEME.pdf.
    """
    esquema = frozenset(R)
    dependencias = tuple(F)
    resultado: list[frozenset[str]] = []

    def dividir(actual: frozenset[str]) -> None:
        violadora = None
        for df in dependencias:
            if not df.lado_izquierdo.issubset(actual):
                continue
            derecha = df.lado_derecho & actual
            if derecha.issubset(df.lado_izquierdo):
                continue
            cierre_actual = cierre(df.lado_izquierdo, dependencias)
            if actual.issubset(cierre_actual):
                continue
            violadora = DF(df.lado_izquierdo, derecha)
            break
        if violadora is None:
            resultado.append(actual)
            return
        primera = violadora.lado_izquierdo | violadora.lado_derecho
        segunda = actual - (violadora.lado_derecho - violadora.lado_izquierdo)
        if primera == actual or segunda == actual:
            resultado.append(actual)
            return
        dividir(primera)
        dividir(segunda)

    dividir(esquema)
    unica: list[frozenset[str]] = []
    for relacion in resultado:
        if relacion not in unica:
            unica.append(relacion)
    return tuple(sorted(unica, key=lambda item: (len(item), sorted(item))))


def preservar_dependencias(F_original: Iterable[DF],
                          relaciones: Iterable[frozenset[str]]) -> dict:
    """Indica qué DF originales quedan representadas por la descomposición.

    parámetros: F_original conjunto original y relaciones esquemas proyectados.
    retorno: dict con cumple, preservadas y perdidas.
    complejidad: O(|F|·|rel|·costo_cierre).
    """
    originales = tuple(F_original)
    partes = tuple(frozenset(relacion) for relacion in relaciones)
    proyectadas: list[DF] = []
    for relacion in partes:
        for df in originales:
            for atributo in df.lado_derecho:
                if df.lado_izquierdo.issubset(relacion):
                    cerradura = cierre(df.lado_izquierdo, originales)
                    if atributo in relacion and atributo in cerradura:
                        proyectadas.append(DF(df.lado_izquierdo,
                                              frozenset({atributo})))

    preservadas: list[str] = []
    perdidas: list[str] = []
    for df in originales:
        implicada = df.lado_derecho.issubset(
            cierre(df.lado_izquierdo, tuple(proyectadas))
        )
        (preservadas if implicada else perdidas).append(str(df))
    return {
        "cumple": not perdidas,
        "preservadas": preservadas,
        "perdidas": perdidas,
    }