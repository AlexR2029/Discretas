"""Pruebas de robustez e ida/vuelta para iniciar la fase 5."""

import unittest

from datos.datos_sinteticos import generar_pedidos_sinteticos
from src.claves import claves_candidatas
from src.dependencias import DF, parsear_dependencias
from src.descomposicion import descomponer_bcnf, sintetizar_3fn
from src.formas_normales import es_1fn, es_2fn, es_3fn, es_bcnf
from src.tableau import verificar_sin_perdida


def proyeccion(filas: tuple[dict, ...], atributos: frozenset[str]) -> list[dict]:
    """Proyecta filas sobre los atributos de una relación."""
    return [
        {atributo: fila[atributo] for atributo in atributos}
        for fila in filas
    ]


def join_natural(relaciones: tuple[list[dict], ...]) -> set[tuple]:
    """Calcula un join natural pequeño sobre filas en memoria."""
    resultado = [{}]
    for relacion in relaciones:
        combinado = []
        for izquierda in resultado:
            for derecha in relacion:
                compartidos = izquierda.keys() & derecha.keys()
                if all(izquierda[atributo] == derecha[atributo]
                       for atributo in compartidos):
                    combinado.append(izquierda | derecha)
        resultado = combinado
    atributos = tuple(sorted(resultado[0])) if resultado else ()
    return {tuple(fila[atributo] for atributo in atributos) for fila in resultado}


def filas_como_conjunto(filas: tuple[dict, ...]) -> set[tuple]:
    atributos = tuple(sorted(filas[0])) if filas else ()
    return {tuple(fila[atributo] for atributo in atributos) for fila in filas}


class PruebasFase5(unittest.TestCase):
    def test_ida_vuelta_pedidos_planos_sin_perdida(self):
        esquema = frozenset({
            "id_pedido", "id_cliente", "nombre_cliente", "ciudad_cliente",
            "id_producto", "nombre_producto", "precio", "cantidad",
        })
        dependencias = (
            DF("id_cliente", "nombre_cliente,ciudad_cliente"),
            DF("id_producto", "nombre_producto,precio"),
            DF("id_pedido", "id_cliente"),
            DF("id_pedido,id_producto", "cantidad"),
        )
        filas = generar_pedidos_sinteticos(semilla=2026)

        relaciones = sintetizar_3fn(esquema, dependencias)
        self.assertEqual(len(relaciones), 4)
        self.assertIn(
            frozenset({"id_producto", "nombre_producto", "precio"}),
            relaciones,
        )
        self.assertIn(
            frozenset({"id_pedido", "id_producto", "cantidad"}),
            relaciones,
        )
        self.assertTrue(verificar_sin_perdida(
            esquema, relaciones, dependencias
        )["cumple"])

        partes = tuple(proyeccion(filas, relacion) for relacion in relaciones)
        reconstruidas = join_natural(partes)
        self.assertEqual(reconstruidas, filas_como_conjunto(filas))

    def test_datos_reproducibles_y_respetan_dependencias(self):
        filas_a = generar_pedidos_sinteticos(semilla=42)
        filas_b = generar_pedidos_sinteticos(semilla=42)
        self.assertEqual(filas_a, filas_b)

        valores_cliente = {}
        valores_producto = {}
        valores_pedido = {}
        for fila in filas_a:
            cliente = (fila["nombre_cliente"], fila["ciudad_cliente"])
            producto = (fila["nombre_producto"], fila["precio"])
            self.assertEqual(valores_cliente.setdefault(fila["id_cliente"], cliente), cliente)
            self.assertEqual(valores_producto.setdefault(fila["id_producto"], producto), producto)
            self.assertEqual(valores_pedido.setdefault(fila["id_pedido"], fila["id_cliente"]), fila["id_cliente"])

    def test_cinco_casos_y_excepcion_de_3fn(self):
        casos = {
            "caso_1_2fn": (
                {"id_pedido", "id_producto", "nombre_producto", "precio", "cantidad"},
                (DF("id_pedido,id_producto", "cantidad"),
                 DF("id_producto", "nombre_producto,precio")),
                {"pk": {"id_pedido", "id_producto"}},
                (True, False, False, False),
            ),
            "caso_2_3fn": (
                {"codigo_estudiante", "nombres", "programa", "valor_semestre"},
                (DF("codigo_estudiante", "nombres,programa"),
                 DF("programa", "valor_semestre")),
                {"pk": {"codigo_estudiante"}},
                (True, True, False, False),
            ),
            "caso_3_bcnf": (
                {"alumno", "curso", "profesor"},
                (DF("alumno,curso", "profesor"), DF("profesor", "curso")),
                {"pk": {"alumno", "curso"}},
                (True, True, True, False),
            ),
            "caso_4_dos_claves": (
                {"dni", "email", "nombre", "ciudad"},
                (DF("dni", "email,nombre,ciudad"),
                 DF("email", "dni,nombre,ciudad")),
                {"pk": {"dni"}, "aks": ({"email"},)},
                (True, True, True, True),
            ),
            "caso_5_bcnf_ok": (
                {"id_empleado", "nombre", "ciudad"},
                (DF("id_empleado", "nombre,ciudad"),),
                {"pk": {"id_empleado"}},
                (True, True, True, True),
            ),
        }
        for nombre, (esquema, df, claves, esperado) in casos.items():
            with self.subTest(caso=nombre):
                clave_sets = (frozenset(claves["pk"]),) + tuple(
                    frozenset(ak) for ak in claves.get("aks", ())
                )
                reales = (
                    es_1fn(esquema, tipos={a: "VARCHAR(100)" for a in esquema})["cumple"],
                    es_2fn(esquema, df, claves=clave_sets)["cumple"],
                    es_3fn(esquema, df, claves=clave_sets)["cumple"],
                    es_bcnf(esquema, df, claves=clave_sets)["cumple"],
                )
                self.assertEqual(reales, esperado)

    def test_caso_3_bcnf_descompone_sin_perdida(self):
        esquema = frozenset({"alumno", "curso", "profesor"})
        dependencias = (
            DF("alumno,curso", "profesor"),
            DF("profesor", "curso"),
        )
        partes = descomponer_bcnf(esquema, dependencias)
        self.assertEqual(
            set(partes),
            {
                frozenset({"profesor", "curso"}),
                frozenset({"alumno", "profesor"}),
            },
        )
        self.assertTrue(verificar_sin_perdida(esquema, partes, dependencias)["cumple"])

    def test_clave_unica_clave_alterna_y_dependencia_trivial(self):
        dependencias = (
            DF("dni", "email,nombre,ciudad"),
            DF("email", "dni,nombre,ciudad"),
            DF("dni", "dni"),
        )
        claves = claves_candidatas(
            {"dni", "email", "nombre", "ciudad"}, dependencias
        )
        self.assertEqual(
            set(claves), {frozenset({"dni"}), frozenset({"email"})}
        )

    def test_rechaza_df_mal_escrita_o_atributo_inexistente(self):
        with self.assertRaises(ValueError):
            parsear_dependencias("A B -> C", {"A", "B", "C"})
        with self.assertRaises(ValueError):
            parsear_dependencias("A -> Z", {"A", "B", "C"})

    def test_rechaza_tamanos_sinteticos_invalidos(self):
        with self.assertRaises(ValueError):
            generar_pedidos_sinteticos(semilla=7, cantidad_productos=0)


if __name__ == "__main__":
    unittest.main()
