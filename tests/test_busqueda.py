"""Tests del motor de busqueda.

Se usa un doble de IndiceBusqueda que expone listas fijas de candidatos, de
modo que los tests verifican la logica de combinacion de senales y
modulacion por clase sin depender del parquet real de 218k marcas.

Nota (julio 2026): este doble se actualizo para reflejar la interfaz real
de IndiceBusqueda (listas planas: mark_codes, nombres, canonicos, foneticos,
clases, solicitudes) tras la migracion del motor a rapidfuzz.process.cdist.
La version anterior modelaba un IndiceBusqueda de la era FAISS/embeddings
(atributo .meta como DataFrame, metodo candidatos_semanticos()) que ya no
existe en el codigo de produccion.
"""
from __future__ import annotations

import random

import pytest
from rapidfuzz import fuzz

from buscador import config, normalizacion
from buscador.busqueda import MotorBusqueda
from buscador.busqueda import _similitud_fonetica
from buscador.busqueda import _similitud_ortografica


class IndiceFalso:
    """Doble de IndiceBusqueda: listas planas fijas, sin parquet ni cdist real.

    El parametro sim_semantica se mantiene por compatibilidad con las firmas
    de tests existentes, pero ya no tiene efecto: la senal semantica fue
    retirada del motor en julio 2026 (ver busqueda.py).
    """

    def __init__(self, marcas: list[dict], sim_semantica: float = 0.5):
        del sim_semantica  # ya no se usa; ver docstring de la clase.
        self.mark_codes: list[int] = [m["mark_code"] for m in marcas]
        self.nombres: list[str] = [m["nombre"] for m in marcas]
        self.canonicos: list[str] = [normalizacion.limpiar(m["nombre"]) for m in marcas]
        self.foneticos: list[str] = [normalizacion.clave_fonetica(m["nombre"]) for m in marcas]
        self.clases: list[list[int]] = [m["clases"] for m in marcas]
        self.solicitudes: list[list[str]] = [m.get("solicitudes", []) for m in marcas]

    def __len__(self) -> int:
        return len(self.mark_codes)


def test_marca_identica_obtiene_score_alto():
    indice = IndiceFalso([
        {"mark_code": 1, "nombre": "CHALLENGER", "clases": [34]},
        {"mark_code": 2, "nombre": "ZAPATILLAS VELOZ", "clases": [25]},
    ])
    motor = MotorBusqueda(indice)
    resultados = motor.buscar("CHALLENGER", clases_consulta=[34])

    assert resultados[0].mark_code == 1
    assert resultados[0].score_ortografico == 100.0
    assert resultados[0].score > resultados[1].score


def test_contencion_de_palabra_la_atrapa_la_senal_ortografica():
    # CHALLENGER vs CHALLENGER LIGHTS: el embedding solo falla aqui (~0.36),
    # pero la senal ortografica la rescata.
    indice = IndiceFalso([
        {"mark_code": 1, "nombre": "CHALLENGER LIGHTS", "clases": [34]},
    ], sim_semantica=0.36)
    motor = MotorBusqueda(indice)
    r = motor.buscar("CHALLENGER", clases_consulta=[34])[0]
    assert r.score_ortografico > 60.0


def test_homofono_lo_atrapa_la_senal_fonetica():
    indice = IndiceFalso([
        {"mark_code": 1, "nombre": "KAUKENES", "clases": [33]},
    ], sim_semantica=0.4)
    motor = MotorBusqueda(indice)
    r = motor.buscar("CAUQUENES", clases_consulta=[33])[0]
    assert r.score_fonetico == 100.0


def test_clase_no_relacionada_atenua_el_score():
    indice = IndiceFalso([
        {"mark_code": 1, "nombre": "OMEGA", "clases": [14]},
    ])
    motor = MotorBusqueda(indice)
    misma = motor.buscar("OMEGA", clases_consulta=[14])[0]
    distinta = motor.buscar("OMEGA", clases_consulta=[25])[0]

    assert misma.clase_relacionada is True
    assert distinta.clase_relacionada is False
    assert distinta.score < misma.score


def test_sin_clases_consulta_no_penaliza():
    indice = IndiceFalso([{"mark_code": 1, "nombre": "OMEGA", "clases": [14]}])
    motor = MotorBusqueda(indice)
    r = motor.buscar("OMEGA")[0]
    assert r.clase_relacionada is True


