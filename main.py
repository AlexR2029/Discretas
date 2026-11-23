"""Punto de entrada de la interfaz gráfica NormalizadorBD."""

from gui.app_tk import ejecutar_aplicacion


def main() -> None:
    """Inicia la aplicación Tkinter.

    parámetros: ninguno.
    retorno: None.
    complejidad: O(1) para iniciar el bucle gráfico; las operaciones posteriores
    dependen de las pestañas y del servidor MySQL.
    """
    ejecutar_aplicacion()


if __name__ == "__main__":
    main()