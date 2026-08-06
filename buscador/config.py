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

# Umbral minimo de similitud (%) para mostrar marcas en el MVP web.
SIMILITUD_MIN_RESULTADOS: float = 75.0

# Umbral de relacion de clase NCL: si las marcas no comparten clase, el score
# combinado se atenua por este factor (clases no relacionadas = menor riesgo).
FACTOR_CLASE_NO_RELACIONADA: float = 0.7

# Longitud minima (en caracteres, sin contar espacios) que debe tener el
# residuo de CADA marca, en busqueda.py, tras descontar las palabras/claves
# exactamente comunes, para que el descuento de genericos se aplique. Por
# debajo de este umbral el ratio de edicion normalizado es estadisticamente
# inestable (una sola letra de diferencia en un residuo de 2-3 caracteres
# puede hacer caer el score 20-30 puntos), lo que castiga de forma
# desproporcionada variantes casi identicas de una marca multi-palabra.
# Fix 05-ago-2026, caso reportado "brasas del rey" vs "brasas del rei": tras
# descontar "brasas" y "del" (comunes), el residuo "rey"/"rei" (3 caracteres)
# hacia caer el score de ~93% a 66.67%. Ver _residuo_muy_corto() en
# busqueda.py.
LONGITUD_MINIMA_RESIDUO_DESCUENTO: int = 4

# Longitud minima (en caracteres) que debe tener una palabra para que
# normalizacion.lema() intente singularizarla (quitarle la 's' final de
# plural cuando va precedida de vocal, ej. 'cervezas' -> 'cerveza'). Evita
# singularizar palabras muy cortas, donde quitar la 's' final tiene mas
# riesgo de fusionar por error dos palabras que no son la misma. Fix
# 06-ago-2026 AM, caso "cervezas ricas" vs "cerveza tribal": el plural
# evitaba que "cerveza"/"cervezas" (termino generico del rubro) se
# detectara como palabra comun, y el descuento de genericos nunca se
# activaba.
LONGITUD_MINIMA_PALABRA_LEMA: int = 4

# --- Ponderacion por genericidad segun frecuencia en el universo ----------
# Fix 06-ago-2026 PM: reemplaza (complementa) la deteccion de "palabra
# generica" por coincidencia exacta o de lema ENTRE LAS DOS MARCAS
# COMPARADAS por una basada en que tan frecuente es esa palabra dentro de
# las marcas de la MISMA clase NCL que el candidato. Ver
# indice.FrecuenciasPalabras.es_generica().
#
# UMBRAL_FRECUENCIA_GENERICO: fraccion minima (0-1) de las marcas de una
# clase que deben tener una palabra para considerarla generica/descriptiva
# de ese rubro. Calibrado empiricamente contra el universo real: "cerveza"
# aparece en ~4.7% de las marcas de la clase 32 (claramente generico ahi),
# mientras que palabras comunes del espanol pero no descriptivas de ningun
# rubro en particular (ej. "sur") no superan ~0.7% en ninguna clase
# individual. 1% separa razonablemente ambos grupos.
UMBRAL_FRECUENCIA_GENERICO: float = 0.01

# CONTEO_MINIMO_GENERICO: ademas del umbral anterior, la palabra debe
# aparecer en al menos este numero absoluto de marcas de la clase. Evita que
# una clase con pocas marcas totales produzca porcentajes ruidosos (ej. una
# palabra repetida 3 veces en una clase de 50 marcas ya es 6%, sin que eso
# signifique que sea realmente generica).
CONTEO_MINIMO_GENERICO: int = 20

# --- Ponderacion por inicio de palabra (Jaro-Winkler) ----------------------
# Fix 06-ago-2026 PM: un consumidor real presta mas atencion al inicio de
# una palabra que a su final (modelo "cohort" de reconocimiento de habla,
# Marslen-Wilson 1987; metrica de Winkler 1990 usada en record linkage).
# Se combina la metrica de similitud existente (token_sort_ratio para la
# senal ortografica, fuzz.ratio para la fonetica) con Jaro-Winkler, que da
# un bono cuando dos cadenas comparten el inicio. Los pesos de cada mezcla
# suman 1.0; se dejo un peso menor a Jaro-Winkler porque es un ajuste, no un
# reemplazo, de la metrica ya validada por los tests existentes.
PESO_TOKEN_SORT_ORTOGRAFICO: float = 0.75
PESO_JARO_WINKLER_ORTOGRAFICO: float = 0.25
PESO_RATIO_FONETICO: float = 0.75
PESO_JARO_WINKLER_FONETICO: float = 0.25

# --- N-gramas de caracteres como verificacion cruzada adicional ------------
# Fix 06-ago-2026 PM: complementa la comparacion por palabras (token_sort_
# ratio) con una medida agnostica a como estan segmentadas las palabras: el
# coeficiente de Dice sobre fragmentos de N caracteres de la cadena
# completa. Se usa como piso de seguridad adicional (el score final nunca
# puede superarlo), no como señal que pueda subir el score, para no romper
# el invariante del prefiltro vectorizado (ver busqueda.py).
LONGITUD_NGRAMA: int = 3

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