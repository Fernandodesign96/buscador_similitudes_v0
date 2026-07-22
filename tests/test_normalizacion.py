"""Tests de la normalizacion de denominaciones de marca."""
from __future__ import annotations

import pytest

from buscador import normalizacion as norm


# --- limpiar() -------------------------------------------------------------

@pytest.mark.parametrize("entrada, esperado", [
    ("CHALLENGER", "challenger"),
    ("Café Niño", "cafe niño"),                    # acentos fuera, enie se conserva
    ("CES COMPAÑÍA ELECTROACÚSTICA", "ces compañia electroacustica"),
    ("SUPER-ORANGE 1000", "super orange 1000"),    # puntuacion fuera, digitos quedan
    ("  doble   espacio  ", "doble espacio"),
    ("56", "56"),
])
def test_limpiar(entrada, esperado):
    assert norm.limpiar(entrada) == esperado


@pytest.mark.parametrize("entrada", [None, "", "   ", "!!!"])
def test_limpiar_vacios(entrada):
    assert norm.limpiar(entrada) == ""


def test_limpiar_preserva_enie_distinta_de_n():
    assert norm.limpiar("PEÑA") != norm.limpiar("PENA")


# --- clave_fonetica(): homofonos producen la MISMA clave -------------------

@pytest.mark.parametrize("a, b", [
    ("cauquenes", "kaukenes"),   # caso emblematico (jurisprudencia M06)
    ("casa", "kasa"),            # c dura = k
    ("queso", "keso"),           # qu = k
    ("cebra", "sebra"),          # seseo c/s
    ("zapato", "sapato"),        # seseo z/s
    ("gente", "jente"),          # g suave = jota
    ("gira", "jira"),
    ("llave", "yave"),           # yeismo
    ("baca", "vaca"),            # b = v
    ("hola", "ola"),             # h muda
    ("hecho", "echo"),           # h muda + ch
])
def test_homofonos_misma_clave(a, b):
    assert norm.clave_fonetica(a) == norm.clave_fonetica(b)


# --- clave_fonetica(): no-homofonos producen claves DISTINTAS --------------

@pytest.mark.parametrize("a, b", [
    ("guerra", "gente"),    # g dura /gera/ vs jota /jente/
    ("casa", "gasa"),       # k vs g
    ("pino", "vino"),       # p vs b
])
def test_no_homofonos_clave_distinta(a, b):
    assert norm.clave_fonetica(a) != norm.clave_fonetica(b)


# --- clave_fonetica(): bordes ----------------------------------------------

@pytest.mark.parametrize("entrada", [None, "", "56", "1000", "###"])
def test_clave_fonetica_sin_letras_es_vacia(entrada):
    assert norm.clave_fonetica(entrada) == ""


def test_clave_fonetica_colapsa_dobles():
    # carro y caro colapsan al mismo fonema (limitacion documentada y esperada)
    assert norm.clave_fonetica("carro") == norm.clave_fonetica("caro")