"""Verificadores de formas normales del diseño relacional."""

from collections.abc import Iterable, Mapping
from itertools import combinations
from src.cierre import es_superclave
from src.claves import atributos_primos, claves_candidatas
from src.dependencias import DF


_TIPOS_COMPUESTOS = {
    "json", "array", "set", "struct", "list", "map", "multivalorado",
    "compuesto",
}


def _candidatas(R: Iterable[str], F: Iterable[DF],
                claves: Iterable[frozenset[str]] | None) -> tuple[frozenset[str], ...]:
    """Obtiene las claves candidatas declaradas o las calculadas."""
    esquema = frozenset(R)
    dependencias = tuple(F)
    if claves is not None:
        candidatas = tuple(
            frozenset(clave) for clave in claves
            if frozenset(clave).issubset(esquema)
        )
        return candidatas if candidatas else claves_candidatas(esquema, dependencias)
    return claves_candidatas(esquema, dependencias)


def _dependencias_derivadas(R: Iterable[str],
                            F: Iterable[DF]) -> tuple[DF, ...]:
    """Deriva todas las DF simples X -> A presentes en F+."""
    esquema = frozenset(R)
    dependencias = tuple(F)
    derivadas: dict[tuple[frozenset[str], frozenset[str]], DF] = {}
    atributos = sorted(esquema)
    for tamanio in range(len(atributos) + 1):
        for seleccion in combinations(atributos, tamanio):
            izquierdo = frozenset(seleccion)
            cerrado = _cierre_normalizacion(izquierdo, dependencias)
            for atributo in cerrado - izquierdo:
                df = DF(izquierdo, frozenset({atributo}))
                derivadas[(izquierdo, frozenset({atributo}))] = df
    return tuple(derivadas.values())


def _cierre_normalizacion(X: frozenset[str],
                          F: Iterable[DF]) -> frozenset[str]:
    """Calcula cierre para uso interno sin depender de otra interfaz."""
    resultado = frozenset(X)
    dependencias = tuple(F)
    while True:
        siguiente = resultado
        for df in dependencias:
            if df.lado_izquierdo.issubset(siguiente):
                siguiente = siguiente | df.lado_derecho
        if siguiente == resultado:
            return resultado
        resultado = siguiente


def es_1fn(R: Iterable[str],
           tipos: Mapping[str, str] | Iterable[str] | None = None,
           atomicos: Mapping[str, bool] | Iterable[str] | None = None,
           **opciones) -> dict:
    """Verifica atomicidad de los atributos para determinar 1FN.

    Definición formal: R está en 1FN si todos sus atributos tienen valores
    indivisibles y no existen grupos o atributos repetitivos.
    parámetros: R contiene el esquema; tipos mapea atributo->tipo SQL o
    indica el conjunto de atributos con tipo no compuesto; atomicos puede
    ser un mapeo atributo->booleano o el conjunto de atributos atómicos.
    retorno: dict con cumple, violaciones y mensaje.
    complejidad: O(|R|).

    Cite: BD1_MER_Normalizacion_Vr20250311.pdf, pág. 8.
    """
    esquema = frozenset(R)
    no_atomicos: set[str] = set()

    if atomicos is not None:
        if isinstance(atomicos, Mapping):
            no_atomicos.update(nombre for nombre, es_atomico in atomicos.items()
                               if nombre in esquema and not es_atomico)
        else:
            conjunto_atomicos = frozenset(atomicos)
            no_atomicos.update(esquema - conjunto_atomicos)

    if tipos is not None:
        if isinstance(tipos, Mapping):
            for nombre, tipo in tipos.items():
                if nombre not in esquema:
                    continue
                tipo_base = str(tipo).split("(", 1)[0].strip().lower()
                if tipo_base in _TIPOS_COMPUESTOS:
                    no_atomicos.add(nombre)
        else:
            conjunto_tipos_atomicos = frozenset(tipos)
            no_atomicos.update(esquema - conjunto_tipos_atomicos)

    if opciones:
        indicadores = opciones.get("indicadores")
        if isinstance(indicadores, Mapping):
            no_atomicos.update(nombre for nombre, es_atomico in indicadores.items()
                               if nombre in esquema and not es_atomico)
        elif isinstance(indicadores, Iterable):
            indicador_set = frozenset(indicadores)
            no_atomicos.update(esquema - indicador_set)

    violaciones = sorted(no_atomicos)
    cumple = not violaciones
    mensaje = ("El esquema está en 1FN."
               if cumple
               else "Viola 1FN porque existen atributos no atómicos: "
                    + ", ".join(violaciones))
    return {"cumple": cumple, "violaciones": violaciones, "mensaje": mensaje}


