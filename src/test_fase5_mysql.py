"""Prueba MySQL de ida/vuelta, activada explícitamente para el esquema pruebas."""

import os
import unittest
from uuid import uuid4

from datos.datos_sinteticos import generar_pedidos_sinteticos
from datos.generador_sql import (
    ejecutar_migracion,
    generar_ddl,
    generar_insertar_desde,
    escapar,
)


class PruebaMySQLIdaVuelta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("RUN_MYSQL_E2E") != "1":
            raise unittest.SkipTest("Defina RUN_MYSQL_E2E=1 para probar MySQL.")
        from datos.conexion_mysql import abrir_conexion, leer_configuracion_mysql

        configuracion = leer_configuracion_mysql()
        if configuracion.get("database") != "pruebas":
            raise unittest.SkipTest(
                "La prueba solo se permite contra la base aislada 'pruebas'."
            )
        cls.conexion = abrir_conexion()

    @classmethod
    def tearDownClass(cls):
        conexion = getattr(cls, "conexion", None)
        if conexion is not None:
            conexion.close()

    def test_migracion_reconstruye_exactamente_las_filas(self):
        sufijo = uuid4().hex[:10]
        origen = f"f5_origen_{sufijo}"
        clientes = f"f5_clientes_{sufijo}"
        productos = f"f5_productos_{sufijo}"
        pedidos = f"f5_pedidos_{sufijo}"
        detalles = f"f5_detalles_{sufijo}"
        tablas = (origen, clientes, productos, pedidos, detalles)
        cursor = self.conexion.cursor()
        try:
            cursor.execute(
                f"CREATE TABLE {escapar(origen)} ("
                "id_pedido INT NOT NULL, id_cliente INT NOT NULL, "
                "nombre_cliente VARCHAR(120) NOT NULL, "
                "ciudad_cliente VARCHAR(80) NOT NULL, id_producto INT NOT NULL, "
                "nombre_producto VARCHAR(120) NOT NULL, "
                "precio DECIMAL(10,2) NOT NULL, cantidad INT NOT NULL, "
                "PRIMARY KEY (id_pedido, id_producto)) ENGINE=InnoDB"
            )
            filas = generar_pedidos_sinteticos(
                semilla=2026,
                cantidad_clientes=4,
                cantidad_productos=5,
                cantidad_pedidos=7,
            )
            columnas_origen = (
                "id_pedido", "id_cliente", "nombre_cliente", "ciudad_cliente",
                "id_producto", "nombre_producto", "precio", "cantidad",
            )
            placeholders = ", ".join("%s" for _ in columnas_origen)
            cursor.executemany(
                f"INSERT INTO {escapar(origen)} "
                f"({', '.join(map(escapar, columnas_origen))}) "
                f"VALUES ({placeholders})",
                [tuple(fila[columna] for columna in columnas_origen) for fila in filas],
            )
            self.conexion.commit()

            relaciones = {
                clientes: {"id_cliente", "nombre_cliente", "ciudad_cliente"},
                productos: {"id_producto", "nombre_producto", "precio"},
                pedidos: {"id_pedido", "id_cliente"},
                detalles: {"id_pedido", "id_producto", "cantidad"},
            }
            claves = {
                clientes: ("id_cliente",),
                productos: ("id_producto",),
                pedidos: ("id_pedido",),
                detalles: ("id_pedido", "id_producto"),
            }
            tipos = {
                "id_pedido": "INT",
                "id_cliente": "INT",
                "nombre_cliente": "VARCHAR(120)",
                "ciudad_cliente": "VARCHAR(80)",
                "id_producto": "INT",
                "nombre_producto": "VARCHAR(120)",
                "precio": "DECIMAL(10,2)",
                "cantidad": "INT",
            }
            fks = (
                (pedidos, ("id_cliente",), clientes, ("id_cliente",)),
                (detalles, ("id_pedido",), pedidos, ("id_pedido",)),
                (detalles, ("id_producto",), productos, ("id_producto",)),
            )
            for sentencia in generar_ddl(relaciones, claves, tipos, fks):
                cursor.execute(sentencia)
            self.conexion.commit()
            ejecutar_migracion(
                self.conexion,
                generar_insertar_desde(origen, relaciones),
            )

            consulta = (
                f"SELECT o.id_pedido, o.id_cliente, c.nombre_cliente, "
                f"c.ciudad_cliente, d.id_producto, p.nombre_producto, "
                f"p.precio, d.cantidad FROM {escapar(pedidos)} AS o "
                f"JOIN {escapar(clientes)} AS c ON o.id_cliente=c.id_cliente "
                f"JOIN {escapar(detalles)} AS d ON o.id_pedido=d.id_pedido "
                f"JOIN {escapar(productos)} AS p ON d.id_producto=p.id_producto "
                "ORDER BY o.id_pedido, d.id_producto"
            )
            cursor.execute(
                f"SELECT {', '.join(map(escapar, columnas_origen))} "
                f"FROM {escapar(origen)} ORDER BY id_pedido, id_producto"
            )
            originales = set(cursor.fetchall())
            cursor.execute(consulta)
            reconstruidas = set(cursor.fetchall())
            self.assertEqual(reconstruidas, originales)
        finally:
            try:
                self.conexion.rollback()
                for tabla in (detalles, pedidos, productos, clientes, origen):
                    cursor.execute(f"DROP TABLE IF EXISTS {escapar(tabla)}")
                self.conexion.commit()
            finally:
                cursor.close()


if __name__ == "__main__":
    unittest.main()
