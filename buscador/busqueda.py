"""Motor de busqueda de anterioridades por similitud denominativa.

Dada una denominacion consultada, se compara contra el UNIVERSO COMPLETO de
marcas oponibles combinando dos senales:

  - ortografica (rapidfuzz sobre la forma canonica)
  - fonetica    (rapidfuzz sobre la clave fonetica espanol-Chile)

Decision de julio 2026: se retiro la senal semantica del motor (embeddings +
FAISS) por decision de negocio.

Migracion a cdist (julio 2026, produccion con universo completo): el primer
diseno post-FAISS comparaba la consulta contra las ~218.369 marcas con un
loop puro en Python (uno por candidato), lo que tomaba ~13s por consulta.
Se migro a una estrategia en dos pasos, vectorizada con
rapidfuzz.process.cdist (implementado en C++):

  1. Prefiltro bruto: cdist calcula scores ortografico y fonetico SIN el
     descuento de palabras genericas contra el universo completo en un solo
     llamado vectorizado, y se toman los config.CANDIDATOS_PREFILTRO mejores
     candidatos por score combinado bruto.
  2. Recalculo exacto: solo sobre ese top-N (no sobre las 218.369 marcas) se
     aplica la logica exacta con descuento de genericos y el factor de
     clase NCL, y se ordena para devolver el top final.

Esta division es segura porque descontar palabras genericas solo puede
REDUCIR un score, nunca subirlo: el ranking bruto del paso 1 es un
superconjunto del ranking final del paso 2 para un N suficientemente
holgado. Ver MotorBusqueda para el detalle de implementacion.

El score combinado se atenua cuando la marca consultada y la candidata no
comparten ninguna clase NCL, reflejando el menor riesgo de confusion entre
productos o servicios no relacionados (Art. 20 h).

Fix 17-jul-2026: _similitud_fonetica() recibe el texto CRUDO de cada
denominacion (no la clave fonetica ya fusionada) porque internamente hace
texto_a.split() para descontar palabras foneticamente comunes palabra por
palabra. clave_fonetica() elimina los espacios (funde toda la denominacion
en un solo bloque, ver normalizacion.py), asi que pasarle la clave ya
calculada dejaba a texto_a como una sola "palabra" para toda marca
multi-palabra, y el descuento pareado del lado de la consulta nunca se
activaba correctamente. Antes: buscar() calculaba fonetico_consulta =
clave_fonetica(consulta) y se lo pasaba a _similitud_fonetica. Ahora se le
pasa consulta directamente (texto crudo); _similitud_fonetica ya calcula
clave_fonetica internamente para el score base, y usa el texto crudo solo
para el split() del descuento pareado.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
from rapidfuzz import fuzz, process

from . import config, normalizacion
from .indice import IndiceBusqueda

logger = logging.getLogger(__name__)

__all__ = ["Resultado", "MotorBusqueda"]


@dataclass(frozen=True)
class Resultado:
    """Una anterioridad candidata con su desglose de puntajes."""
    mark_code: int
    nombre: str
    clases: list[int]
    solicitudes: list[str]
    score: float                 # combinado, 0-100
    score_ortografico: float     # 0-100
    score_fonetico: float        # 0-100
    clase_relacionada: bool


def _palabras_comunes_fuera(a: str, b: str) -> tuple[str, str]:
    """Quita de cada cadena las palabras exactas que aparecen en ambas."""
    wa, wb = a.split(), b.split()
    comunes = set(wa) & set(wb)
    fa = " ".join(w for w in wa if w not in comunes)
    fb = " ".join(w for w in wb if w not in comunes)
    return fa, fb


def _similitud_ortografica(a: str, b: str) -> float:
    """Similitud ortografica 0-100 sobre formas canonicas.

    Usa token_sort_ratio como base (tolera reordenamiento de palabras, ej.
    'CASA BLANCA' / 'BLANCA CASA'). Para evitar que una palabra generica
    compartida ('BEER', 'CHILE', etc.) infle el parecido entre marcas cuyo
    elemento distintivo es en realidad muy distinto, se calcula tambien el
    score quitando las palabras exactas comunes a ambas marcas y se usa el
    minimo de los dos. Si quitar las comunes deja una cadena vacia (una
    marca es subconjunto casi exacto de la otra, ej. 'SKAAL BEER' vs
    'SKAAL'), no se aplica el castigo: se mantiene el score base.

    Limitacion conocida (aceptada, sin solucion automatica por ahora): esta
    correccion solo detecta palabras EXACTAMENTE comunes. Si el parecido
    viene de una palabra generica compartida que no es identica letra por
    letra (ej. variantes ortograficas de un mismo generico), la inflacion
    artificial del score no se corrige. Se documenta como error conocido en
    vez de intentar una heuristica adicional sin evidencia empirica de que
    sea necesaria.
    """
    if not a or not b:
        return 0.0

    score_base = float(fuzz.token_sort_ratio(a, b))

    if " " not in a and " " not in b:
        return score_base  # una sola palabra cada una: nada que descontar

    fa, fb = _palabras_comunes_fuera(a, b)
    if not fa or not fb:
        return score_base  # una marca es casi subconjunto de la otra

    score_sin_comunes = float(fuzz.token_sort_ratio(fa, fb))
    return min(score_base, score_sin_comunes)


def _similitud_fonetica(texto_a: str, texto_b: str) -> float:
    """Similitud fonetica 0-100, comparando texto original (no clave ya
    fusionada) para poder descontar palabras foneticamente comunes.

    Mismo problema que la senal ortografica: una palabra compartida (p. ej.
    'BEER' en dos marcas de cerveza) infla el ratio aunque el elemento
    distintivo de cada marca suene distinto. Se descuentan las palabras
    cuya clave fonetica es identica en ambas marcas antes de comparar.

    IMPORTANTE: texto_a y texto_b deben ser el texto CRUDO de la
    denominacion (con espacios), no el resultado de clave_fonetica(). Esta
    funcion calcula la clave fonetica internamente. Si se le pasa una clave
    ya fusionada, texto_a.split() la trata como una sola palabra y el
    descuento pareado deja de funcionar correctamente para ese lado de la
    comparacion (bug corregido el 17-jul-2026 en MotorBusqueda.buscar()).

    Al igual que en _similitud_ortografica, el resultado final es el minimo
    entre el score base y el score sin las palabras comunes. Sin este
    minimo, fuzz.ratio(fa, fb) podria en teoria superar a score_base (nada
    garantiza que acortar dos cadenas suba o baje su ratio de edicion), lo
    que rompe la invariante de la que depende MotorBusqueda.buscar() para
    su prefiltro: que el descuento de genericos nunca puede aumentar un
    score por encima del bruto calculado por cdist (bug corregido
    03-ago-2026; hasta entonces esta funcion devolvia fuzz.ratio(fa, fb)
    directamente, sin el minimo, y ese caso no estaba cubierto por tests
    porque los universos de prueba son mas chicos que
    config.CANDIDATOS_PREFILTRO).
    """
    if not texto_a or not texto_b:
        return 0.0

    clave_completa_a = normalizacion.clave_fonetica(texto_a)
    clave_completa_b = normalizacion.clave_fonetica(texto_b)
    score_base = float(fuzz.ratio(clave_completa_a, clave_completa_b))

    wa, wb = texto_a.split(), texto_b.split()
    if len(wa) <= 1 and len(wb) <= 1:
        return score_base  # una sola palabra cada lado: nada que descontar

    claves_a = [normalizacion.clave_fonetica(w) for w in wa]
    claves_b = [normalizacion.clave_fonetica(w) for w in wb]
    comunes = set(claves_a) & set(claves_b)

    fa = " ".join(c for c in claves_a if c not in comunes)
    fb = " ".join(c for c in claves_b if c not in comunes)

    if not fa or not fb:
        return score_base  # una marca es subconjunto fonetico de la otra

    score_sin_comunes = float(fuzz.ratio(fa, fb))
    return min(score_base, score_sin_comunes)


class MotorBusqueda:
    """Motor de busqueda sobre un IndiceBusqueda cargado.

    Estrategia en dos pasos (julio 2026, migracion a cdist):

    1. Prefiltro bruto vectorizado: se calcula un score ortografico y
       fonetico BRUTO (sin descuento de palabras genericas) contra el
       universo completo con rapidfuzz.process.cdist, y se toman los
       config.CANDIDATOS_PREFILTRO mejores por score combinado bruto.
    2. Recalculo exacto: sobre ese top-N (no sobre las 218.369 marcas) se
       recalculan los scores con la logica exacta de _similitud_ortografica
       y _similitud_fonetica (que incluye el descuento de genericos), se
       aplica el factor de clase NCL y se ordena para devolver el top final.

    El paso 1 es una cota superior segura del paso 2: descontar palabras
    genericas solo puede bajar un score, nunca subirlo, asi que ningun
    candidato relevante puede quedar fuera del top-N bruto para un N
    suficientemente holgado frente a config.TOP_RESULTADOS.
    """

    def __init__(self, indice: IndiceBusqueda) -> None:
        self.indice = indice

    def buscar(
        self,
        consulta: str,
        clases_consulta: list[int] | None = None,
        top: int = config.TOP_RESULTADOS,
    ) -> list[Resultado]:
        """Busca anterioridades similares a la denominacion consultada.

        Compara la consulta contra el universo COMPLETO de marcas oponibles
        cargado en self.indice, vectorizado con cdist (ver docstring de la
        clase para el detalle del prefiltro + recalculo exacto).

        Args:
            consulta: denominacion de la marca solicitada (texto crudo).
            clases_consulta: clases NCL de la solicitud; si se entregan, se usan
                para modular el score por relacion de clase.
            top: numero de resultados a devolver.

        Returns:
            Lista de Resultado ordenada por score combinado descendente.
        """
        idx = self.indice
        n = len(idx)
        if n == 0:
            return []

        canonico = normalizacion.limpiar(consulta)
        clave_fonetica_consulta = normalizacion.clave_fonetica(consulta)
        clases_consulta = clases_consulta or []
        set_clases = {int(c) for c in clases_consulta}

        # --- Paso 1: scoring bruto vectorizado (sin descuento de genericos) ---
        s_ort_bruto = process.cdist(
            [canonico], idx.canonicos, scorer=fuzz.token_sort_ratio,
        )[0]
        s_fon_bruto = process.cdist(
            [clave_fonetica_consulta], idx.foneticos, scorer=fuzz.ratio,
        )[0]

        combinado_bruto = (
            config.PESO_ORTOGRAFICO * s_ort_bruto
            + config.PESO_FONETICO * s_fon_bruto
        )

        n_prefiltro = min(config.CANDIDATOS_PREFILTRO, n)
        # argpartition es O(n): mas rapido que ordenar todo el universo cuando
        # solo necesitamos los n_prefiltro mejores, sin garantia de orden interno.
        indices_top = np.argpartition(-combinado_bruto, n_prefiltro - 1)[:n_prefiltro]

        # --- Paso 2: recalculo exacto (con descuento de genericos) sobre el top-N ---
        resultados: list[Resultado] = []
        for i in indices_top:
            i = int(i)
            cand_canonico = idx.canonicos[i]

            s_ort = _similitud_ortografica(canonico, cand_canonico)
            # Se pasa 'consulta' cruda (no clave_fonetica(consulta)): ver
            # docstring de _similitud_fonetica y nota de fix mas arriba.
            s_fon = _similitud_fonetica(consulta, idx.nombres[i])

            combinado = (
                config.PESO_ORTOGRAFICO * s_ort
                + config.PESO_FONETICO * s_fon
            )

            clases_cand = [int(c) for c in idx.clases[i]]
            relacionada = bool(set_clases & set(clases_cand)) if set_clases else True
            if set_clases and not relacionada:
                combinado *= config.FACTOR_CLASE_NO_RELACIONADA

            resultados.append(Resultado(
                mark_code=int(idx.mark_codes[i]),
                nombre=str(idx.nombres[i]),
                clases=clases_cand,
                solicitudes=list(idx.solicitudes[i]),
                score=round(combinado, 2),
                score_ortografico=round(s_ort, 2),
                score_fonetico=round(s_fon, 2),
                clase_relacionada=relacionada,
            ))

        resultados.sort(key=lambda r: r.score, reverse=True)
        return resultados[:top]