def test_resultados_ordenados_por_score_desc():
    indice = IndiceFalso([
        {"mark_code": 1, "nombre": "SOLYMAR", "clases": [25]},
        {"mark_code": 2, "nombre": "SOL Y MAR", "clases": [25]},
        {"mark_code": 3, "nombre": "TOTALMENTE DISTINTA", "clases": [25]},
    ])
    motor = MotorBusqueda(indice)
    resultados = motor.buscar("SOLYMAR", clases_consulta=[25])
    scores = [r.score for r in resultados]
    assert scores == sorted(scores, reverse=True)



def test_palabra_generica_compartida_no_infla_el_score():
    # SKAAL vs SVAJG no se parecen; compartir "BEER" no deberia salvarlos.
    s_con = _similitud_ortografica("skaal beer", "svajg beer")
    s_sin = _similitud_ortografica("skaal", "svajg")
    assert s_con == pytest.approx(s_sin, abs=0.5)


def test_subconjunto_casi_exacto_no_se_castiga():
    # "SKAAL BEER" vs "SKAAL": quitar la comun deja una cadena vacia,
    # no debe caer a 0.
    s = _similitud_ortografica("skaal beer", "skaal")
    assert s > 50.0


def test_una_sola_palabra_no_se_descuenta():
    s = _similitud_ortografica("omega", "omega")
    assert s == 100.0


def test_reordenamiento_se_mantiene_alto():
    s = _similitud_ortografica("casa blanca", "blanca casa")
    assert s == 100.0

def test_palabra_generica_fonetica_no_infla_el_score():
    s_con = _similitud_fonetica("skaal beer", "svajg beer")
    s_sin = _similitud_fonetica("skaal", "svajg")
    assert s_con == pytest.approx(s_sin, abs=1.0)


def test_subconjunto_fonetico_no_se_castiga():
    s = _similitud_fonetica("skaal beer", "skaal")
    assert s > 50.0


def test_homofono_sigue_dando_score_alto():
    assert _similitud_fonetica("cauquenes", "kaukenes") == 100.0


def test_similitud_fonetica_nunca_supera_el_score_bruto():
    """El descuento de palabras comunes no puede subir el score por encima
    del que calcularia cdist sobre el texto completo (sin descuento).

    Este es el invariante del que depende el prefiltro de dos etapas en
    MotorBusqueda.buscar(): si _similitud_fonetica pudiera superar el score
    bruto, un candidato real podria quedar fuera del top-N del prefiltro y
    nunca llegar al recalculo exacto (bug corregido el 03-ago-2026, antes
    de este fix la funcion no aplicaba min() como si hace
    _similitud_ortografica). Se prueba con pares generados al azar (mezcla
    de palabras y letras) para no depender solo de los ejemplos de mano
    usados en los demas tests.
    """
    random.seed(0)
    letras = "abcdefghijklmnopqrstuvwxyz"
    palabras_base = ["beer", "chile", "casa", "blanca", "sol", "mar", "kids"]

    def marca_al_azar():
        n_palabras = random.randint(1, 3)
        palabras = []
        for _ in range(n_palabras):
            if random.random() < 0.5:
                palabras.append(random.choice(palabras_base))
            else:
                largo = random.randint(3, 8)
                palabras.append("".join(random.choice(letras) for _ in range(largo)))
        return " ".join(palabras)

    for _ in range(200):
        a, b = marca_al_azar(), marca_al_azar()
        score_bruto = float(fuzz.ratio(
            normalizacion.clave_fonetica(a), normalizacion.clave_fonetica(b),
        ))
        score_exacto = _similitud_fonetica(a, b)
        assert score_exacto <= score_bruto + 1e-9, (a, b, score_exacto, score_bruto)


def test_prefiltro_no_pierde_una_anterioridad_clara_en_universo_grande():
    """El motor debe seguir encontrando un match evidente aunque el universo
    supere config.CANDIDATOS_PREFILTRO, ejercitando de verdad la rama de
    prefiltro vectorizado + recalculo exacto (argpartition), que los demas
    tests de este archivo nunca activan por usar universos chicos.
    """
    random.seed(1)
    letras = "abcdefghijklmnopqrstuvwxyz"

    def ruido_al_azar():
        largo = random.randint(4, 10)
        return "".join(random.choice(letras) for _ in range(largo)).upper()

    n_ruido = config.CANDIDATOS_PREFILTRO * 3
    marcas = [
        {"mark_code": i + 1, "nombre": ruido_al_azar(), "clases": [25]}
        for i in range(n_ruido)
    ]
    marcas.append({"mark_code": 999, "nombre": "CAUQUENES", "clases": [33]})

    indice = IndiceFalso(marcas)
    motor = MotorBusqueda(indice)
    resultados = motor.buscar("KAUKENES", clases_consulta=[33], top=5)

    assert any(r.mark_code == 999 for r in resultados)