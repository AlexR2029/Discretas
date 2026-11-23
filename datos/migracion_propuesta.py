"""Aplicación transaccional y verificación de propuestas de los casos SQL."""

from datos.lector_esquema import (
    escapar_identificador,
    listar_columnas,
    listar_claves,
)
from datos.propuestas import PropuestaCaso


def aplicar_propuesta(conexion, tabla_origen: str, propuesta: PropuestaCaso,
                      tipos: dict[str, str]) -> dict:
    """Crea las entidades y migra sus proyecciones preservando el origen.

    MySQL confirma implícitamente los CREATE TABLE. Por eso se preparan las
    tablas primero y la migración de filas, limpieza y verificaciones se hace
    en una única transacción DML.
    """
    origen = escapar_identificador(tabla_origen)
    entidades = propuesta.entidades
    if not entidades:
        raise ValueError("La propuesta no contiene entidades.")
    nombres = {e.nombre for e in entidades}
    for e in entidades:
        if not e.atributos or not e.pk or not set(e.pk) <= set(e.atributos):
            raise ValueError(f"La entidad {e.nombre} tiene atributos o PK inválidos.")
        for local, remota, destino in e.fk:
            if remota not in nombres:
                raise ValueError(f"FK de {e.nombre} apunta a entidad inexistente {remota}.")
            entidad_remota = next(x for x in entidades if x.nombre == remota)
            if destino not in entidad_remota.atributos or local not in e.atributos:
                raise ValueError(f"FK inválida: {e.nombre}.{local} -> {remota}.{destino}.")

    ddl = []
    for e in entidades:
        definiciones = []
        for atributo in e.atributos:
            tipo = tipos.get(atributo, "VARCHAR(255)")
            # INFORMATION_SCHEMA devuelve tipos MySQL; validar para no aceptar
            # fragmentos SQL que no sean tipos simples.
            if not tipo or not all(c.isalnum() or c in "_(), " for c in tipo):
                raise ValueError(f"Tipo SQL no permitido para {atributo}: {tipo!r}")
            nullabilidad = " NOT NULL"
            definiciones.append(f"{escapar_identificador(atributo)} {tipo}{nullabilidad}")
        definiciones.append("PRIMARY KEY (" + ", ".join(map(escapar_identificador, e.pk)) + ")")
        for indice, atributo in enumerate(e.ak, 1):
            definiciones.append(
                f"UNIQUE KEY `uq_{e.nombre}_{indice}` "
                f"({escapar_identificador(atributo)})"
            )
        for local, remota, destino in e.fk:
            definiciones.append(
                f"FOREIGN KEY ({escapar_identificador(local)}) REFERENCES "
                f"{escapar_identificador(remota)} ({escapar_identificador(destino)})"
            )
        ddl.append(
            f"CREATE TABLE IF NOT EXISTS {escapar_identificador(e.nombre)} "
            f"({', '.join(definiciones)}) ENGINE=InnoDB"
        )

    cursor = conexion.cursor()
    try:
        for sentencia in ddl:
            cursor.execute(sentencia)
        for entidad in entidades:
            columnas_existentes = frozenset(
                columna["nombre"]
                for columna in listar_columnas(conexion, entidad.nombre)
            )
            claves = listar_claves(conexion, entidad.nombre)
            cursor.execute(
                "SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, "
                "REFERENCED_COLUMN_NAME "
                "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
                "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
                "AND REFERENCED_TABLE_NAME IS NOT NULL",
                (conexion.database, entidad.nombre),
            )
            destinos_fk = frozenset(cursor.fetchall())
            destinos_esperados = frozenset(
                (local, remota, destino)
                for local, remota, destino in entidad.fk
            )
            fk_esperadas = frozenset(fk[0] for fk in entidad.fk)
            aks_esperadas = frozenset(frozenset((ak,)) for ak in entidad.ak)
            if (
                columnas_existentes != frozenset(entidad.atributos)
                or claves["pk"] != frozenset(entidad.pk)
                or claves["fk"] != fk_esperadas
                or destinos_fk != destinos_esperados
                or not aks_esperadas.issubset(frozenset(claves["aks"]))
            ):
                raise ValueError(
                    f"La tabla destino {entidad.nombre} ya existe con una "
                    "estructura distinta a la propuesta."
                )
        conexion.start_transaction()
        # Vaciar primero las tablas dependientes y poblar primero las maestras.
        for entidad in reversed(entidades):
            cursor.execute(f"DELETE FROM {escapar_identificador(entidad.nombre)}")
        for entidad in entidades:
            columnas = ", ".join(map(escapar_identificador, entidad.atributos))
            cursor.execute(
                f"INSERT INTO {escapar_identificador(entidad.nombre)} ({columnas}) "
                f"SELECT DISTINCT {columnas} FROM {origen}"
            )

        conteos = {}
        for entidad in entidades:
            nombres_columnas = ", ".join(map(escapar_identificador, entidad.atributos))
            cursor.execute(
                f"SELECT COUNT(*) FROM (SELECT DISTINCT {nombres_columnas} "
                f"FROM {origen}) AS proyeccion"
            )
            esperado = cursor.fetchone()[0]
            cursor.execute(f"SELECT COUNT(*) FROM {escapar_identificador(entidad.nombre)}")
            migrado = cursor.fetchone()[0]
            if esperado != migrado:
                raise ValueError(
                    f"Verificación fallida en {entidad.nombre}: "
                    f"origen proyectado={esperado}, migrado={migrado}."
                )
            conteos[entidad.nombre] = migrado

        # Reconstruir el conjunto de filas de origen mediante las FK declaradas.
        raiz = entidades[0]
        joins = []
        unidas = {raiz.nombre}
        pendientes = list(propuesta.relaciones)
        while len(unidas) < len(entidades):
            avance = False
            for relacion in tuple(pendientes):
                if relacion.origen in unidas and relacion.destino not in unidas:
                    joins.append((relacion, relacion.destino, True))
                    unidas.add(relacion.destino)
                    pendientes.remove(relacion)
                    avance = True
                elif relacion.destino in unidas and relacion.origen not in unidas:
                    joins.append((relacion, relacion.origen, False))
                    unidas.add(relacion.origen)
                    pendientes.remove(relacion)
                    avance = True
            if not avance:
                # Una sola entidad no requiere JOIN; propuestas desconectadas
                # no se pueden demostrar sin pérdida con esta verificación.
                if len(entidades) == 1:
                    break
                raise ValueError("No se pueden reconstruir las entidades mediante sus FK.")
        if len(entidades) > 1:
            raiz_sql = escapar_identificador(raiz.nombre)
            partes = [f"{raiz_sql} AS r0"]
            alias = {raiz.nombre: "r0"}
            for relacion, nueva, forward in joins:
                nuevo_alias = f"r{len(alias)}"
                if forward:
                    izquierda = (
                        f"{alias[relacion.origen]}."
                        f"{escapar_identificador(relacion.atributo_origen)}"
                    )
                    derecha = (
                        f"{nuevo_alias}."
                        f"{escapar_identificador(relacion.atributo_destino)}"
                    )
                else:
                    izquierda = (
                        f"{nuevo_alias}."
                        f"{escapar_identificador(relacion.atributo_origen)}"
                    )
                    derecha = (
                        f"{alias[relacion.destino]}."
                        f"{escapar_identificador(relacion.atributo_destino)}"
                    )
                partes.append(
                    f"JOIN {escapar_identificador(nueva)} AS {nuevo_alias} "
                    f"ON {izquierda} = {derecha}"
                )
                alias[nueva] = nuevo_alias
            cursor.execute(f"SELECT COUNT(*) FROM {origen}")
            filas_origen = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM " + " ".join(partes))
            filas_join = cursor.fetchone()[0]
            if filas_origen != filas_join:
                raise ValueError(
                    f"Verificación de join fallida: origen={filas_origen}, "
                    f"reconstrucción={filas_join}."
                )
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
    return {"entidades": conteos, "ddl": tuple(ddl), "origen": tabla_origen}
