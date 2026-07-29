"""Evalua el recall del buscador contra los rechazos M10 de 2025.

Uso:
    python validar.py
"""
from __future__ import annotations

import logging
import sys

import pandas as pd

from buscador import config, validacion
from buscador.busqueda import MotorBusqueda
from buscador.indice import IndiceBusqueda

OBSERVACIONES = config.DATA_DIR / "observaciones_2025_parseadas.xlsx"


def _configurar_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> int:
    _configurar_logging()
    log = logging.getLogger(__name__)

    if not OBSERVACIONES.exists():
        log.error("No se encontro %s", OBSERVACIONES)
        return 1

    marcas = pd.read_parquet(config.MARCAS_PROCESADAS)
    casos = validacion.preparar_casos(OBSERVACIONES, marcas)
    if not casos:
        log.error("No se prepararon casos de validacion.")
        return 1

    log.info("Cargando indice y motor...")
    motor = MotorBusqueda(IndiceBusqueda())

    log.info("Evaluando %d casos...", len(casos))
    resultado = validacion.evaluar(casos, motor)

    print("\n" + "=" * 40)
    print("VALIDACION DE RECALL - Art. 20 h) 2025")
    print("=" * 40)
    print(resultado.resumen())
    print("\nNota: recall medido solo sobre casos cuya anterioridad esta en la")
    print("base del MVP. Anterioridades en tramite (no registradas) requieren")
    print("SQL Server y no se evaluan aqui.")
    return 0


if __name__ == "__main__":
    sys.exit(main())