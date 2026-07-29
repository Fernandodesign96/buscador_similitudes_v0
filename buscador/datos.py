"""Carga, validacion, filtrado y agrupacion de las marcas de INAPI.

El archivo de origen (export de SQL Server a Excel) tiene grano
(marca, clase): una fila por cada clase Niza de cada marca. Este modulo lo
transforma en el dataset que alimenta el indice de busqueda: una fila por
marca, identificada por su Mark Code, con el conjunto de clases Niza y los
numeros de solicitud base asociados.

El modulo no configura logging: expone un logger de modulo y delega la
configuracion de handlers al script de entrada, segun la convencion estandar
de librerias de Python.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from . import config

logger = logging.getLogger(__name__)

__all__ = [
    "DatosInvalidosError",
    "cargar_crudo",
    "derivar_solicitud_base",
    "filtrar_oponibles",
    "agrupar_por_marca",
    "construir",
    "guardar",
]


class DatosInvalidosError(ValueError):
    """El archivo de origen no cumple el esquema esperado."""


def _validar_columnas(df: pd.DataFrame) -> None:
    """Verifica que el DataFrame contenga todas las columnas requeridas.

    Raises:
        DatosInvalidosError: si falta al menos una columna del esquema.
    """
    faltantes = [c for c in config.COLUMNAS_REQUERIDAS if c not in df.columns]
    if faltantes:
        raise DatosInvalidosError(
            f"El archivo de origen no contiene las columnas requeridas: {faltantes}. "
            f"Columnas encontradas: {list(df.columns)}."
        )


def cargar_crudo(ruta: Path = config.ARCHIVO_MARCAS) -> pd.DataFrame:
    """Lee el Excel de origen, normaliza los encabezados y valida el esquema.

    Args:
        ruta: ubicacion del archivo Excel de marcas.

    Returns:
        DataFrame con los encabezados sin espacios sobrantes.

    Raises:
        FileNotFoundError: si el archivo no existe.
        DatosInvalidosError: si faltan columnas del esquema esperado.
    """
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontro el archivo de marcas: {ruta}")

    logger.info("Leyendo archivo de origen: %s", ruta)
    df = pd.read_excel(ruta)
    df.columns = df.columns.str.strip()
    _validar_columnas(df)
    logger.info("Archivo leido: %d filas", len(df))
    return df


def derivar_solicitud_base(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Agrega la columna 'solicitud_base': el Nro_sol sin el sufijo de clase.

    En los datos de INAPI el Nro_sol concatena el numero de solicitud base con
    el codigo de clase Niza al final, sin relleno de ceros (ej.: solicitud
    1185275 + clase 7 -> 11852757). El sufijo se remueve solo cuando el Nro_sol
    efectivamente termina en el codigo de clase de esa fila; en caso contrario
    el valor se conserva intacto y se contabiliza como excepcion al patron.

    Args:
        df: DataFrame validado con las columnas de Nro_sol y clase.

    Returns:
        Tupla (DataFrame con la columna 'solicitud_base', cantidad de filas que
        no cumplieron el patron). Un conteo alto de excepciones indica que la
        regla de derivacion debe revisarse.
    """
    nro = df[config.COL_NRO_SOL].astype(str).str.strip()
    clase = df[config.COL_CLASE].astype(str).str.strip()

    termina_en_clase = [n.endswith(c) for n, c in zip(nro, clase)]
    base = [
        n[: -len(c)] if t else n
        for n, c, t in zip(nro, clase, termina_en_clase)
    ]

    resultado = df.copy()
    resultado["solicitud_base"] = base

    no_cumple = len(termina_en_clase) - sum(termina_en_clase)
    proporcion = no_cumple / len(df) if len(df) else 0.0
    if proporcion > 0.01:
        logger.warning(
            "Derivacion de solicitud_base: %d filas (%.2f%%) no siguen el patron "
            "Nro_sol = base + clase; revisar la regla.",
            no_cumple, proporcion * 100,
        )
    else:
        logger.info(
            "Derivacion de solicitud_base: %d filas fuera de patron (%.2f%%).",
            no_cumple, proporcion * 100,
        )
    return resultado, no_cumple


