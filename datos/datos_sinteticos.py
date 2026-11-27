"""Generación reproducible de filas coherentes para pedidos_planos."""

from random import Random


def generar_pedidos_sinteticos(
    semilla: int,
    cantidad_clientes: int = 8,
    cantidad_productos: int = 10,
    cantidad_pedidos: int = 12,
) -> tuple[dict[str, object], ...]:
    """Genera datos deterministas que respetan las DF del caso demostrativo.

    Una misma semilla y los mismos tamaños producen exactamente las mismas
    filas. Se usa un generador local para no alterar el estado aleatorio global.
    """
    if min(cantidad_clientes, cantidad_productos, cantidad_pedidos) < 1:
        raise ValueError("Las cantidades de clientes, productos y pedidos deben ser positivas.")

    aleatorio = Random(semilla)
    ciudades = ("Cali", "Bogota", "Medellin", "Pasto", "Manizales")
    nombres = ("Ana", "Luis", "Marta", "Juan", "Sofia", "Carlos", "Sara", "David")
    clientes = {
        identificador: (
            f"{nombres[(identificador - 1) % len(nombres)]} {identificador}",
            ciudades[aleatorio.randrange(len(ciudades))],
        )
        for identificador in range(1, cantidad_clientes + 1)
    }
    productos = {
        identificador: (
            f"Producto {identificador}",
            round(aleatorio.uniform(500, 50000), 2),
        )
        for identificador in range(100, 100 + cantidad_productos)
    }

    filas: list[dict[str, object]] = []
    ids_productos = tuple(productos)
    for id_pedido in range(1000, 1000 + cantidad_pedidos):
        id_cliente = aleatorio.choice(tuple(clientes))
        nombre_cliente, ciudad_cliente = clientes[id_cliente]
        cantidad_lineas = aleatorio.randint(1, min(4, cantidad_productos))
        for id_producto in aleatorio.sample(ids_productos, cantidad_lineas):
            nombre_producto, precio = productos[id_producto]
            filas.append({
                "id_pedido": id_pedido,
                "id_cliente": id_cliente,
                "nombre_cliente": nombre_cliente,
                "ciudad_cliente": ciudad_cliente,
                "id_producto": id_producto,
                "nombre_producto": nombre_producto,
                "precio": precio,
                "cantidad": aleatorio.randint(1, 10),
            })
    return tuple(filas)
