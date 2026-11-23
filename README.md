# Normalizador de Esquemas Relacionales con Matemática Discreta

Herramienta en Python que carga cinco casos SQL, analiza sus esquemas y normaliza tablas relacionales mediante dependencias funcionales, teoría de conjuntos y relaciones.

Proyecto Integrador (Actividad No 10) – Matemática Discreta, Ingeniería Informática.

Integrantes: Alessandro Herrera Medina · Brayan Stiven Duque Hernandez · Anderson Ararat Quevedo
Docente: Oswaldo Rodriguez Diaz · 4 semestre

---

##  Decisiones de arquitectura

| Decisión | Valor |
| --- | --- |
| Lenguaje | Python 3.11 o superior |
| Interfaz gráfica | Tkinter / ttk (incluida con Python) |
| Gestor de base de datos | MySQL 8.x, **servidor local** |
| Host y puerto por defecto | `127.0.0.1:3306` (configurable) |
| Esquema de trabajo | `pruebas` (base existente, sin crear ni recrear) |
| Núcleo matemático | Python puro con `frozenset`; **sin librerías de normalización** |
| Empaquetado | PyInstaller (`.exe`) |

MongoDB y Firebase quedaron descartados porque la normalización es una teoría de modelos relacionales (tablas, claves, joins).

**Principio de diseño:** el núcleo (`nucleo/`) no importa MySQL ni Tkinter. Trabaja solo con conjuntos en memoria, así se prueba con `unittest` sin servidor y se puede sustentar como matemática pura.

---

## Dependencias y documentación

### Obligatorias

| Dependencia | Para qué se usa | Instalación | Documentación |
| --- | --- | --- | --- |
| Python 3.11+ | Lenguaje base | https://www.python.org/downloads/ | https://docs.python.org/3/ |
| MySQL Server 8.x | Base de datos local | https://dev.mysql.com/downloads/mysql/ | https://dev.mysql.com/doc/refman/8.0/en/ |
| mysql-connector-python | Conexión Python a MySQL | `pip install mysql-connector-python` | https://dev.mysql.com/doc/connector-python/en/ |
| tkinter / ttk | Interfaz gráfica (viene con Python) | En Linux: `sudo apt install python3-tk` | https://docs.python.org/3/library/tkinter.html y https://docs.python.org/3/library/tkinter.ttk.html |
| unittest | Pruebas del núcleo (biblioteca estándar) | Incluida | https://docs.python.org/3/library/unittest.html |

### Para generar el ejecutable

| Dependencia | Para qué se usa | Instalación | Documentación |
| --- | --- | --- | --- |
| PyInstaller | Crear el `.exe` | `pip install pyinstaller` | https://pyinstaller.org/en/stable/ |

### Opcionales (solo si sobra tiempo)

| Dependencia | Para qué se usa | Instalación | Documentación |
| --- | --- | --- | --- |
| matplotlib | Dibujar el grafo de dependencias (solo dibujo) | `pip install matplotlib` | https://matplotlib.org/stable/ |
| networkx | Solo para dibujar; los algoritmos son propios | `pip install networkx` | https://networkx.org/documentation/stable/ |

### Módulos de la biblioteca estándar que usa el proyecto

`itertools` (combinaciones para claves candidatas), `random` (datos sintéticos con semilla), `dataclasses`, `typing`, `os` y `json` (configuración).
Documentación general: https://docs.python.org/3/library/

> **Regla del proyecto:** las librerías externas solo pueden usarse para conexión, interfaz o dibujo. Cierre de atributos, claves, formas normales, cobertura mínima, descomposición, tableau y join natural están implementados por el equipo.

### Archivo `requirements.txt`

```text
mysql-connector-python
pyinstaller
# opcionales:
# matplotlib
# networkx
```

> Antes de la entrega, ejecutar `pip freeze` en el entorno limpio y fijar las versiones exactas en este archivo y en la sección 3.

---

## Requisitos del sistema

- Sistema operativo: Windows 10/11, Linux o macOS.
- Python 3.11 o superior (verificar con `python --version`).
- MySQL Server 8.x en ejecución en el equipo.
- 4 GB de RAM y 200 MB de disco libres.
- Versiones usadas en las pruebas finales: _Python x.y.z · MySQL x.y.z · mysql-connector-python x.y.z_ (completar).

---

## Instalación y ejecución

### Clonar y preparar el entorno (ya hecho)

