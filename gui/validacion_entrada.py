"""Validación amable de sintaxis en los campos de entrada de la interfaz."""

import re


_IDENTIFICADOR = re.compile(r"[A-Za-z_][A-Za-z0-9_$]*")
_FLECHA = re.compile(r"->")


def validar_dependencias(texto: str, esquema) -> None:
    """Valida sintaxis y ubicación de errores antes de invocar el analizador."""
    texto = _normalizar_saltos(texto)
    if not texto.strip():
        return
    _validar_puntuacion_global(texto)
    _validar_separadores_df(texto)
    atributos_validos = frozenset(esquema)
    for segmento in re.finditer(r"[^;\n]+", texto):
        contenido = segmento.group()
        if contenido.strip():
            _validar_dependencia(
                contenido, segmento.start(), texto, atributos_validos
            )


def validar_consulta_cierre(texto: str, esquema) -> None:
    """Valida X o X -> Y del campo de cierre e implicación."""
    texto = _normalizar_saltos(texto)
    if not texto.strip():
        return
    _validar_puntuacion_global(texto)
    if ";" in texto:
        posicion = texto.index(";")
        raise _error(
            texto, posicion,
            "El punto y coma separa dependencias en el campo DF; aquí escribe "
            "solo atributos separados por comas.",
        )
    if "\n" in texto:
        posicion = texto.index("\n")
        raise _error(texto, posicion, "Escribe la consulta X en una sola línea.")

    flechas = tuple(_FLECHA.finditer(texto))
    if len(flechas) > 1:
        raise _error_flecha(
            texto, flechas[1].start(),
            "Solo se permite una flecha en la consulta X -> Y.",
        )
    if not flechas:
        _validar_flecha_mal_escrita(texto, 0, texto)
        izquierda = texto
        base_izquierda = 0
        derecha = None
    else:
        flecha = flechas[0]
        _comprobar_flecha_exacta(texto, flecha.start(), flecha.end())
        izquierda = texto[:flecha.start()]
        derecha = texto[flecha.end():]
        base_izquierda = 0
    _validar_lista_atributos(
        izquierda, base_izquierda, texto, frozenset(esquema), "X"
    )
    if derecha is not None:
        _validar_lista_atributos(
            derecha, flecha.end(), texto, frozenset(esquema), "Y"
        )


def _normalizar_saltos(texto: str) -> str:
    return texto.replace("\r\n", "\n").replace("\r", "\n")


def _validar_puntuacion_global(texto: str) -> None:
    for posicion, caracter in enumerate(texto):
        if caracter in ".:":
            descripcion = (
                "El punto no es válido en un nombre de atributo."
                if caracter == "."
                else "Los dos puntos no se usan en una dependencia funcional."
            )
            raise _error(texto, posicion, descripcion)


def _validar_separadores_df(texto: str) -> None:
    for posicion, caracter in enumerate(texto):
        if caracter != ";":
            continue
        anterior = posicion - 1
        while anterior >= 0 and texto[anterior].isspace():
            anterior -= 1
        siguiente = posicion + 1
        while siguiente < len(texto) and texto[siguiente].isspace():
            siguiente += 1
        if anterior < 0 or (anterior >= 0 and texto[anterior] == ";"):
            raise _error(
                texto, posicion,
                "Este punto y coma no tiene una dependencia antes. "
                "Escribe una DF antes de separar la siguiente.",
            )


def _validar_dependencia(
    segmento: str,
    inicio: int,
    texto_completo: str,
    esquema: frozenset[str],
) -> None:
    desplazamiento = len(segmento) - len(segmento.lstrip())
    cuerpo = segmento.strip()
    base = inicio + desplazamiento
    flechas = tuple(_FLECHA.finditer(cuerpo))
    if len(flechas) > 1:
        raise _error_flecha(
            texto_completo, base + flechas[1].start(),
            "Cada dependencia lleva una sola flecha. "
            "Separa dependencias distintas con punto y coma.",
        )
    if not flechas:
        _validar_flecha_mal_escrita(cuerpo, base, texto_completo)
        posicion = base + len(cuerpo)
        raise _error_flecha(
            texto_completo, posicion,
            "Falta la flecha entre los dos lados. Formato: atributo -> atributo.",
        )
    flecha = flechas[0]
    _comprobar_flecha_exacta(
        texto_completo, base + flecha.start(), base + flecha.end()
    )
    _validar_lista_atributos(
        cuerpo[:flecha.start()], base, texto_completo, esquema, "lado izquierdo"
    )
    _validar_lista_atributos(
        cuerpo[flecha.end():], base + flecha.end(),
        texto_completo, esquema, "lado derecho"
    )


