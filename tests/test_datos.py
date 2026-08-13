"""Tests de la logica de transformacion de datos del buscador.

Se prueban las funciones puras (derivacion del Nro_sol, filtrado, agrupacion
y validacion de esquema) con DataFrames construidos en memoria, sin depender
del archivo Excel real.
"""
from __future__ import annotations

import pandas as pd
import pytest

from buscador import config, datos


def _fila(mark_code, nombre, clase, nro_sol, status):
    return {
        config.COL_MARK_CODE: mark_code,
        config.COL_NOMBRE: nombre,
        config.COL_CLASE: clase,
        config.COL_NRO_SOL: nro_sol,
        config.COL_STATUS: status,
    }


# --- Validacion de esquema -------------------------------------------------

def test_validar_columnas_falla_si_falta_columna():
    df = pd.DataFrame({config.COL_MARK_CODE: [1], config.COL_NOMBRE: ["X"]})
    with pytest.raises(datos.DatosInvalidosError):
        datos._validar_columnas(df)


def test_validar_columnas_pasa_con_esquema_completo():
    df = pd.DataFrame([_fila(1, "X", 5, 12345, "Registrada")])
    datos._validar_columnas(df)  # no debe lanzar


# --- Derivacion de solicitud_base -----------------------------------------

@pytest.mark.parametrize("nro_sol, clase, esperado", [
    ("11852757", 7, "1185275"),     # clase de un digito
    ("99192045442", 42, "991920454"),  # clase de dos digitos
    ("11852721", 1, "1185272"),     # clase 1
])
def test_derivar_quita_sufijo_de_clase(nro_sol, clase, esperado):
    df = pd.DataFrame([_fila(1, "M", clase, nro_sol, "Registrada")])
    resultado, no_cumple = datos.derivar_solicitud_base(df)
    assert resultado["solicitud_base"].iloc[0] == esperado
    assert no_cumple == 0


def test_derivar_conserva_valor_si_no_termina_en_clase():
    # Nro_sol termina en 7, no en 9 -> no se altera y cuenta como excepcion.
    df = pd.DataFrame([_fila(1, "M", 9, "1234567", "Registrada")])
    resultado, no_cumple = datos.derivar_solicitud_base(df)
    assert resultado["solicitud_base"].iloc[0] == "1234567"
    assert no_cumple == 1


# --- Filtrado de oponibles -------------------------------------------------

def test_filtrar_conserva_solo_estados_oponibles():
    df = pd.DataFrame([
        _fila(1, "REGISTRADA SA", 5, 100, "Registrada"),
        _fila(2, "RECHAZADA SA", 5, 200, "Rechazada"),
    ])
    resultado = datos.filtrar_oponibles(df)
    assert list(resultado[config.COL_MARK_CODE]) == [1]


@pytest.mark.parametrize("nombre", [None, "", "   "])
def test_filtrar_descarta_nombres_vacios(nombre):
    df = pd.DataFrame([_fila(1, nombre, 5, 100, "Registrada")])
    resultado = datos.filtrar_oponibles(df)
    assert len(resultado) == 0


# --- Agrupacion por marca --------------------------------------------------

def test_agrupar_reune_clases_y_solicitudes():
    df = pd.DataFrame([
        _fila(533217, "SAFRAN", 2, "11852752", "Registrada"),
        _fila(533217, "SAFRAN", 7, "11852757", "Registrada"),
        _fila(533217, "SAFRAN", 9, "11852759", "Registrada"),
    ])
    df, _ = datos.derivar_solicitud_base(df)
    agrupado = datos.agrupar_por_marca(df)

    assert len(agrupado) == 1
    fila = agrupado.iloc[0]
    assert fila["mark_code"] == 533217
    assert fila["nombre"] == "SAFRAN"
    assert fila["clases"] == [2, 7, 9]
    assert fila["solicitudes"] == ["1185275"]  # misma base, deduplicada


def test_agrupar_separa_marcas_distintas():
    df = pd.DataFrame([
        _fila(1, "ALFA", 5, "1005", "Registrada"),
        _fila(2, "BETA", 5, "2005", "Registrada"),
    ])
    df, _ = datos.derivar_solicitud_base(df)
    agrupado = datos.agrupar_por_marca(df)
    assert len(agrupado) == 2
    assert set(agrupado["mark_code"]) == {1, 2}

def test_agrupar_uniforma_nombre_numerico_a_texto():
    # Una marca cuyo nombre es puramente numerico debe quedar como texto,
    # para garantizar un esquema consistente al persistir.
    df = pd.DataFrame([_fila(1, 1000, 5, "10005", "Registrada")])
    df, _ = datos.derivar_solicitud_base(df)
    agrupado = datos.agrupar_por_marca(df)

    assert agrupado["nombre"].iloc[0] == "1000"
    assert isinstance(agrupado["nombre"].iloc[0], str)