```bash
git clone <url-del-repositorio>
cd Proyecto_Discretas
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 4.2 Preparar MySQL local

1. Verificar que el servicio MySQL está activo (puerto 3306 por defecto).
2. Ejecutar el script incluido sobre la base existente `pruebas`:

```bash
mysql -u root -p < scripts/crear_bd_lab.sql
```

El script solo crea o actualiza la tabla `pedidos_planos`; no crea ni recrea
la base `pruebas` ni añade usuarios.

3. Definir las credenciales con variables de entorno (no se suben al repositorio):

| Variable | Valor en `.env` |
| --- | --- |
| `HOST` | Vacío por defecto |
| `DB_PORT` | Vacío por defecto |
| `USER` | Vacío por defecto |
| `PASSWORD` | Vacío por defecto |
| `DATABASE` | `pruebas` |

### 4.3 Ejecutar la aplicación

```bash
python main.py
```

### 4.4 Ejecutar las pruebas

```bash
python -m unittest discover -s pruebas -v
```

### 4.5 Generar el ejecutable

```bash
pyinstaller --onefile --windowed --name NormalizadorBD main.py
```

El ejecutable queda en `dist/NormalizadorBD.exe`. Probarlo en un equipo sin Python instalado.

---

## 5. Estructura del proyecto

```text
Proyecto_Discretas/
├── main.py                    # punto de entrada
├── requirements.txt
├── README.md
├── src/                    # MATEMÁTICA DISCRETA (sin MySQL, sin Tkinter)
│   ├── dependencias.py        # clase DF y parser "A,B -> C"
│   ├── cierre.py              # cierre X+, implicación, Armstrong
│   ├── claves.py              # claves candidatas, atributos primos
│   ├── formas_normales.py     # 1FN, 2FN, 3FN, BCNF
│   ├── cobertura.py           # cobertura mínima
│   ├── descomposicion.py      # síntesis 3FN, descomposición BCNF
│   └── tableau.py             # prueba de join sin pérdida (chase)
├── datos/
│   ├── conexion_mysql.py      # conexión y esquema aislado
│   ├── lector_esquema.py      # lectura de INFORMATION_SCHEMA
│   ├── verificador_df.py      # GROUP BY ... HAVING COUNT(DISTINCT)
│   └── generador_sql.py       # CREATE TABLE e INSERT ... SELECT DISTINCT
├── gui/
│   └── app_tk.py              # pestañas: Conexión, DF, Análisis, SQL
├── tests/                   # unittest del núcleo y de los casos SQL
├── docs/                      # informe, manual, diapositivas, capturas
├── icons/                    #para imagenes
└── scripts/
    └── crear_bd_lab.sql
```

**Representación base:** un atributo es un `str`, un conjunto de atributos es un `frozenset[str]` y una dependencia funcional es un par `(lado_izquierdo, lado_derecho)` de `frozenset`.

---

## 6. Fases de desarrollo

| Fase | Contenido | Criterio de cierre |
| --- | --- | --- |
| 1. Corazón del proyecto | `nucleo/`: DF, cierre, claves, formas normales, con `unittest` | 5 ejemplos de libro pasan con resultado calculado a mano |
| 2. Enlace con MySQL | `datos/`: conexión, lectura de esquema, verificador de DF | Lee una tabla real y reporta DF cumplidas o violadas |
| 3. Funcionalidades | Cobertura mínima, síntesis 3FN, descomposición BCNF, tableau y generador SQL | Una tabla plana se descompone y el SQL se ejecuta en localhost |
| 4. Interfaz gráfica | `interfaz/app_tk.py` sobre funciones ya probadas | Flujo completo sin usar consola |
| 5. Pruebas de extremo a extremo | Ida y vuelta, casos límite, errores (servidor apagado, DF mal escrita) | El join de las partes reproduce exactamente las filas originales |
| 6. Empaquetado y entrega | PyInstaller, README final, prueba en equipo limpio | El `.exe` y el script corren en otra máquina |

**Alcance mínimo seguro:** fases 1 y 2, formas normales hasta BCNF, diseñador de tablas, datos sintéticos y verificación de DF.
**Alcance completo:** cobertura mínima, síntesis 3FN, descomposición BCNF con tableau y SQL de migración.
**Extras:** inyección de violaciones, descubrimiento de DF, grafo de dependencias.

---

## 7. Funcionalidades

1. Conectar a MySQL local y listar tablas y columnas.
2. Declarar o editar dependencias funcionales.
3. Calcular cierre de atributos, claves candidatas y cobertura mínima.
4. Detectar 1FN, 2FN, 3FN y BCNF por tabla.
5. Proponer descomposición (3FN por síntesis, BCNF por división) y verificar si es sin pérdida.
6. Generar y ejecutar el SQL de migración.
7. Verificar con datos reales si una DF se cumple y mostrar las filas conflictivas.
8. Casos SQL: cargar esquemas predefinidos desde scripts y corregirlos según DF declaradas.

---

## 8. Caso de demostración

Tabla plana `pedidos_planos`:

`(id_pedido, id_cliente, nombre_cliente, ciudad_cliente, id_producto, nombre_producto, precio, cantidad)`

DF declaradas:

```text
id_cliente -> nombre_cliente, ciudad_cliente
id_producto -> nombre_producto, precio
id_pedido -> id_cliente
id_pedido, id_producto -> cantidad
```

Resultado esperado: el programa detecta que no cumple 2FN y propone `clientes`, `productos`, `pedidos` y `detalle_pedido`, con join sin pérdida verificado.

---

## 9. Fundamento teórico (resumen)

Conjuntos y retículo de subconjuntos, bases de datos relacionales, relaciones, funciones y formas normales. El desarrollo completo está en `docs/`.

---

## 10. Solución de problemas

| Problema | Causa probable | Solución |
| --- | --- | --- |
| `Can't connect to MySQL server` | Servicio apagado o puerto distinto | Iniciar el servicio y revisar `DB_PORT` |
| `Access denied for user` | Usuario o clave incorrectos | Revisar variables de entorno y el script SQL |
| `ModuleNotFoundError: mysql` | Dependencias sin instalar | Activar el entorno virtual y `pip install -r requirements.txt` |
| `No module named tkinter` (Linux) | Falta el paquete | `sudo apt install python3-tk` |
| El `.exe` no abre | Antivirus o falta de recursos | Probar sin `--onefile` y revisar la consola |

---

## 11. Entregables de la Actividad No 10 (No realizar)

- Código fuente y ejecutable (este repositorio y `dist/`).
- `docs/manual_usuario.pdf`
- `docs/informe_final.pdf`
- `docs/sustentacion.pptx`

---

## 12. Referencias

Se listan en el informe final (sección Bibliografía).

## 13. Consideraciones

No se implementa el lenguaje de programación Java.