"""Construye el dataset de marcas oponibles desde el Excel de INAPI.

Punto de entrada del pipeline de datos. Configura el logging de la aplicacion
y reporta el resumen del procesamiento.

Uso:
    python construir_datos.py
"""
from __future__ import annotations

import logging
import sys

from buscador import config, datos


def _configurar_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> int:
    _configurar_logging()
    try:
        marcas, stats = datos.construir()
    except (FileNotFoundError, datos.DatosInvalidosError) as error:
        logging.getLogger(__name__).error("No se pudo construir el dataset: %s", error)
        return 1

    print("\nResumen del procesamiento")
    print("-" * 42)
    print(f"Filas en el Excel original   : {stats['filas_crudas']:,}")
    print(f"Filas fuera de patron de clase: {stats['solicitud_base_sin_patron']:,}")
    print(f"Filas oponibles (Registrada) : {stats['filas_oponibles']:,}")
    print(f"Marcas unicas (Mark Code)    : {stats['marcas_unicas']:,}")

    datos.guardar(marcas)

    print(f"\nGuardado en: {config.MARCAS_PROCESADAS}")
    print("\nPrimeras filas:")
    print(marcas.head(10).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())