def filtrar_oponibles(
    df: pd.DataFrame,
    estados: frozenset[str] = config.ESTADOS_OPONIBLES,
) -> pd.DataFrame:
    """Conserva solo las filas oponibles y buscables denominativamente.

    Descarta las filas cuyo Status Name no esta en el conjunto de estados
    oponibles y las que no tienen nombre de marca (nulo o vacio), porque sin
    nombre no pueden compararse por similitud denominativa.

    Args:
        df: DataFrame de origen.
        estados: conjunto de Status Name considerados anterioridad oponible.

    Returns:
        DataFrame filtrado.
    """
    n_inicial = len(df)

    por_estado = df[df[config.COL_STATUS].isin(estados)]
    n_estado = len(por_estado)

    nombre = por_estado[config.COL_NOMBRE]
    con_nombre = por_estado[nombre.notna() & (nombre.astype(str).str.strip() != "")]
    n_final = len(con_nombre)

    logger.info(
        "Filtrado: %d filas -> %d por estado oponible -> %d con nombre valido.",
        n_inicial, n_estado, n_final,
    )
    return con_nombre


def agrupar_por_marca(df: pd.DataFrame) -> pd.DataFrame:
    """Reduce el grano (marca, clase) a una fila por marca.

    Agrupa por Mark Code y reune el conjunto de clases Niza y de solicitudes
    base. El nombre se toma como el primero del grupo porque es constante por
    Mark Code (verificado en la inspeccion de datos).

    Algunos nombres de marca son puramente numericos (ej.: "1000") y el lector
    de Excel los tipa como int, dejando la columna con tipos mixtos. Se uniforman
    a texto para garantizar un esquema consistente al persistir en Parquet.

    Args:
        df: DataFrame filtrado que incluye la columna 'solicitud_base'.

    Returns:
        DataFrame con columnas: mark_code, nombre, clases, solicitudes.
    """
    df = df.copy()
    df[config.COL_NOMBRE] = df[config.COL_NOMBRE].astype(str)

    agrupado = (
        df.groupby(config.COL_MARK_CODE)
        .agg(
            nombre=(config.COL_NOMBRE, "first"),
            clases=(config.COL_CLASE, lambda s: sorted({int(x) for x in s})),
            solicitudes=("solicitud_base", lambda s: sorted(set(s))),
        )
        .reset_index()
        .rename(columns={config.COL_MARK_CODE: "mark_code"})
    )
    logger.info("Agrupacion: %d marcas unicas.", len(agrupado))
    return agrupado


def construir(ruta: Path = config.ARCHIVO_MARCAS) -> tuple[pd.DataFrame, dict[str, int]]:
    """Ejecuta el pipeline completo: carga -> deriva base -> filtra -> agrupa.

    Args:
        ruta: ubicacion del archivo Excel de marcas.

    Returns:
        Tupla (DataFrame de marcas oponibles agrupadas, diccionario de
        estadisticas del procesamiento).
    """
    crudo = cargar_crudo(ruta)
    con_base, no_cumple = derivar_solicitud_base(crudo)
    oponibles = filtrar_oponibles(con_base)
    marcas = agrupar_por_marca(oponibles)

    stats: dict[str, int] = {
        "filas_crudas": len(crudo),
        "solicitud_base_sin_patron": no_cumple,
        "filas_oponibles": len(oponibles),
        "marcas_unicas": len(marcas),
    }
    return marcas, stats


def guardar(marcas: pd.DataFrame, ruta: Path = config.MARCAS_PROCESADAS) -> None:
    """Persiste el dataset de marcas en formato Parquet.

    Args:
        marcas: DataFrame agrupado a guardar.
        ruta: destino del archivo Parquet.
    """
    marcas.to_parquet(ruta, index=False)
    logger.info("Dataset guardado en %s (%d marcas).", ruta, len(marcas))