"""Validacion de recall del buscador contra rechazos reales de Art. 20 h).

Mide que tan bien el motor recupera las anterioridades que los examinadores
citaron efectivamente al rechazar solicitudes por la causal h) en 2025.

Metodologia
-----------
Para cada observacion M10 de 2025 con anterioridad identificable:
  1. Se toma el nombre de la solicitud rechazada (recuperado desde la base de
     marcas via solicitud_base) y sus clases.
  2. Se ejecuta el buscador sobre ese nombre.
  3. Se considera ACIERTO si alguna de las anterioridades citadas por el
     examinador aparece en los top-N resultados del buscador.

El recall resultante es una cota INFERIOR del desempeno real: solo se evaluan
los casos cuya anterioridad citada esta presente en la base de marcas del MVP
(~69%); las anterioridades en tramite no registradas requieren SQL Server y
quedan fuera de esta medicion, documentadas como limitacion conocida.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import pandas as pd

from . import config
from .busqueda import MotorBusqueda

logger = logging.getLogger(__name__)

__all__ = ["CasoValidacion", "ResultadoValidacion", "preparar_casos", "evaluar"]

_PATRON_REGISTRO = re.compile(r"[Rr]egistro[^\d]{0,15}0*(\d{5,8})")


@dataclass(frozen=True)
class CasoValidacion:
    """Un caso de prueba: una solicitud rechazada y sus anterioridades."""
    file_nbr: int
    nombre_solicitud: str
    clases: list[int]
    anterioridades_base: set[int]   # solicitud_base de las anterioridades citadas


@dataclass(frozen=True)
class ResultadoValidacion:
    """Metricas agregadas de la evaluacion."""
    casos_totales: int
    aciertos: dict[int, int]        # top_n -> numero de aciertos
    recall: dict[int, float]        # top_n -> recall

    def resumen(self) -> str:
        lineas = [f"Casos evaluados: {self.casos_totales}", "-" * 32]
        for n in sorted(self.recall):
            lineas.append(
                f"Recall@{n:<3}: {self.recall[n]*100:5.1f}%  "
                f"({self.aciertos[n]}/{self.casos_totales})"
            )
        return "\n".join(lineas)


def _registros_citados(texto: str) -> set[int]:
    if not isinstance(texto, str):
        return set()
    return {int(x) for x in _PATRON_REGISTRO.findall(texto)}


def preparar_casos(
    obs_parquet_o_xlsx,
    marcas,
) -> list[CasoValidacion]:
    """Construye los casos de validacion cruzando observaciones y marcas.

    Args:
        obs_parquet_o_xlsx: ruta al archivo de observaciones parseadas.
        marcas: DataFrame de marcas agrupadas (con columnas mark_code, nombre,
            clases, solicitudes).

    Returns:
        Lista de CasoValidacion con anterioridad presente en la base.
    """
    obs = pd.read_excel(obs_parquet_o_xlsx)
    obs.columns = obs.columns.str.strip()
    m10 = obs[obs["modulo"] == "M10"].copy()

    # Mapa solicitud_base -> (nombre, clases) desde las marcas agrupadas.
    nombre_por_base: dict[int, str] = {}
    clases_por_base: dict[int, list[int]] = {}
    for _, fila in marcas.iterrows():
        for s in fila["solicitudes"]:
            nombre_por_base[int(s)] = fila["nombre"]
            clases_por_base[int(s)] = [int(c) for c in fila["clases"]]

    # Universo de solicitudes_base presentes en la base (para filtrar citas).
    bases_presentes = set(nombre_por_base.keys())

    casos: list[CasoValidacion] = []
    for _, fila in m10.iterrows():
        file_nbr = int(fila["File_Nbr"])
        nombre = nombre_por_base.get(file_nbr)
        if nombre is None:
            continue  # no recuperamos el nombre de la solicitud
        citados = _registros_citados(fila["texto_observacion"])
        anterioridades = citados & bases_presentes
        if not anterioridades:
            continue  # ninguna anterioridad citada esta en la base
        casos.append(CasoValidacion(
            file_nbr=file_nbr,
            nombre_solicitud=nombre,
            clases=clases_por_base.get(file_nbr, []),
            anterioridades_base=anterioridades,
        ))
    logger.info("Casos de validacion preparados: %d", len(casos))
    return casos


def evaluar(
    casos: list[CasoValidacion],
    motor: MotorBusqueda,
    tops: tuple[int, ...] = (1, 3, 5, 10),
) -> ResultadoValidacion:
    """Evalua el recall del motor sobre los casos.

    Un caso es acierto en top-N si alguna anterioridad citada aparece, por su
    solicitud_base, entre los N primeros resultados del buscador.
    """
    max_top = max(tops)
    aciertos = {n: 0 for n in tops}

    for i, caso in enumerate(casos, 1):
        resultados = motor.buscar(
            caso.nombre_solicitud,
            clases_consulta=caso.clases,
            top=max_top,
        )
        # solicitud_base de cada resultado (un resultado puede tener varias).
        bases_por_rank = [
            {int(s) for s in r.solicitudes} for r in resultados
        ]
        for n in tops:
            encontrado = any(
                caso.anterioridades_base & bases
                for bases in bases_por_rank[:n]
            )
            if encontrado:
                aciertos[n] += 1
        if i % 500 == 0:
            logger.info("Evaluados %d/%d casos", i, len(casos))

    total = len(casos)
    recall = {n: (aciertos[n] / total if total else 0.0) for n in tops}
    return ResultadoValidacion(casos_totales=total, aciertos=aciertos, recall=recall)