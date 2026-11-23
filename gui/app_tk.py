"""Interfaz Tkinter del normalizador de esquemas."""

import tkinter as tk
import re
from tkinter import messagebox, ttk

from datos.conexion_mysql import (
    abrir_conexion,
    cerrar_conexion,
    leer_configuracion_mysql,
)
from datos.casos_sql import CASOS_SQL, ejecutar_caso
from datos.propuestas import propuesta_para
from datos.generador_sql import (
    ejecutar_migracion,
    generar_migracion_demo,
)
from datos.lector_esquema import (
    listar_columnas,
    listar_tablas,
    listar_claves,
    validar_tabla,
    escapar_identificador,
)
from datos.verificador_df import verificar_dependencias
from src.cierre import cierre, implica
from src.claves import (
    atributos_primos,
    claves_candidatas,
    claves_candidatas_declaradas,
)
from src.cobertura import cobertura_minima
from src.dependencias import DF, parsear_dependencias
from src.descomposicion import descomponer_bcnf, sintetizar_3fn
from src.formas_normales import es_1fn, es_2fn, es_3fn, es_bcnf


class TextoSoloLectura(tk.Text):
    """Text de Tkinter que puede ser actualizado por el programa."""

    def insert(self, index, chars, *args) -> None:
        """Inserta texto permitiendo temporalmente la actualización."""
        self.configure(state="normal")
        super().insert(index, chars, *args)
        self.configure(state="disabled")

    def delete(self, index1, index2=None) -> None:
        """Borra texto permitiendo temporalmente la actualización."""
        self.configure(state="normal")
        super().delete(index1, index2)
        self.configure(state="disabled")


def crear_estado_inicial() -> dict:
    """Crea el estado compartido de todas las pestañas.

    parámetros: ninguno.
    retorno: diccionario vacío con conexión, esquema, DF y resultados.
    complejidad: O(1).
    """
    return {
        "conexion": None,
        "tabla": "",
        "atributos": frozenset(),
        "tabla_confirmada": "",
        "atributos_confirmados": frozenset(),
        "tipos_confirmados": {},
        "pk_confirmada": frozenset(),
        "fk_confirmadas": frozenset(),
        "aks_confirmadas": (),
        "tipos": {},
        "df": (),
        "relaciones_fk": (),
        "resultados": {},
    }


