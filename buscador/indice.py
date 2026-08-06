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
  4. (fix 06-ago-2026 PM) Precalcular, por clase NCL, la frecuencia de cada
     palabra (por su lema, ver normalizacion.lema) entre las marcas de esa
     clase. Esto reemplaza la deteccion de "palabra generica" por
     coincidencia exacta o de lema ENTRE LAS DOS MARCAS COMPARADAS (usada
     hasta ahora en busqueda.py) por una basada en que tan descriptiva es
     esa palabra para el rubro real del candidato: una palabra que aparece
     en una fraccion alta de las marcas de una clase (ej. "cerveza" en la
     clase 32) es objetivamente generica en ese rubro, sin necesidad de que
     la consulta la comparta letra por letra.

     Se condiciona por clase, no de forma global, porque una frecuencia
     global confunde "palabra generica del rubro" con "palabra comun del
     espanol" que se repite en nombres de marca de clases muy distintas sin
     ser descriptiva de ningun producto o servicio en particular (ej. "sur",
     que en el universo completo aparece en cientos de marcas de clases tan
     distintas como alimentos, transporte y servicios financieros, pero
     dentro de cualquier clase especifica no supera el 0.7% de las marcas de
     esa clase). Ver FrecuenciasPalabras y su uso en busqueda.py.
"""
from __future__ import annotations

import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from . import config, normalizacion

logger = logging.getLogger(__name__)

__all__ = ["IndiceBusqueda", "FrecuenciasPalabras"]


def _fonetico_por_palabra(nombre: str) -> str:
    """Clave fonetica de cada palabra del nombre, por separado, unidas con
    espacio (a diferencia de normalizacion.clave_fonetica(nombre completo),
    que fusiona todas las palabras en un solo bloque sin espacios). Se
    necesita esta version con limites de palabra preservados para poder
    construir la frecuencia de cada palabra fonetica por clase (ver
    FrecuenciasPalabras); normalizacion.clave_fonetica() por si sola no
    sirve para esto porque no distingue donde termina cada palabra.
    """
    return " ".join(normalizacion.clave_fonetica(w) for w in normalizacion.limpiar(nombre).split())


def _preparar_representaciones(marcas: pd.DataFrame) -> pd.DataFrame:
    """Agrega las columnas canonica y fonetica derivadas del nombre."""
    df = marcas.copy()
    df["canonico"] = df["nombre"].map(normalizacion.limpiar)
    df["canonico_ordenado"] = df["canonico"].map(normalizacion.ordenar_tokens)
    df["fonetico"] = df["nombre"].map(normalizacion.clave_fonetica)
    df["fonetico_palabras"] = df["nombre"].map(_fonetico_por_palabra)
    return df


@dataclass(frozen=True)
class FrecuenciasPalabras:
    """Frecuencia de cada lema de palabra, por clase NCL, en el universo de
    marcas oponibles. Ver el punto 4 del docstring del modulo.

    conteo_por_clase[clase][lema] = numero de marcas de esa clase que tienen
    una palabra con ese lema. total_por_clase[clase] = numero de marcas
    (distintas) de esa clase.
    """
    conteo_por_clase: dict[int, dict[str, int]] = field(default_factory=dict)
    total_por_clase: dict[int, int] = field(default_factory=dict)

    def es_generica(self, palabra: str, clases: list[int] | None) -> bool:
        """True si `palabra` es generica/descriptiva para AL MENOS UNA de
        las clases dadas: aparece en al menos config.CONTEO_MINIMO_GENERICO
        marcas de esa clase, Y en una fraccion de esa clase mayor o igual a
        config.UMBRAL_FRECUENCIA_GENERICO. Basta con que sea generica en una
        sola clase relevante (no en todas) para considerarla generica en
        esta comparacion, igual que en la doctrina marcaria basta con que un
        termino sea descriptivo de UNO de los productos o servicios en
        juego para debilitar su aporte a la distintividad de la marca.

        El piso de conteo minimo evita que una clase con pocas marcas totales
        produzca porcentajes ruidosos (ej. 1 palabra repetida 3 veces en una
        clase de 50 marcas ya es 6%, sin que eso signifique nada).
        """
        if clases is None or len(clases) == 0:
            return False  # len(), no 'not clases': clases puede ser un array de numpy
        lema = normalizacion.lema(palabra)
        for clase in clases:
            total = self.total_por_clase.get(int(clase), 0)
            if total <= 0:
                continue
            conteo = self.conteo_por_clase.get(int(clase), {}).get(lema, 0)
            if conteo < config.CONTEO_MINIMO_GENERICO:
                continue
            if conteo / total >= config.UMBRAL_FRECUENCIA_GENERICO:
                return True
        return False


def _construir_frecuencias(marcas: pd.DataFrame, columna_texto: str) -> FrecuenciasPalabras:
    """Calcula FrecuenciasPalabras a partir de una columna de texto ya
    normalizada (canonico u.foneticas por palabra) y la columna 'clases'.
    """
    conteo_por_clase: dict[int, Counter] = defaultdict(Counter)
    total_por_clase: Counter = Counter()

    for texto, clases in zip(marcas[columna_texto], marcas["clases"]):
        lemas_unicos = {normalizacion.lema(w) for w in texto.split()}
        clases_unicas = {int(c) for c in clases}
        for clase in clases_unicas:
            total_por_clase[clase] += 1
            for lema in lemas_unicos:
                conteo_por_clase[clase][lema] += 1

    return FrecuenciasPalabras(
        conteo_por_clase={c: dict(cnt) for c, cnt in conteo_por_clase.items()},
        total_por_clase=dict(total_por_clase),
    )


class IndiceBusqueda:
    """Universo de marcas oponibles cargado en memoria, listo para consultas.

    Se instancia una vez (p. ej. al arrancar la API) y se reutiliza en cada
    consulta. Ya no depende de FAISS ni de un modelo de embeddings: solo
    carga el parquet de marcas y precalcula sus representaciones canonica y
    fonetica, ademas de las tablas de frecuencia por clase (fix 06-ago-2026
    PM, ver FrecuenciasPalabras) que usa busqueda.py para decidir que
    palabras son genericas/descriptivas de un rubro.
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
        # Version con las palabras ya ordenadas alfabeticamente: la necesita
        # el prefiltro vectorizado (MotorBusqueda.buscar()) para calcular
        # Jaro-Winkler con la misma tolerancia al reordenamiento de palabras
        # que token_sort_ratio ya tiene incorporada (ver
        # normalizacion.ordenar_tokens). Precalculada aqui, no en cada
        # consulta, por el mismo motivo que canonico/fonetico.
        self.canonicos_ordenados: list[str] = marcas["canonico_ordenado"].tolist()
        self.foneticos: list[str] = marcas["fonetico"].tolist()
        self.clases: list[list[int]] = marcas["clases"].tolist()
        self.solicitudes: list[list[str]] = marcas["solicitudes"].tolist()

        # Frecuencia de cada palabra (por lema) por clase NCL: una tabla
        # para palabras ortograficas (canonico) y otra para palabras
        # foneticas (fonetico_palabras, con limites de palabra preservados).
        # Se calculan una sola vez aqui, no en cada consulta.
        self.frecuencias_ortograficas: FrecuenciasPalabras = _construir_frecuencias(
            marcas, "canonico",
        )
        self.frecuencias_foneticas: FrecuenciasPalabras = _construir_frecuencias(
            marcas, "fonetico_palabras",
        )

        logger.info("Universo cargado: %d marcas oponibles.", len(self.mark_codes))

    def __len__(self) -> int:
        return len(self.mark_codes)