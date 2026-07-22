"""Configuracion central del buscador de anterioridades de INAPI.

Toda constante de operacion (rutas, esquema de columnas, criterio de
oponibilidad, parametros del motor) vive aqui y en ningun otro lugar. El
codigo de produccion importa desde este modulo; no se redefinen rutas ni
nombres de columna en otros archivos.
"""
from __future__ import annotations

from pathlib import Path

# --- Rutas -----------------------------------------------------------------
RAIZ: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = RAIZ / "data"

ARCHIVO_MARCAS: Path = DATA_DIR / "Datos Marcas.xlsx"   # ajustar extension si corresponde
MARCAS_PROCESADAS: Path = DATA_DIR / "marcas_oponibles.parquet"

# --- Criterio de oponibilidad ---------------------------------------------
# Estados de 'Status Name' considerados anterioridad oponible (marca viva).
# Decision de dominio fundada en los estados que los examinadores citaron
# efectivamente como anterioridad en las observaciones M10 de 2025.
# Se excluyen estados de marca extinta (rechazada, abandonada, desistida,
# cancelada), aunque aparezcan citados: en su momento estaban vivas, hoy no
# son oponibles.
ESTADOS_OPONIBLES: frozenset[str] = frozenset({
    "Registrada",
    "Aguardando por renovación de marca nacional",
    "Aguardando que resolución de aceptación parcial a registro quede en firme",
    "Aguardando que resolución de aceptación a registro sea publicada",
    "Aguardando que fallo de aceptación a registro quede en firme",
    "Aguardando que fallo de aceptación parcial a registro quede en firme",
})
# --- Esquema del archivo de origen ----------------------------------------
COL_MARK_CODE: str = "Mark Code (Ip Name)"
COL_NOMBRE: str = "Mark Name"
COL_CLASE: str = "Nice Class Code"
COL_NRO_SOL: str = "Nro_sol"
COL_STATUS: str = "Status Name"

# Columnas que el archivo de origen DEBE contener para ser procesable.
COLUMNAS_REQUERIDAS: tuple[str, ...] = (
    COL_MARK_CODE,
    COL_NOMBRE,
    COL_CLASE,
    COL_NRO_SOL,
    COL_STATUS,
)

# --- Parametros del motor de busqueda -------------------------------------
# Pesos de las dos senales al combinar (deben sumar 1.0).
# La senal semantica fue retirada del motor por decision de negocio (reunion
# julio 2026): el riesgo de confusion marcaria se evalua exclusivamente por
# parecido grafico y fonetico, que es ademas el criterio que usa el
# examinador real. Se mantiene la proporcion relativa que tenian ortografico
# y fonetico cuando existia la tercera senal (0.55 / 0.40 -> reescalado a
# suma 1.0).
PESO_ORTOGRAFICO: float = 0.58
PESO_FONETICO: float = 0.42

# Resultados finales devueltos por consulta.
TOP_RESULTADOS: int = 10

# Umbral de relacion de clase NCL: si las marcas no comparten clase, el score
# combinado se atenua por este factor (clases no relacionadas = menor riesgo).
FACTOR_CLASE_NO_RELACIONADA: float = 0.7

# --- Pre-filtro vectorizado (cdist) ---------------------------------------
# Decision de julio 2026: el motor calcula un score bruto (sin descuento de
# palabras genericas) contra el universo completo usando rapidfuzz.process.cdist
# (vectorizado en C++). Solo se recalcula el score exacto (con descuento de
# genericos) sobre este top-N de candidatos brutos, no sobre las 218.369 marcas.
# Justificacion: descontar palabras genericas solo puede REDUCIR el score de un
# par (nunca aumentarlo), por lo que el ranking bruto es un superconjunto seguro
# del ranking final para un N suficientemente holgado frente a TOP_RESULTADOS.
# No confundir con el extinto CANDIDATOS_FAISS (recuperacion semantica, ya
# retirada): este prefiltro es puramente ortografico/fonetico y determinista.
CANDIDATOS_PREFILTRO: int = 200