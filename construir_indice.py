"""Construye el indice de busqueda (embeddings + FAISS) de forma offline.

Se ejecuta una sola vez tras actualizar el dataset de marcas. El calculo de
embeddings sobre el universo completo toma varios minutos; cada consulta
posterior tiene costo marginal cero.

Uso:
    python construir_indice.py
"""
from __future__ import annotations

import logging
import sys

from buscador import config, indice


def _configurar_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> int:
    _configurar_logging()
    try:
        stats = indice.construir_indice()
    except FileNotFoundError as error:
        logging.getLogger(__name__).error(
            "Falta el dataset de marcas. Corre primero 'python construir_datos.py'. %s",
            error,
        )
        return 1

    print("\nIndice construido")
    print("-" * 42)
    print(f"Marcas indexadas    : {stats['marcas']:,}")
    print(f"Dimension embedding : {stats['dimension']}")
    print(f"\nArtefactos:")
    print(f"  {config.INDICE_FAISS}")
    print(f"  {config.INDICE_META}")
    return 0


if __name__ == "__main__":
    sys.exit(main())