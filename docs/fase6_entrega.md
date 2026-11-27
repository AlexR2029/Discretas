# Fase 6: empaquetado y entrega

Esta fase está en curso. La fase 5 se registra como completada según la
confirmación del equipo.

## Entorno de compilación

El entorno aislado `.venv\release_build` usa Python 3.13.12. Las versiones
exactas de las dependencias están guardadas en
`docs/release/requirements.lock.txt`. Tkinter se incluye con Python; MySQL
Server debe instalarse y estar iniciado por separado.

## Generar el ejecutable

Desde la raíz del proyecto, ejecuta:

```powershell
.\scripts\build_release.ps1
```

El script revisa Python, Tkinter, Connector/Python y PyInstaller. El archivo
resultante se guarda en `docs/release/dist/NormalizadorBD.exe`.

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

Después de probar el ejecutable en un equipo limpio, actualizar el README con
las versiones realmente usadas y crear la etiqueta local `v1.0`. La compilación
y la prueba limpia son pasos separados; el segundo requiere un Windows limpio
con MySQL configurado.

