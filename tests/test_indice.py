"""Tests de indice.py, en particular FrecuenciasPalabras y su construccion
(fix 06-ago-2026 PM). No requieren el parquet real: se construye un
DataFrame pequeno en memoria con la misma forma que produce
_preparar_representaciones().
"""
from __future__ import annotations

import pandas as pd

from buscador.indice import FrecuenciasPalabras, _construir_frecuencias


def _marcas_de_prueba() -> pd.DataFrame:
    filas = [
        {"nombre": "CERVEZA TRIBAL", "clases": [32]},
        {"nombre": "CERVEZA DEL SUR", "clases": [32]},
        {"nombre": "CERVEZA ARTESANAL LOS ANDES", "clases": [32]},
        {"nombre": "SOLGAR VITAMINAS", "clases": [5]},
        {"nombre": "SOLKA SUPLEMENTOS", "clases": [5]},
    ]
    df = pd.DataFrame(filas)
    df["canonico"] = df["nombre"].str.lower()
    return df


def test_construir_frecuencias_cuenta_por_clase_no_globalmente():
    marcas = _marcas_de_prueba()
    frecuencias = _construir_frecuencias(marcas, "canonico")

    assert frecuencias.total_por_clase[32] == 3
    assert frecuencias.total_por_clase[5] == 2
    assert frecuencias.conteo_por_clase[32]["cerveza"] == 3
    # "cerveza" no aparece en absoluto en la clase 5: no debe figurar ahi.
    assert "cerveza" not in frecuencias.conteo_por_clase.get(5, {})


def test_construir_frecuencias_usa_lema_no_cadena_exacta():
    # "cerveza"/"cervezas" ya vienen singularizadas por normalizacion.lema()
    # antes de contar, asi que un plural cuenta para el mismo lema.
    marcas = pd.DataFrame([
        {"nombre": "cervezas ricas", "canonico": "cervezas ricas", "clases": [32]},
        {"nombre": "cerveza fina", "canonico": "cerveza fina", "clases": [32]},
    ])
    frecuencias = _construir_frecuencias(marcas, "canonico")
    assert frecuencias.conteo_por_clase[32]["cerveza"] == 2


def test_es_generica_requiere_superar_umbral_y_piso_de_conteo():
    frecuencias = FrecuenciasPalabras(
        conteo_por_clase={32: {"cerveza": 50}, 5: {"cerveza": 1}},
        total_por_clase={32: 100, 5: 100},
    )
    assert frecuencias.es_generica("cerveza", [32]) is True
    # Mismo lema, pero en la clase 5 no supera config.CONTEO_MINIMO_GENERICO.
    assert frecuencias.es_generica("cerveza", [5]) is False
    # Basta con que sea generica en UNA de las clases del candidato.
    assert frecuencias.es_generica("cerveza", [5, 32]) is True


def test_es_generica_sin_clases_devuelve_false():
    frecuencias = FrecuenciasPalabras(
        conteo_por_clase={32: {"cerveza": 50}},
        total_por_clase={32: 100},
    )
    assert frecuencias.es_generica("cerveza", None) is False
    assert frecuencias.es_generica("cerveza", []) is False