def es_2fn(R: Iterable[str], F: Iterable[DF],
           claves: Iterable[frozenset[str]] | None = None) -> dict:
    """Verifica que ningún atributo no primo dependa parcialmente de una clave.

    Definición formal: R está en 2FN si está en 1FN y todo atributo no clave
    depende funcionalmente completa de la clave principal/candidata.
    parámetros: R es el esquema, F las DF y claves permite fijar las candidatas.
    retorno: dict con cumple, violaciones y mensaje.
    complejidad: O(|K|·|F|·|R|·k + |F|·|R|).

    Cite: BD1_MER_Normalizacion_Vr20250311.pdf, págs. 16 y 18.
    """
    esquema = frozenset(R)
    dependencias = tuple(F)
    candidatas = _candidatas(esquema, dependencias, claves)
    primos = frozenset().union(*candidatas) if candidatas else frozenset()
    if not candidatas:
        primos = frozenset()

    violaciones: list[str] = []
    derivadas = _dependencias_derivadas(esquema, dependencias)
    for clave in candidatas:
        if len(clave) <= 1:
            continue
        for df in derivadas:
            if df.es_trivial():
                continue
            izquierdo = df.lado_izquierdo
            if izquierdo < clave:
                atributos_parciales = df.lado_derecho - primos
                for atributo in sorted(atributos_parciales):
                    violaciones.append(
                        f"{atributo} depende parcialmente de {clave} "
                        f"mediante {df}"
                    )

    violaciones = list(dict.fromkeys(violaciones))
    cumple = not violaciones
    mensaje = ("El esquema está en 2FN."
               if cumple
               else "Viola 2FN: " + "; ".join(violaciones))
    return {"cumple": cumple, "violaciones": violaciones, "mensaje": mensaje,
            "claves_candidatas": [sorted(clave) for clave in candidatas]}


def es_3fn(R: Iterable[str], F: Iterable[DF],
           claves: Iterable[frozenset[str]] | None = None) -> dict:
    """Verifica la ausencia de dependencias transitivas sobre atributos no clave.

    Definición formal: toda DF no trivial X -> Y cumple que X es superclave
    o todos los atributos de Y son primos.
    parámetros: R es el esquema, F las DF y claves las candidatas opcionales.
    retorno: dict con cumple, violaciones y mensaje.
    complejidad: O(|F|·|R|·k), con k iteraciones de cierre.

    Cite: BD1_MER_Normalizacion_Vr20250311.pdf, pág. 23.
    """
    esquema = frozenset(R)
    dependencias = tuple(F)
    candidatas = _candidatas(esquema, dependencias, claves)
    primos = frozenset().union(*candidatas) if candidatas else frozenset()

    violaciones: list[str] = []
    for df in _dependencias_derivadas(esquema, dependencias):
        if df.es_trivial():
            continue
        if es_superclave(df.lado_izquierdo, esquema, dependencias):
            continue
        atributos_no_primos = df.lado_derecho - primos
        if atributos_no_primos:
            if any(
                atributo not in primos
                for atributo in df.lado_derecho
            ):
                violaciones.append(
                    f"{df} tiene un determinante que no es superclave "
                    f"y determina atributos no primos: "
                    f"{', '.join(sorted(atributos_no_primos))}"
                )

    violaciones = list(dict.fromkeys(violaciones))
    cumple = not violaciones
    mensaje = ("El esquema está en 3FN."
               if cumple
               else "Viola 3FN: " + "; ".join(violaciones))
    return {"cumple": cumple, "violaciones": violaciones, "mensaje": mensaje,
            "claves_candidatas": [sorted(clave) for clave in candidatas]}


def es_bcnf(R: Iterable[str], F: Iterable[DF],
            claves: Iterable[frozenset[str]] | None = None) -> dict:
    """Verifica que toda DF no trivial tenga como determinante una superclave.

    Definición formal: R está en BCNF si, para toda X -> Y en F+,
    X -> Y es trivial o X es superclave.
    parámetros: R es el esquema y F las DF declaradas.
    retorno: dict con cumple, violaciones y mensaje.
    complejidad: O(|F|·|R|·k).

    Nota: la fuente disponible no desarrolla formalmente BCNF; requiere fuente
    externa para la definición completa.
    """
    esquema = frozenset(R)
    dependencias = tuple(F)
    candidatas = _candidatas(esquema, dependencias, claves)
    violaciones: list[str] = []
    for df in _dependencias_derivadas(esquema, dependencias):
        if df.es_trivial():
            continue
        if not es_superclave(df.lado_izquierdo, esquema, dependencias):
            violaciones.append(
                f"{df} viola BCNF porque {sorted(df.lado_izquierdo)} "
                "no es superclave"
            )

    violaciones = list(dict.fromkeys(violaciones))
    cumple = not violaciones
    mensaje = ("El esquema está en BCNF."
               if cumple
               else "Viola BCNF: " + "; ".join(violaciones))
    return {"cumple": cumple, "violaciones": violaciones, "mensaje": mensaje,
            "claves_candidatas": [
                sorted(clave) for clave in claves_candidatas(esquema, dependencias)
            ]}