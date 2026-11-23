# Fase 6: empaquetado y entrega

Esta fase está en curso. La fase 5 se registra como completada según la
confirmación del equipo.

## Preparar versiones reproducibles

Usa un entorno limpio con Python 3.11 o superior. Instala únicamente las
dependencias necesarias para ejecutar y empaquetar la aplicación, revisa sus
versiones y congela la salida de `pip freeze` en `requirements.txt`. Tkinter
pertenece a Python; MySQL Server se instala por separado.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install mysql-connector-python pyinstaller
python --version
python -m pip freeze
```

No rellenes las versiones con valores supuestos: deben corresponder al
entorno que se usó para compilar y probar el ejecutable.

## Ejecutar la compilación

Cuando `requirements.txt` tenga las versiones exactas y estén instaladas en
`.venv`, ejecuta:

```powershell
.\scripts\build_release.ps1
```

El script comprueba Python, Tkinter, el conector MySQL y PyInstaller. El
ejecutable se guarda en `docs/release/dist/NormalizadorBD.exe`.

## Lista de comprobación en un equipo limpio

- Instalar MySQL Server 8.x y preparar la base `pruebas`.
- Copiar el ejecutable; no instalar Python en el equipo de verificación.
- Abrirlo y conectar usando el host, puerto, usuario y base correctos.
- Cargar los cinco casos, analizar y dibujar/aplicar sus propuestas.
- Verificar una conexión fallida y confirmar que la aplicación muestra el error.
- Guardar capturas del análisis, la propuesta y la conexión para el manual.
- No mostrar contraseñas en capturas ni incluirlas en el repositorio.

## Respaldo para la sustentación

Guardar en `docs/` capturas del flujo completo y un video corto de la
demostración. Tener a mano las consultas y resultados de los casos por si el
servicio MySQL no inicia durante la presentación.

## Cierre y versión

Después de que la compilación y la prueba en el equipo limpio pasen, actualizar
el README con las versiones realmente usadas y crear la etiqueta local `v1.0`.
No marcar esta fase como completa hasta verificar esos pasos.

## Estado de este entorno

No se pudo compilar aquí: Windows no tiene un intérprete Python funcional y
`.venv` apunta a una instalación base que no está disponible. `requirements.txt`
está vacío, así que no hay versiones verificadas que congelar todavía. El
script de compilación queda preparado para ejecutarse cuando se restaure
Python y se fijen las dependencias.