def _validar_flecha_mal_escrita(
    fragmento: str,
    inicio: int,
    texto_completo: str,
) -> None:
    candidatos = list(re.finditer(r"=>|<-|-\s+>|>\s*-|[-<>]|=", fragmento))
    if candidatos:
        token = candidatos[0]
        absoluto = inicio + token.start()
        raise _error_flecha(
            texto_completo, absoluto,
            "La flecha está mal escrita. Usa guion y luego mayor que, juntos: "
            "A, B -> C.",
        )


def _comprobar_flecha_exacta(texto: str, inicio: int, fin: int) -> None:
    if inicio > 0 and texto[inicio - 1] in "-<=>":
        raise _error_flecha(
            texto, inicio - 1,
            "Hay un carácter extra antes de la flecha. Escríbela como ->.",
        )
    if fin < len(texto) and texto[fin] in "-<=>":
        raise _error_flecha(
            texto, fin,
            "Hay un carácter extra después de la flecha. Escríbela como ->.",
        )


def _validar_lista_atributos(
    lista: str,
    inicio: int,
    texto_completo: str,
    esquema: frozenset[str],
    lado: str,
) -> None:
    desplazamiento = len(lista) - len(lista.lstrip())
    contenido = lista.strip()
    base = inicio + desplazamiento
    if not contenido:
        raise _error(
            texto_completo, min(inicio, len(texto_completo)),
            f"Falta un atributo en el {lado}. Escribe un nombre antes y después de la flecha.",
        )

    cursor = 0
    partes = contenido.split(",")
    for indice, parte in enumerate(partes):
        inicio_parte = cursor
        cursor += len(parte) + 1
        nombre = parte.strip()
        if not nombre:
            posicion = (
                base + inicio_parte + len(parte)
                if indice < len(partes) - 1
                else base + inicio_parte - 1
            )
            raise _error(
                texto_completo, posicion,
                f"Hay una coma sin atributo en el {lado}. "
                "Escribe un nombre a cada lado de la coma.",
            )
        espacios = re.search(r"\s", nombre)
        if espacios:
            posicion = base + inicio_parte + len(parte) - len(parte.lstrip())
            posicion += espacios.start()
            raise _error(
                texto_completo, posicion,
                f"El nombre de atributo {nombre!r} contiene un espacio. "
                "Separa atributos con coma.",
            )
        if not _IDENTIFICADOR.fullmatch(nombre):
            inicio_nombre = base + inicio_parte + len(parte) - len(parte.lstrip())
            invalido = _primer_caracter_invalido(nombre)
            posicion = inicio_nombre + invalido
            raise _error(
                texto_completo, posicion,
                f"El nombre {nombre!r} no es válido. Usa letras, números, "
                "guion bajo o dólar; comienza con letra o guion bajo.",
            )
        if nombre not in esquema:
            inicio_nombre = base + inicio_parte + len(parte) - len(parte.lstrip())
            raise _error(
                texto_completo, inicio_nombre,
                f"No existe el atributo {nombre!r} en la tabla seleccionada. "
                "Revisa cómo aparece escrito en el esquema.",
            )


def _primer_caracter_invalido(nombre: str) -> int:
    for indice, caracter in enumerate(nombre):
        permitido = (
            caracter.isascii() and caracter.isalpha() or caracter == "_"
            if indice == 0
            else caracter.isascii() and (caracter.isalnum() or caracter in "_$")
        )
        if not permitido:
            return indice
    return 0


def _error(texto: str, posicion: int, explicacion: str) -> ValueError:
    posicion = max(0, min(posicion, len(texto)))
    linea = texto.count("\n", 0, posicion) + 1
    inicio_linea = texto.rfind("\n", 0, posicion) + 1
    columna = posicion - inicio_linea + 1
    caracter = texto[posicion] if posicion < len(texto) else "fin de entrada"
    return ValueError(
        f"{explicacion}\nUbicación: línea {linea}, columna {columna} "
        f"(carácter {caracter!r})."
    )


def _error_flecha(texto: str, posicion: int, explicacion: str) -> ValueError:
    return _error(texto, posicion, explicacion)
