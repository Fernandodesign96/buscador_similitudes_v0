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

# Distancia de edicion ABSOLUTA (Levenshtein, sin normalizar) maxima entre
# dos residuos cortos para tratarlos como la misma palabra con un error de
# tipeo (y por lo tanto omitir el descuento de genericos, igual que antes).
# Fix 06-ago-2026 PM (continuacion), caso reportado "cervezas ricas" vs
# "cerveza yal": antes, CUALQUIER residuo por debajo de
# LONGITUD_MINIMA_RESIDUO_DESCUENTO hacia que se ignorara el descuento sin
# mirar que tan parecido era al otro residuo. "ricas" vs "yal" tambien caia
# en esa regla (por "yal", de 3 caracteres) y el resultado era el score SIN
# descontar "cerveza"/"cervezas" (76.31%), pese a que "ricas" y "yal" no se
# parecen en nada (18.75% entre ellos, que es el numero correcto). La
# distincion correcta es "residuo corto Y ademas muy parecido al otro
# residuo" (ej. 'rey'/'rei', distancia 1) vs "residuo corto pero distinto"
# (ej. 'ricas'/'yal', distancia alta): solo en el primer caso el ratio
# normalizado es el que esta mal (ver fix 05-ago-2026), no el segundo. Se
# usa distancia ABSOLUTA (no ratio) porque el ratio normalizado es
# precisamente la metrica que resulta inestable en cadenas cortas; con
# distancia absoluta, "una sola letra distinta" siempre vale 1 sin importar
# el largo de la palabra. Ver busqueda._residuos_variante_corta().
DISTANCIA_MAXIMA_RESIDUO_CORTO: int = 1

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

# --- Piso por contencion total (prototipo 13-ago-2026, en validacion) ------
# Detectado analizando los rechazos M10 de 2025 reales (sin acceso a SQL
# Server, usando el nombre de la anterioridad extraido del propio texto de
# la observacion): el 31% de los casos sin acierto en el top-10 tienen una
# diferencia de 2+ palabras entre la solicitud y la marca citada (ej. "TU
# ASTRO CAFE" no encuentra a "ASTRO"; "VECTOR LOVE STORY" no encuentra a
# "VECTOR"; "HUAYU REMOTE COTROL" no encuentra a "HUAYU"), con un score
# promedio ~11 puntos mas bajo que el resto de los fallos.
#
# Causa: cuando una de las dos denominaciones queda vacia tras el descuento
# de comunes (_palabras_comunes_fuera), _similitud_ortografica/_fonetica ya
# reconocen que "una marca es casi subconjunto de la otra" y NO aplican el
# castigo -- pero devuelven score_base sin modificar, que sigue siendo el
# ratio bruto de las dos cadenas completas (una mucho mas larga que la
# otra), diluido por las palabras sobrantes del lado largo aunque esas
# palabras no sean genericas. No hay ningun mecanismo que premie el hecho de
# que la marca corta esta contenida, ENTERA, como palabra o palabras
# completas de la marca larga -- que es precisamente la doctrina del
# "elemento dominante" (Sabel v. Puma, C-251/95) que este motor ya invoca
# para el descuento de genericos, pero aplicada aqui de forma incompleta:
# hoy solo protege el elemento dominante cuando el sobrante es generico: no
# cuando una marca completa es, literalmente, una palabra entera de la otra
# (sea o no generico el resto).
#
# PISO_CONTENCION_TOTAL: score minimo (0-100) que se aplica --como maximo
# con el score ya calculado, nunca lo baja-- cuando TODAS las palabras de
# una de las dos marcas (por lema) estan contenidas en las palabras de la
# otra, Y ninguna de esas palabras contenidas es generica por frecuencia en
# la clase NCL del candidato (ver _contencion_total() en busqueda.py). Se
# excluye deliberadamente el caso generico (ej. "SKAAL BEER" vs "BEER": NO
# debe recibir este piso, "BEER" no aporta distintividad) para no
# reintroducir el problema que el descuento de genericos existe para
# resolver.
#
# Valor elegido tras validar contra los 743 casos sin acierto de la
# validacion 2025 (ver notebook/registro de validacion): 82.0 queda por
# encima de SIMILITUD_MIN_RESULTADOS (75) sin llegar al rango de una
# coincidencia exacta (~95-100), dejando lugar a que coincidencias mas
# literales sigan rankeando mas arriba.
#
# Fix 13-ago-2026 (cierre de brecha, deploy): al agregar este piso se dejo
# documentada una advertencia -- "el prefiltro vectorizado (paso 1) no
# incluye todavia esta senal, un candidato con score bruto muy bajo puede
# quedar fuera del top-CANDIDATOS_PREFILTRO y nunca llegar al paso 2 para
# recibir el piso" -- que ya esta resuelta: IndiceBusqueda precalcula un
# indice invertido lema -> marcas (ver indice._indice_invertido_lemas) y
# MotorBusqueda.buscar() lo usa en el PASO 1, antes del recorte a
# CANDIDATOS_PREFILTRO, para encontrar los candidatos que podrian calificar
# (misma logica exacta de largo minimo y genericidad que _contencion_total())
# y subir su score bruto de cada senal a este piso antes de seleccionar el
# top-N. Ver _candidatos_contencion_total() en busqueda.py.
PISO_CONTENCION_TOTAL: float = 82.0

# Longitud minima (sin espacios) que debe tener la marca contenida para
# aplicar el piso anterior. Mismo espiritu que LONGITUD_MINIMA_RESIDUO_
# DESCUENTO: por debajo de este umbral, un piso automatico es mas riesgoso
# que util (una palabra de 3-4 letras contenida en muchas otras marcas por
# pura coincidencia, sin ser realmente el elemento distintivo compartido).
LARGO_MINIMO_CONTENCION_TOTAL: int = 5

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