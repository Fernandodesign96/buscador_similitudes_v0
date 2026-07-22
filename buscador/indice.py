"""Carga en memoria del universo de marcas oponibles.

Ya no existe un indice vectorial (FAISS) ni un modelo de embeddings: la
recuperacion de candidatos se hace por comparacion directa (rapidfuzz)
contra el universo completo de marcas oponibles, sin filtrado previo. Ver
justificacion de esta decision en busqueda.py.

Este modulo se limita a:
  1. Leer el parquet de marcas oponibles.
  2. Precalcular una sola vez la forma canonica y la clave fonetica de cada
     marca (evita recalcularlas en cada consulta).
  3. Mantener esas representaciones en listas planas (no DataFrame) para que
     el loop de comparacion en busqueda.py no pague el overhead de pandas
     por fila.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from . import config, normalizacion

logger = logging.getLogger(__name__)

__all__ = ["IndiceBusqueda"]


def _preparar_representaciones(marcas: pd.DataFrame) -> pd.DataFrame:
    """Agrega las columnas canonica y fonetica derivadas del nombre."""
    df = marcas.copy()
    df["canonico"] = df["nombre"].map(normalizacion.limpiar)
    df["fonetico"] = df["nombre"].map(normalizacion.clave_fonetica)
    return df


class IndiceBusqueda:
    """Universo de marcas oponibles cargado en memoria, listo para consultas.

    Se instancia una vez (p. ej. al arrancar la API) y se reutiliza en cada
    consulta. Ya no depende de FAISS ni de un modelo de embeddings: solo
    carga el parquet de marcas y precalcula sus representaciones canonica y
    fonetica.
    """

    def __init__(
        self,
        marcas_parquet: Path = config.MARCAS_PROCESADAS,
    ) -> None:
        logger.info("Cargando marcas oponibles desde %s", marcas_parquet)
        marcas = pd.read_parquet(marcas_parquet)
        marcas = _preparar_representaciones(marcas)

        # Listas planas: evita el overhead de indexar un DataFrame fila a
        # fila dentro del loop de comparacion (busqueda.py itera esto en
        # cada consulta, para las ~218k marcas del universo).
        self.mark_codes: list[int] = marcas["mark_code"].tolist()
        self.nombres: list[str] = marcas["nombre"].tolist()
        self.canonicos: list[str] = marcas["canonico"].tolist()
        self.foneticos: list[str] = marcas["fonetico"].tolist()
        self.clases: list[list[int]] = marcas["clases"].tolist()
        self.solicitudes: list[list[str]] = marcas["solicitudes"].tolist()

        logger.info("Universo cargado: %d marcas oponibles.", len(self.mark_codes))

    def __len__(self) -> int:
        return len(self.mark_codes)
