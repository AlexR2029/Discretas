"""Verifica que SQL use el caso asignado y admita ejecuciones repetidas."""

import unittest

from datos.sql_casos import generar_migracion_caso, tablas_destino_caso


class PruebasSQLPorCaso(unittest.TestCase):
    def test_destinos_corresponden_a_cada_caso(self):
        esperados = {
            "caso_1_2fn": ("productos", "pedido_detalles"),
            "caso_2_3fn": ("programas", "estudiantes"),
            "caso_3_bcnf": ("profesores_cursos", "alumno_profesor"),
            "caso_4_dos_claves": ("personas",),
            "caso_5_bcnf_ok": ("empleados",),
        }
        for caso, tablas in esperados.items():
            with self.subTest(caso=caso):
                self.assertEqual(tablas_destino_caso(caso), tablas)
                sql = generar_migracion_caso(caso)
                ddls = sql[:len(tablas)]
                inserts = sql[len(tablas):]
                self.assertEqual(len(ddls), len(tablas))
                self.assertEqual(len(inserts), len(tablas))
                for ddl, tabla in zip(ddls, tablas):
                    self.assertIn("CREATE TABLE IF NOT EXISTS", ddl)
                    self.assertIn(tabla, ddl)
                for insercion in inserts:
                    self.assertIn("ON DUPLICATE KEY UPDATE", insercion)
                    self.assertIn("SELECT DISTINCT", insercion)
                    self.assertNotIn("pedidos_planos", insercion)

    def test_caso_usa_su_tabla_origen_y_rechaza_otra(self):
        sql = generar_migracion_caso("caso_2_3fn", "caso_2_estudiantes")
        self.assertTrue(
            all("caso_2_estudiantes" in sentencia for sentencia in sql[2:])
        )
        with self.assertRaisesRegex(ValueError, "caso_2_estudiantes"):
            generar_migracion_caso("caso_2_3fn", "caso_1_pedidos")

    def test_esquemas_incluyen_claves_y_relaciones_de_soluciones(self):
        caso1 = generar_migracion_caso("caso_1_2fn")
        self.assertIn("PRIMARY KEY", caso1[1])
        self.assertIn("id_pedido", caso1[1])
        self.assertIn("id_producto", caso1[1])
        self.assertIn("REFERENCES", caso1[1])
        self.assertIn("productos", caso1[1])

        caso2 = generar_migracion_caso("caso_2_3fn")
        self.assertIn("REFERENCES", caso2[1])
        self.assertIn("programas", caso2[1])

        caso3 = generar_migracion_caso("caso_3_bcnf")
        self.assertIn("PRIMARY KEY", caso3[1])
        self.assertIn("alumno", caso3[1])
        self.assertIn("profesor", caso3[1])
        self.assertIn("profesores_cursos", caso3[1])

        caso4 = generar_migracion_caso("caso_4_dos_claves")
        self.assertIn("uk_persona_email", caso4[0])
        self.assertIn("UNIQUE", caso4[0])


if __name__ == "__main__":
    unittest.main()