class AplicacionTk(tk.Tk):
    """Ventana principal que delega toda la matemática y el acceso a datos."""

    def __init__(self) -> None:
        """Inicializa la ventana, el estado compartido y las pestañas.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(n), n widgets de las pestañas.
        """
        super().__init__()
        self.title("Normalizador de Esquemas Relacionales")
        self.geometry("980x680")
        self.minsize(820, 560)

        self.estado = crear_estado_inicial()
        self._configurar_estilo()
        self._crear_estado_visual()
        self._crear_pestanas()

    def _configurar_estilo(self) -> None:
        """Aplica estilos ttk básicos.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(1).
        """
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("TNotebook.Tab", padding=(14, 8))

    def _crear_estado_visual(self) -> None:
        """Crea la barra superior y el estado inferior.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(1).
        """
        encabezado = ttk.Frame(self, padding=8)
        encabezado.pack(fill="x")
        ttk.Label(
            encabezado,
            text="Normalizador de Esquemas",
            font=("Segoe UI", 16, "bold"),
        ).pack(side="left")

        pie = ttk.Frame(self, padding=6)
        pie.pack(fill="x", side="bottom")
        self.estado_label = ttk.Label(pie, text="Listo")
        self.estado_label.pack(side="left")

    def _procesando(self, mensaje: str) -> None:
        """Muestra un estado temporal antes de una operación.

        parámetros: mensaje visible al usuario.
        retorno: None.
        complejidad: O(1) más el refresco gráfico requerido.
        """
        self.estado_label.configure(text=mensaje)
        self.update_idletasks()

    def _error(self, accion: Exception | str) -> None:
        """Presenta errores mediante un cuadro de diálogo.

        parámetros: excepción o texto a mostrar.
        retorno: None.
        complejidad: O(1).
        """
        texto = str(accion)
        self.estado_label.configure(text="Error")
        messagebox.showerror("Error", texto, parent=self)

    def _validar_identificador(self, nombre: str, etiqueta: str) -> str:
        """Valida nombres de tablas y atributos introducidos en la interfaz.

        parámetros: nombre y etiqueta que se muestran al usuario.
        retorno: nombre sin espacios externos.
        complejidad: O(|nombre|).
        """
        nombre = nombre.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_$]*", nombre):
            raise ValueError(
                f"{etiqueta} inválido/a. Use letras, números, '_' o '$'; "
                "debe comenzar por letra o '_'."
            )
        return nombre

    def _leer_entero(self, texto: str, etiqueta: str,
                     minimo: int = 0) -> int:
        """Lee un entero con límites claros y un mensaje de entrada válida.

        parámetros: texto, etiqueta visible y mínimo permitido.
        retorno: entero validado.
        complejidad: O(|texto|).
        """
        try:
            valor = int(texto.strip())
        except (TypeError, ValueError) as error:
            raise ValueError(f"{etiqueta} debe ser un número entero.") from error
        if valor < minimo:
            raise ValueError(f"{etiqueta} debe ser mayor o igual que {minimo}.")
        return valor

    def _parsear_x(self, texto: str) -> frozenset[str]:
        """Interpreta el lado X de X -> Y,Z escrito por el usuario.

        parámetros: texto con atributos separados por coma o punto y coma.
        retorno: frozenset de atributos explicitamente indicados.
        complejidad: O(n), n caracteres/nombres indicados.
        """
        texto = texto.strip()
        if not texto:
            return frozenset()
        return frozenset(
            parte.strip()
            for parte in re.split(r"[,;]", texto)
            if parte.strip()
        )

    def _parsear_y(self, texto: str) -> frozenset[str]:
        """Interpreta únicamente el conjunto Y escrito por el usuario.

        parámetros: texto con atributos separados por coma o punto y coma.
        retorno: frozenset vacío si no se indicó Y.
        complejidad: O(n), n caracteres/nombres indicados.
        """
        texto = texto.strip()
        if "->" in texto:
            raise ValueError(
                "El campo Y acepta solo atributos. "
                "No incluya nuevamente una flecha."
            )
        return frozenset(
            parte.strip()
            for parte in re.split(r"[,;]", texto)
            if parte.strip()
        )

    @staticmethod
    def estado_condicional_columna(tipo: str,
                                   clave: str) -> tuple[str, str]:
        """Define cuándo están activos ENUM y los campos de FK.

        parámetros: tipo de columna y tipo de clave seleccionado.
        retorno: estados "normal"/"disabled" para ENUM y campos FK.
        complejidad: O(1).
        """
        estado_enum = "normal" if tipo.upper() == "ENUM" else "disabled"
        estado_fk = "normal" if clave.upper() == "FK" else "disabled"
        return estado_enum, estado_fk

    def _crear_pestanas(self) -> None:
        """Crea las cinco pestañas de la Fase 4.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(n), n widgets básicos declarados.
        """
        cuaderno = ttk.Notebook(self)
        cuaderno.pack(fill="both", expand=True)

        self.pestana_conexion = ttk.Frame(cuaderno, padding=12)
        self.pestana_df = ttk.Frame(cuaderno, padding=12)
        self.pestana_analisis = ttk.Frame(cuaderno, padding=12)
        self.pestana_sql = ttk.Frame(cuaderno, padding=12)

        cuaderno.add(self.pestana_conexion, text="Conexión")
        cuaderno.add(self.pestana_df, text="DF")
        cuaderno.add(self.pestana_analisis, text="Análisis")
        cuaderno.add(self.pestana_sql, text="SQL")

        self._crear_conexion()
        self._crear_df()
        self._crear_analisis()
        self._crear_sql()

    def _crear_conexion(self) -> None:
        """Construye los controles de conexión y listado de tablas.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(n), n controles gráficos.
        """
        config = leer_configuracion_mysql()
        valores = {
            "host": config["host"],
            "port": str(config["port"]),
            "user": config["user"],
            "password": config["password"],
            "database": config["database"],
        }

        formulario = ttk.LabelFrame(self.pestana_conexion, text="Configuración")
        formulario.pack(fill="x")
        self.formulario_conexion = formulario

        self.conexion_campos = {}
        for fila, clave in enumerate(("host", "port", "user", "password", "database")):
            ttk.Label(formulario, text=clave.upper()).grid(
                row=fila, column=0, sticky="w", padx=6, pady=4
            )
            mostrar = "*" if clave == "password" else None
            entrada = ttk.Entry(formulario, width=45, show=mostrar)
            entrada.insert(0, valores[clave])
            entrada.grid(row=fila, column=1, sticky="w", padx=6, pady=4)
            self.conexion_campos[clave] = entrada

        ttk.Button(formulario, text="Conectar", command=self.conectar).grid(
            row=5, column=0, padx=6, pady=8, sticky="w"
        )
        ttk.Button(formulario, text="Listar tablas", command=self.listar_tablas).grid(
            row=5, column=1, padx=6, pady=8, sticky="w"
        )

        self.seccion_conectado = ttk.LabelFrame(
            self.pestana_conexion, text="Conexión"
        )
        self.label_conexion = ttk.Label(
            self.seccion_conectado,
            text="",
            font=("Segoe UI", 10, "bold"),
        )
        self.label_conexion.pack(side="left", padx=8, pady=8)
        ttk.Button(
            self.seccion_conectado,
            text="Desconectar",
            command=self.desconectar,
        ).pack(side="right", padx=8, pady=8)

        resultado = ttk.LabelFrame(self.pestana_conexion, text="Esquema")
        resultado.pack(fill="both", expand=True, pady=8)

        casos = ttk.LabelFrame(
            self.pestana_conexion,
            text="Casos SQL",
        )
        casos.pack(fill="x", pady=(0, 8))
        ttk.Label(casos, text="Caso").grid(
            row=0, column=0, padx=6, pady=6
        )
        self.selector_caso = ttk.Combobox(
            casos,
            values=tuple(CASOS_SQL),
            width=28,
            state="readonly",
        )
        self.selector_caso.set("caso_1_2fn")
        self.selector_caso.grid(row=0, column=1, padx=6, pady=6)
        ttk.Button(
            casos,
            text="Cargar caso",
            command=self.cargar_caso_sql,
        ).grid(row=0, column=2, padx=6, pady=6)

        self.lista_tablas = tk.Listbox(resultado, height=8)
        self.lista_tablas.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        self.lista_tablas.bind("<<ListboxSelect>>", self._seleccionar_tabla)

        self.texto_columnas = TextoSoloLectura(resultado, height=12, width=55)
        self.texto_columnas.configure(state="disabled")
        self.texto_columnas.pack(side="left", fill="both", expand=True, padx=6, pady=6)

    def conectar(self) -> None:
        """Abre la conexión usando los campos visibles.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(1) de código, más la latencia de MySQL.
        """
        self._procesando("Conectando...")
        try:
            if self.estado["conexion"] is not None:
                cerrar_conexion(self.estado["conexion"])
            config = {
                clave: campo.get()
                for clave, campo in self.conexion_campos.items()
            }
            for clave in ("host", "user", "database"):
                config[clave] = config[clave].strip()
                if not config[clave]:
                    raise ValueError(
                        f"{clave.upper()} no puede estar vacío."
                    )
            config["port"] = self._leer_entero(
                config["port"], "DB_PORT", minimo=1
            )
            if config["port"] > 65535:
                raise ValueError("DB_PORT debe estar entre 1 y 65535.")
            conexion = abrir_conexion(config)
            self.estado["conexion"] = conexion
            self.label_conexion.configure(
                text=f"Conectado correctamente a {config['database']}"
            )
            self.formulario_conexion.pack_forget()
            self.seccion_conectado.pack(fill="x", pady=(0, 8))
            self.listar_tablas()
        except (ValueError, ConnectionError, OSError) as error:
            self._error(error)
        except Exception as error:
            self._error(error)

    def desconectar(self) -> None:
        """Cierra la conexión y vuelve a mostrar el formulario seguro.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(1).
        """
        conexion = self.estado["conexion"]
        if conexion is not None:
            cerrar_conexion(conexion)
        self.estado["conexion"] = None
        self.seccion_conectado.pack_forget()
        self.formulario_conexion.pack(fill="x")
        self.lista_tablas.delete(0, tk.END)
        self.texto_columnas.delete("1.0", tk.END)
        self.estado_label.configure(text="Desconectado")

    def listar_tablas(self) -> None:
        """Lista las tablas y deja la selección disponible.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(n log n), n tablas.
        """
        conexion = self.estado["conexion"]
        if conexion is None:
            self._error("Conecte primero al servidor MySQL.")
            return
        self._procesando("Leyendo tablas...")
        try:
            tablas = listar_tablas(conexion)
            self.lista_tablas.delete(0, tk.END)
            for tabla in tablas:
                self.lista_tablas.insert(tk.END, tabla)
            self.estado_label.configure(text=f"{len(tablas)} tablas encontradas")
        except Exception as error:
            self._error(error)

    def cargar_caso_sql(self) -> None:
        """Carga uno de los cinco scripts SQL definidos en scripts/.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(n) sentencias del script seleccionado.
        """
        conexion = self.estado["conexion"]
        if conexion is None:
            self._error("Conecte primero al servidor MySQL.")
            return
        caso = self.selector_caso.get().strip()
        try:
            resultado = ejecutar_caso(conexion, caso)
            self.estado["df"] = ()
            self.estado["tabla_confirmada"] = ""
            self.estado["atributos_confirmados"] = frozenset()
            self.estado["tipos_confirmados"] = {}
            self.estado["pk_confirmada"] = frozenset()
            self.estado["fk_confirmadas"] = frozenset()
            self.estado["aks_confirmadas"] = ()
            self.estado["resultados"] = {}
            self.entrada_tabla_df.delete(0, tk.END)
            self.entrada_tabla_analisis.delete(0, tk.END)
            self.texto_df.delete("1.0", tk.END)
            self.texto_analisis.delete("1.0", tk.END)
            self.listar_tablas()
            self.estado_label.configure(
                text=f"Caso SQL cargado: {caso}"
            )
        except Exception as error:
            self._error(error)

    def _seleccionar_tabla(self, evento=None) -> None:
        """Carga columnas y tipos de la tabla seleccionada.

        parámetros: evento opcional del widget Listbox.
        retorno: None.
        complejidad: O(n), n columnas.
        """
        conexion = self.estado["conexion"]
        seleccion = self.lista_tablas.curselection()
        if conexion is None or not seleccion:
            return
        tabla = self.lista_tablas.get(seleccion[0])
        try:
            columnas = listar_columnas(conexion, tabla)
            self.estado["tabla"] = tabla
            self.estado["atributos"] = frozenset(
                columna["nombre"] for columna in columnas
            )
            self.estado["tipos"] = {
                columna["nombre"]: columna["tipo"] for columna in columnas
            }

            self.texto_columnas.delete("1.0", tk.END)
            for columna in columnas:
                clave = "PK" if columna["clave_primaria"] else ""
                nulable = "NULL" if columna["permite_nulos"] else "NOT NULL"
                self.texto_columnas.insert(
                    tk.END,
                    f"{columna['nombre']} | {columna['tipo']} | {nulable} | {clave}\n",
                )
            self.entrada_tabla_df.delete(0, tk.END)
            self.entrada_tabla_df.insert(0, tabla)
            self.entrada_tabla_analisis.delete(0, tk.END)
            self.entrada_tabla_analisis.insert(0, tabla)
            self.estado_label.configure(text=f"Tabla seleccionada: {tabla}")
        except Exception as error:
            self._error(error)

    def _crear_df(self) -> None:
        """Construye la pestaña editable de dependencias.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(n), n controles.
        """
        superior = ttk.Frame(self.pestana_df)
        superior.pack(fill="x")
        guia = ttk.LabelFrame(
            self.pestana_df,
            text="Guía rápida para escribir DF",
        )
        guia.pack(fill="x", padx=6, pady=6)
        ttk.Label(
            guia,
            text=(
                "Formato: lado_izquierdo -> lado_derecho. "
                "Separe atributos por comas y varias DF por punto y coma.\n"
                "Ejemplo: id_cliente -> nombre_cliente, ciudad_cliente; "
                "id_pedido, id_producto -> cantidad\n"
                "Use solo atributos existentes en la tabla. "
                "X -> X es una DF trivial."
            ),
            justify="left",
        ).pack(fill="x", padx=8, pady=6)
        ttk.Label(superior, text="Tabla").grid(row=0, column=0, padx=6, pady=6)
        self.entrada_tabla_df = ttk.Entry(superior, width=35)
        self.entrada_tabla_df.grid(row=0, column=1, padx=6, pady=6)
        ttk.Label(superior, text="DF").grid(row=1, column=0, padx=6, pady=6)
        self.entrada_df_texto = ttk.Entry(superior, width=70)
        self.entrada_df_texto.grid(row=1, column=1, padx=6, pady=6)

        ttk.Button(
            superior,
            text="Agregar/establecer",
            command=self.establecer_df,
        ).grid(row=2, column=0, padx=6, pady=6)
        ttk.Button(
            superior,
            text="Verificar contra datos",
            command=self.verificar_df_interfaz,
        ).grid(row=2, column=1, padx=6, pady=6, sticky="w")

        self.texto_df = TextoSoloLectura(self.pestana_df, height=20)
        self.texto_df.configure(state="disabled")
        self.texto_df.pack(fill="both", expand=True, padx=6, pady=6)

    def establecer_df(self) -> None:
        """Parsea las DF y las guarda en el estado compartido.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(n·m), n DF y m atributos del esquema.
        """
        try:
            tabla = self._validar_identificador(
                self.entrada_tabla_df.get(),
                "Nombre de tabla",
            )
        except ValueError as error:
            self._error(error)
            return
        atributos = self.estado["atributos"]
        if not tabla:
            self._error("Indique una tabla.")
            return
        if not atributos:
            conexion = self.estado["conexion"]
            if conexion is None:
                self._error("Seleccione una tabla después de conectar.")
                return
            columnas = listar_columnas(conexion, tabla)
            atributos = frozenset(
                columna["nombre"] for columna in columnas
            )
            self.estado["atributos"] = atributos
            self.estado["tipos"] = {
                columna["nombre"]: columna["tipo"] for columna in columnas
            }
        try:
            df = parsear_dependencias(self.entrada_df_texto.get(), atributos)
            self.estado["tabla"] = tabla
            self.estado["df"] = df
            self.estado["tabla_confirmada"] = tabla
            self.estado["atributos_confirmados"] = atributos
            self.texto_df.delete("1.0", tk.END)
            for dependencia in df:
                self.texto_df.insert(tk.END, f"{dependencia}\n")
            self.estado_label.configure(text=f"{len(df)} DF establecidas")
        except Exception as error:
            self._error(error)

    def verificar_df_interfaz(self) -> None:
        """Verifica las DF actuales contra los datos reales.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(d·r·(|X|+|Y|)), d DF y r filas.
        """
        conexion = self.estado["conexion"]
        tabla = self.entrada_tabla_df.get().strip()
        if conexion is None:
            self._error("Conecte primero al servidor MySQL.")
            return
        if not tabla or not self.estado["df"]:
            self._error("Seleccione una tabla y establezca DF.")
            return
        self._procesando("Verificando dependencias...")
        try:
            reportes = verificar_dependencias(
                conexion, tabla, self.estado["df"]
            )
            self.texto_df.delete("1.0", tk.END)
            for reporte in reportes:
                self.texto_df.insert(tk.END, reporte["mensaje"] + "\n")
                for fila in reporte["filas_conflictivas"][:20]:
                    self.texto_df.insert(tk.END, f"  {fila}\n")
            self.estado["resultados"]["df"] = reportes
            self.estado_label.configure(text="Verificación completada")
        except Exception as error:
            self._error(error)

    def _crear_analisis(self) -> None:
        """Construye los controles de cierre, claves y formas normales.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(n), n controles.
        """
        formulario = ttk.LabelFrame(self.pestana_analisis, text="Análisis")
        formulario.pack(fill="x")
        ttk.Label(formulario, text="Tabla").grid(row=0, column=0, padx=6, pady=6)
        self.entrada_tabla_analisis = ttk.Entry(formulario, width=35)
        self.entrada_tabla_analisis.grid(row=0, column=1, padx=6, pady=6)
        ttk.Button(
            formulario,
            text="Confirmar Tabla",
            command=self.confirmar_tabla,
        ).grid(row=0, column=2, padx=6, pady=6)
        ttk.Label(formulario, text="X").grid(row=1, column=0, padx=6, pady=6)
        self.entrada_cierre = ttk.Entry(formulario, width=70)
        self.entrada_cierre.grid(row=1, column=1, columnspan=4, padx=6, pady=6)
        self.entrada_cierre.bind("<Return>", lambda evento: self.calcular_analisis())

        ttk.Button(
            formulario,
            text="Calcular",
            command=self.calcular_analisis,
        ).grid(row=4, column=0, padx=6, pady=6)
        ttk.Button(
            formulario,
            text="Limpiar análisis",
            command=self.limpiar_analisis,
        ).grid(row=4, column=1, padx=6, pady=6)
        ttk.Button(
            formulario,
            text="Dibujar propuesta",
            command=self.dibujar_propuesta_normalizacion,
        ).grid(row=4, column=2, padx=6, pady=6)
        ttk.Button(
            formulario,
            text="Aplicar propuesta",
            command=self.aplicar_propuesta_normalizacion,
        ).grid(row=4, column=3, padx=6, pady=6)

        dividido = ttk.Panedwindow(self.pestana_analisis, orient="horizontal")
        dividido.pack(fill="both", expand=True, padx=6, pady=6)

        panel_texto = ttk.Frame(dividido)
        panel_visual = ttk.Frame(dividido)
        dividido.add(panel_texto, weight=1)
        dividido.add(panel_visual, weight=2)

        self.texto_analisis = TextoSoloLectura(panel_texto, height=24)
        self.texto_analisis.configure(state="disabled")
        self.texto_analisis.pack(fill="both", expand=True)

        canvas_frame = ttk.Frame(panel_visual)
        canvas_frame.pack(fill="both", expand=True)

        self.canvas_tabla = tk.Canvas(
            canvas_frame,
            width=520,
            height=360,
            background="#f7f7f7",
            highlightthickness=1,
            highlightbackground="#b8b8b8",
        )
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_tabla.grid(row=0, column=0, sticky="nsew")

    def confirmar_tabla(self) -> None:
        """Confirma que la tabla existe y dibuja sus columnas y filas.

        Definición formal: la tabla debe pertenecer al esquema MySQL conectado
        y sus atributos deben coincidir con INFORMATION_SCHEMA.
        parámetros: ninguno.
        retorno: None.
        complejidad: O(n log n) para listar/validar y O(r·n) para leer filas,
        con un máximo de 100 filas mostradas.
        """
        conexion = self.estado["conexion"]
        if conexion is None:
            self._error("Conecte primero al servidor MySQL.")
            return
        try:
            tabla = self._validar_identificador(
                self.entrada_tabla_analisis.get(),
                "Nombre de tabla",
            )
            validar_tabla(conexion, tabla)
            columnas = listar_columnas(conexion, tabla)
            if not columnas:
                raise ValueError(
                    f"La tabla '{tabla}' no tiene columnas visibles."
                )
            claves = listar_claves(conexion, tabla)

            tabla_anterior = self.estado["tabla"]
            if tabla_anterior and tabla_anterior != tabla:
                self.estado["df"] = ()
                self.texto_df.delete("1.0", tk.END)
                self.texto_analisis.delete("1.0", tk.END)
                self.estado["resultados"] = {}

            atributos = frozenset(
                columna["nombre"] for columna in columnas
            )
            tipos = {
                columna["nombre"]: columna["tipo"] for columna in columnas
            }
            self.estado["tabla"] = tabla
            self.estado["atributos"] = atributos
            self.estado["tipos"] = tipos
            self.estado["tabla_confirmada"] = tabla
            self.estado["atributos_confirmados"] = atributos
            self.estado["tipos_confirmados"] = tipos
            self.estado["pk_confirmada"] = claves["pk"]
            self.estado["fk_confirmadas"] = claves["fk"]
            self.estado["aks_confirmadas"] = claves["aks"]

            nombres = self._ordenar_nombres_por_clave(
                sorted(atributos),
                claves["pk"],
                claves["fk"],
                claves["aks"],
            )
            seleccion = ", ".join(
                escapar_identificador(nombre) for nombre in nombres
            )
            cursor = conexion.cursor(dictionary=True)
            try:
                cursor.execute(
                    f"SELECT {seleccion} FROM "
                    f"{escapar_identificador(tabla)} LIMIT 100"
                )
                filas = cursor.fetchall()
            finally:
                cursor.close()

            self._dibujar_tabla(
                tabla,
                nombres,
                filas,
                pk=claves["pk"],
                fk=claves["fk"],
                aks=claves["aks"],
            )
            self.entrada_tabla_df.delete(0, tk.END)
            self.entrada_tabla_df.insert(0, tabla)
            self.estado_label.configure(
                text=f"Tabla '{tabla}' confirmada"
            )
        except Exception as error:
            self._error(error)

    @staticmethod
    def _ordenar_nombres_por_clave(
        nombres: list[str],
        pk: frozenset[str],
        fk: frozenset[str],
        aks: tuple[frozenset[str], ...],
    ) -> list[str]:
        """Ordena columnas visualmente: PK, FK, normales y AK.

        parámetros: nombres disponibles y conjuntos de clave.
        retorno: lista de nombres en el orden pedido.
        complejidad: O(n), n nombres.
        """
        disponibles = set(nombres)
        ak = frozenset().union(*aks) if aks else frozenset()
        pk_orden = sorted(disponibles & pk)
        fk_orden = sorted((disponibles & fk) - pk)
        ak_orden = sorted((disponibles & ak) - pk - fk)
        normales = sorted(
            disponibles - pk - fk - ak
        )
        return pk_orden + fk_orden + normales + ak_orden

    def _dibujar_tabla(
        self,
        tabla: str,
        nombres: list[str],
        filas: list[dict],
        pk: frozenset[str] = frozenset(),
        fk: frozenset[str] = frozenset(),
        aks: tuple[frozenset[str], ...] = (),
    ) -> None:
        """Dibuja una tabla única mediante Canvas y Treeview.

        parámetros: nombre de tabla, nombres de columnas y filas consultadas.
        retorno: None.
        complejidad: O(n·r), n columnas y r filas mostradas.
        """
        nombres = self._ordenar_nombres_por_clave(
            list(nombres),
            pk,
            fk,
            aks,
        )
        canvas = self.canvas_tabla
        canvas.delete("all")
        canvas.create_text(
            12,
            18,
            anchor="nw",
            text=f"Tabla: {tabla}",
            font=("Segoe UI", 11, "bold"),
        )
        canvas.create_text(
            12,
            38,
            anchor="nw",
            text=f"{len(nombres)} columnas · {len(filas)} filas mostradas",
            font=("Segoe UI", 9),
            fill="#555555",
        )

        contenedor = ttk.Frame(canvas)
        scroll_y = ttk.Scrollbar(
            contenedor,
            orient="vertical",
        )
        scroll_x = ttk.Scrollbar(
            contenedor,
            orient="horizontal",
        )
        tree = ttk.Treeview(
            contenedor,
            columns=tuple(nombres),
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            height=min(12, max(4, len(filas) + 1)),
        )
        for nombre in nombres:
            tree.heading(nombre, text=nombre)
            tree.column(nombre, width=max(90, min(180, len(nombre) * 12 + 60)),
                        minwidth=70, anchor="w", stretch=True)

        for indice, fila in enumerate(filas, start=1):
            valores = [
                "" if fila[nombre] is None else str(fila[nombre])
                for nombre in nombres
            ]
            etiquetas = ("par",) if indice % 2 == 0 else ("impar",)
            tree.insert("", tk.END, values=valores, tags=etiquetas)

        tree.tag_configure("par", background="#eef4fb")
        tree.tag_configure("impar", background="#ffffff")

        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)
        tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)

        canvas_window = canvas.create_window(
            12,
            58,
            anchor="nw",
            width=500,
            height=280,
            window=contenedor,
        )
        canvas.itemconfigure(canvas_window)
        canvas.configure(scrollregion=(0, 0, 530, 350))

    def dibujar_propuesta_normalizacion(self) -> None:
        """Dibuja las relaciones propuestas por síntesis 3FN."""
        atributos = self.estado["atributos_confirmados"]
        df = self.estado["df"]
        if not atributos or not df:
            self._error(
                "Confirme la tabla y establezca las DF antes de proponer."
            )
            return
        nombre_caso = self.selector_caso.get().strip()
        propuesta = propuesta_para(nombre_caso, atributos, df)
        self._dibujar_propuesta(propuesta)

    def _dibujar_propuesta(
        self,
        propuesta,
    ) -> None:
        """Representa entidades, claves y relaciones normalizadas."""
        canvas = self.canvas_tabla
        canvas.delete("all")
        canvas.create_text(
            12,
            18,
            anchor="nw",
            text="Propuesta normalizada",
            font=("Segoe UI", 11, "bold"),
        )
        posiciones: dict[str, tuple[int, int]] = {}
        for indice, entidad in enumerate(propuesta.entidades, start=1):
            x = 12 + ((indice - 1) % 2) * 250
            y = 55 + ((indice - 1) // 2) * 145
            posiciones[entidad.nombre] = (x, y)
            filas = []
            for atributo in entidad.atributos:
                rol = []
                if atributo in entidad.pk:
                    rol.append("PK")
                fk_local = next(
                    (fk for fk in entidad.fk if fk[0] == atributo),
                    None,
                )
                if fk_local is not None:
                    rol.append("FK")
                if atributo in entidad.ak:
                    rol.append("AK")
                sufijo = f" [{'/'.join(rol)}]" if rol else ""
                filas.append(f"{atributo}{sufijo}")

            canvas.create_rectangle(
                x,
                y,
                x + 230,
                y + 105,
                fill="#eef4fb",
                outline="#6b7280",
            )
            canvas.create_text(
                x + 12,
                y + 12,
                anchor="nw",
                text=entidad.nombre,
                font=("Segoe UI", 10, "bold"),
            )
            canvas.create_text(
                x + 12,
                y + 35,
                anchor="nw",
                text="\n".join(filas),
                font=("Courier", 9),
                width=205,
            )
        for relacion in propuesta.relaciones:
            if relacion.origen not in posiciones or relacion.destino not in posiciones:
                continue
            origen_x, origen_y = posiciones[relacion.origen]
            destino_x, destino_y = posiciones[relacion.destino]
            origen_centro = (origen_x + 230, origen_y + 52)
            destino_centro = (destino_x, destino_y + 52)
            canvas.create_line(
                origen_centro[0],
                origen_centro[1],
                destino_centro[0],
                destino_centro[1],
                fill="#2563eb",
                width=2,
                arrow=tk.LAST,
            )
            canvas.create_text(
                (origen_centro[0] + destino_centro[0]) // 2,
                (origen_centro[1] + destino_centro[1]) // 2 - 8,
                text=f"{relacion.atributo_origen} -> "
                     f"{relacion.atributo_destino}",
                fill="#1d4ed8",
                font=("Segoe UI", 8),
            )
        canvas.configure(
            scrollregion=(
                0,
                0,
                520,
                55 + len(propuesta.entidades) * 155,
            )
        )

    def aplicar_propuesta_normalizacion(self) -> None:
        """Crea las tablas 3FN propuestas y migra datos sin eliminar el origen."""
        try:
            conexion = self.estado["conexion"]
            tabla_origen = self.estado["tabla_confirmada"]
            atributos = self.estado["atributos_confirmados"]
            df = self.estado["df"]
            if conexion is None or not tabla_origen:
                raise ValueError("Confirme una tabla cargada desde scripts/.")
            if not atributos or not df:
                raise ValueError("Establezca las DF en la pestaña DF.")

            nombre_caso = self.selector_caso.get().strip()
            propuesta = propuesta_para(nombre_caso, atributos, df)
            tipos = self.estado["tipos_confirmados"]
            cursor = conexion.cursor()
            sentencias: list[str] = []
            try:
                conexion.start_transaction()
                for entidad in propuesta.entidades:
                    nombre = entidad.nombre
                    columnas = list(entidad.atributos)
                    definiciones = []
                    for columna in columnas:
                        tipo = tipos.get(columna, "VARCHAR(255)")
                        definiciones.append(
                            f"{escapar_identificador(columna)} {tipo}"
                        )
                    if entidad.pk:
                        definiciones.append(
                            "PRIMARY KEY (" +
                            ", ".join(
                                escapar_identificador(columna)
                                for columna in entidad.pk
                            ) +
                            ")"
                        )
                    for atributo, tabla_ref, atributo_ref in entidad.fk:
                        definiciones.append(
                            f"FOREIGN KEY ({escapar_identificador(atributo)}) "
                            f"REFERENCES {escapar_identificador(tabla_ref)} "
                            f"({escapar_identificador(atributo_ref)})"
                        )
                    for atributo in entidad.ak:
                        definiciones.append(
                            f"UNIQUE KEY ({escapar_identificador(atributo)})"
                        )
                    sentencias.append(
                        f"CREATE TABLE IF NOT EXISTS "
                        f"{escapar_identificador(nombre)} "
                        f"({', '.join(definiciones)})"
                    )
                    cursor.execute(sentencias[-1])
                    cursor.execute(
                        f"DELETE FROM {escapar_identificador(nombre)}"
                    )
                    seleccion = ", ".join(
                        escapar_identificador(columna)
                        for columna in columnas
                    )
                    if columnas:
                        cursor.execute(
                            f"INSERT INTO {escapar_identificador(nombre)} "
                            f"({seleccion}) "
                            f"SELECT DISTINCT {seleccion} "
                            f"FROM {escapar_identificador(tabla_origen)}"
                        )
                conexion.commit()
            except Exception:
                conexion.rollback()
                raise
            finally:
                cursor.close()

            self._dibujar_propuesta(propuesta)
            self.estado["resultados"]["propuesta"] = {
                "entidades": propuesta.entidades,
                "relaciones": propuesta.relaciones,
                "sentencias": tuple(sentencias),
            }
            self.estado_label.configure(
                text=f"Propuesta aplicada: {len(relaciones)} tablas creadas"
            )
        except Exception as error:
            self._error(error)

    def calcular_analisis(self) -> None:
        """Calcula cierre, claves, cobertura y formas normales.

        parámetros: ninguno.
        retorno: None.
        complejidad: depende de claves candidatas y cierre.
        """
        tabla = self.entrada_tabla_analisis.get().strip()
        atributos_confirmados = self.estado["atributos_confirmados"]
        tabla_confirmada = self.estado["tabla_confirmada"]
        atributos = (
            atributos_confirmados
            if tabla_confirmada and tabla == tabla_confirmada
            else self.estado["atributos"]
        )
        df = self.estado["df"]

        texto_df = self.entrada_df_texto.get().strip()
        if texto_df:
            try:
                df = parsear_dependencias(texto_df, atributos)
                self.estado["df"] = df
            except Exception as error:
                self._error(error)
                return

        if not atributos:
            if str(self.focus_get()) == str(self.entrada_cierre):
                return
            self._error("Seleccione una tabla primero.")
            return
        try:
            x = self.entrada_cierre.get().strip()
            if "->" in x:
                izquierdo, derecho = x.split("->", 1)
                x_atributos = self._parsear_x(izquierdo)
                y_atributos = self._parsear_y(derecho)
            else:
                x_atributos = self._parsear_x(x)
                y_atributos = frozenset()
            desconocidos = (x_atributos | y_atributos) - atributos
            if desconocidos:
                raise ValueError(
                    "X o Y contienen atributos fuera del esquema: "
                    + ", ".join(sorted(desconocidos))
                )
            pk = self.estado["pk_confirmada"]
            fk = self.estado["fk_confirmadas"]
            aks = self.estado["aks_confirmadas"]
            cierre_resultado = cierre(x_atributos, df) if x_atributos else frozenset()
            implicacion = (
                implica(df, x_atributos, y_atributos)
                if y_atributos
                else None
            )
            pk = self.estado["pk_confirmada"]
            fk = self.estado["fk_confirmadas"]
            aks = self.estado["aks_confirmadas"]
            claves = claves_candidatas_declaradas(
                atributos,
                df,
                pk=pk,
                aks=aks,
            )
            primos = frozenset().union(*claves) if claves else frozenset()
            cobertura = cobertura_minima(atributos, df)
            claves_forma = tuple(
                dict.fromkeys(
                    ((pk,) if pk else ())
                    + tuple(aks)
                )
            )
            claves_argumento = (
                claves_forma if claves_forma else None
            )
            reportes = {
                "1fn": es_1fn(
                    atributos,
                    tipos=self.estado["tipos"],
                ),
                "2fn": es_2fn(
                    atributos,
                    df,
                    claves=claves_argumento,
                ),
                "3fn": es_3fn(
                    atributos,
                    df,
                    claves=claves_argumento,
                ),
                "bcnf": es_bcnf(
                    atributos,
                    df,
                    claves=claves_argumento,
                ),
            }

            self.texto_analisis.delete("1.0", tk.END)
            self.texto_analisis.insert(tk.END, f"Cierre(X): {sorted(cierre_resultado)}\n")
            if y_atributos:
                resultado_implica = "Sí" if implicacion else "No"
                self.texto_analisis.insert(
                    tk.END,
                    f"Implica ({', '.join(sorted(x_atributos))}) "
                    f"-> ({', '.join(sorted(y_atributos))}): "
                    f"{resultado_implica}\n",
                )
            self.texto_analisis.insert(
                tk.END,
                f"PK declarada: {[sorted(k) for k in ((pk,) if pk else ())]}\n",
            )
            self.texto_analisis.insert(
                tk.END,
                f"FK declaradas: {sorted(fk)}\n",
            )
            self.texto_analisis.insert(
                tk.END,
                f"AK declaradas: {[sorted(k) for k in aks]}\n",
            )
            self.texto_analisis.insert(
                tk.END,
                f"Claves candidatas válidas: {[sorted(k) for k in claves]}\n",
            )
            self.texto_analisis.insert(
                tk.END,
                "Atributos primos: "
                f"{sorted(primos)} "
                "(pertenecen a alguna PK/AK candidata)\n",
            )
            self.texto_analisis.insert(
                tk.END,
                f"Cobertura mínima: {[str(d) for d in cobertura]}\n",
            )
            for nombre, reporte in reportes.items():
                self.texto_analisis.insert(
                    tk.END,
                    f"{nombre.upper()}: {reporte['mensaje']}\n",
                )
            if not reportes["3fn"]["cumple"]:
                relaciones = sintetizar_3fn(atributos, df)
                self.estado["resultados"]["propuesta"] = {
                    "relaciones": relaciones,
                    "sentencias": (),
                }
                self.texto_analisis.insert(
                    tk.END,
                    "La tabla no cumple 3FN; propuesta disponible "
                    "en Dibujar/Aplicar propuesta.\n",
                )
                self._dibujar_propuesta(relaciones)
            self.estado["resultados"]["analisis"] = {
                "cierre": cierre_resultado,
                "claves": claves,
                "primos": primos,
                "cobertura": cobertura,
                "formas_normales": reportes,
            }
            self.estado_label.configure(text="Análisis completado")
        except Exception as error:
            self._error(error)

    def limpiar_analisis(self) -> None:
        """Borra el resultado y el conjunto X del análisis.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(n), n caracteres del cuadro de texto.
        """
        self.entrada_cierre.delete(0, tk.END)
        self.texto_analisis.delete("1.0", tk.END)
        self.canvas_tabla.delete("all")
        self.estado["resultados"].pop("analisis", None)
        self.estado_label.configure(text="Análisis limpiado")

    def _crear_sql(self) -> None:
        """Construye la pestaña de descomposición y SQL.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(n), n controles.
        """
        controles = ttk.Frame(self.pestana_sql)
        controles.pack(fill="x")
        ttk.Button(
            controles,
            text="Cargar caso de demostración",
            command=self.cargar_demo,
        ).pack(side="left", padx=6, pady=6)
        ttk.Button(
            controles,
            text="Generar propuesta",
            command=self.generar_propuesta_sql,
        ).pack(side="left", padx=6, pady=6)
        ttk.Button(
            controles,
            text="Solo mostrar",
            command=lambda: self.ejecutar_sql(solo_mostrar=True),
        ).pack(side="left", padx=6, pady=6)
        ttk.Button(
            controles,
            text="Ejecutar",
            command=lambda: self.ejecutar_sql(solo_mostrar=False),
        ).pack(side="left", padx=6, pady=6)
        ttk.Button(
            controles,
            text="Actualizar propuesta",
            command=self.generar_propuesta_sql,
        ).pack(side="left", padx=6, pady=6)
        ttk.Button(
            controles,
            text="Limpiar",
            command=self.limpiar_sql,
        ).pack(side="left", padx=6, pady=6)

        self.texto_sql = TextoSoloLectura(self.pestana_sql, height=24)
        self.texto_sql.configure(state="disabled")
        self.texto_sql.pack(fill="both", expand=True, padx=6, pady=6)

    def cargar_demo(self) -> None:
        """Carga pedidos_planos y sus DF sin ejecutar SQL.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(n), n DF declaradas.
        """
        atributos = frozenset({
            "id_pedido", "id_cliente", "nombre_cliente", "ciudad_cliente",
            "id_producto", "nombre_producto", "precio", "cantidad",
        })
        df = (
            DF("id_cliente", "nombre_cliente,ciudad_cliente"),
            DF("id_producto", "nombre_producto,precio"),
            DF("id_pedido", "id_cliente"),
            DF("id_pedido,id_producto", "cantidad"),
        )
        self.estado["tabla"] = "pedidos_planos"
        self.estado["atributos"] = atributos
        self.estado["df"] = df
        self.entrada_tabla_df.delete(0, tk.END)
        self.entrada_tabla_df.insert(0, "pedidos_planos")
        self.entrada_tabla_analisis.delete(0, tk.END)
        self.entrada_tabla_analisis.insert(0, "pedidos_planos")
        self.texto_df.delete("1.0", tk.END)
        for dependencia in df:
            self.texto_df.insert(tk.END, f"{dependencia}\n")
        self.estado_label.configure(text="Caso de demostración cargado")

    def limpiar_sql(self) -> None:
        """Borra el SQL mostrado y elimina la propuesta almacenada.

        parámetros: ninguno.
        retorno: None.
        complejidad: O(n), n caracteres del cuadro SQL.
        """
        self.texto_sql.delete("1.0", tk.END)
        self.estado["resultados"].pop("sql", None)
        self.estado_label.configure(text="Salida SQL limpiada")

    def generar_propuesta_sql(self) -> None:
        """Genera 3FN/BCNF, tableau y SQL para el caso activo.

        parámetros: ninguno.
        retorno: None.
        complejidad: depende de descomposición y tableau.
        """
        atributos = self.estado["atributos"]
        df = self.estado["df"]
        if not atributos or not df:
            self._error("Cargue el caso de demostración o establezca DF.")
            return
        self._procesando("Generando descomposición...")
        try:
            tresfn = sintetizar_3fn(atributos, df)
            bcnf = descomponer_bcnf(atributos, df)
            del tresfn
            sentencias = generar_migracion_demo()
            self.estado["resultados"]["sql"] = sentencias
            self.texto_sql.delete("1.0", tk.END)
            self.texto_sql.insert(
                tk.END,
                "BCNF: " + ", ".join(str(sorted(r)) for r in bcnf) + "\n\n",
            )
            for sentencia in sentencias:
                self.texto_sql.insert(tk.END, sentencia + ";\n")
            self.estado_label.configure(text="Propuesta SQL generada")
        except Exception as error:
            self._error(error)

    def ejecutar_sql(self, solo_mostrar: bool) -> None:
        """Muestra o ejecuta las sentencias SQL generadas.

        parámetros: solo_mostrar True evita ejecución.
        retorno: None.
        complejidad: O(n) sentencias, n SQL generado.
        """
        conexion = self.estado["conexion"]
        sentencias = self.estado["resultados"].get("sql")
        if sentencias is None:
            self._error("Genere primero la propuesta SQL.")
            return
        if solo_mostrar:
            resultado = ejecutar_migracion(
                conexion,
                sentencias,
                solo_mostrar=True,
            )
            self.texto_sql.delete("1.0", tk.END)
            for sentencia in resultado["sentencias"]:
                self.texto_sql.insert(tk.END, sentencia + ";\n")
            self.estado_label.configure(text=resultado["mensaje"])
            return
        if conexion is None:
            self._error("Conecte primero al servidor MySQL.")
            return
        self._procesando("Ejecutando migración...")
        try:
            resultado = ejecutar_migracion(conexion, sentencias)
            self.texto_sql.delete("1.0", tk.END)
            self.texto_sql.insert(
                tk.END,
                f"{resultado['mensaje']}\n"
                f"Sentencias ejecutadas: {resultado['ejecutadas']}\n",
            )
            self.estado_label.configure(text=resultado["mensaje"])
            messagebox.showinfo(
                "SQL",
                f"{resultado['ejecutadas']} sentencias ejecutadas.",
                parent=self,
            )
        except Exception as error:
            self._error(error)


def ejecutar_aplicacion() -> None:
    """Crea y muestra la ventana principal.

    parámetros: ninguno.
    retorno: None.
    complejidad: O(1) al iniciar; el bucle Tk persiste hasta cerrar.
    """
    app = AplicacionTk()
    app.mainloop()