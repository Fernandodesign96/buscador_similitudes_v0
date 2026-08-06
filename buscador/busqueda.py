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

Fix 05-ago-2026 (residuo demasiado corto tras el descuento de genericos):
reportado con "brasas del rey" vs "brasas del rei". Al descontar las
palabras exactas comunes ("brasas", "del"), el residuo queda en "rey" vs
"rei" (3 caracteres). El ratio de edicion normalizado es muy inestable
sobre residuos tan cortos: una sola letra distinta ya hace caer el score de
~93% a 66.67%, castigando de forma desproporcionada una variante casi
identica de una marca multi-palabra. Se agrega un piso de longitud
(config.LONGITUD_MINIMA_RESIDUO_DESCUENTO): si el residuo de cualquiera de
los dos lados queda por debajo de ese piso, se omite el descuento y se
devuelve el score base (sin descontar), igual que cuando el residuo queda
vacio. Esto no reabre el problema original que motivo el descuento (p. ej.
"SKAAL BEER" vs "SVAJG BEER": el residuo "skaal"/"svajg" tiene 5 caracteres,
por encima del piso), solo evita aplicarlo cuando el residuo es demasiado
corto para que el porcentaje sea confiable.

Fix 06-ago-2026 (palabras genericas casi-comunes, no EXACTAMENTE comunes):
reportado con "cervezas ricas" vs "cerveza tribal" (77% de similitud pese a
no tener relacion real). "cervezas" (plural) y "cerveza" (singular) NO son
la misma cadena, asi que _palabras_comunes_fuera() no las detectaba como
comunes: el descuento de genericos nunca se activaba, y "cerveza"/"cervezas"
(termino descriptivo del rubro, no elemento distintivo) dominaba el ratio de
caracteres frente a "ricas"/"tribal" (las palabras que si distinguen a cada
marca). Se agrega _lema(), una singularizacion naive (solo cubre el patron
de plural mas comun del espanol: vocal + 's', ej. 'cervezas' -> 'cerveza',
'casas' -> 'casa') que se usa SOLO para decidir que palabras se consideran
"comunes" en ambas senales (ortografica y fonetica); el residuo que se
compara sigue usando las palabras/claves originales, no el lema. No cubre el
patron consonante + 'es' (ej. 'flores' -> 'flor'): se documenta como
limitacion conocida en vez de arriesgar una regla mas agresiva sin evidencia
empirica de que sea necesaria, mismo criterio que el resto de este modulo.
La singularizacion (_lema() en ese momento) se movio a normalizacion.lema()
en el fix siguiente porque indice.py tambien la necesita.

Fix 06-ago-2026 PM (acercar el motor al criterio de un examinador humano):
tres cambios, pensados para que compongan con todo lo anterior sin romper
el invariante de seguridad del prefiltro (el descuento/ajuste solo puede
BAJAR un score, nunca subirlo por encima del bruto calculado por cdist):

  1. Ponderacion por genericidad segun frecuencia en el universo (sustituye
     la deteccion de "palabra generica" por coincidencia exacta/de lema
     ENTRE LAS DOS MARCAS COMPARADAS por una basada en que tan frecuente es
     esa palabra dentro de las marcas de la clase NCL real del candidato:
     ver indice.FrecuenciasPalabras y _palabras_comunes_fuera() mas abajo).
     Motivo doctrinal: el examinador no compara con el mismo peso cada
     palabra de una marca, sino que identifica el elemento distintivo y
     descuenta lo meramente descriptivo del rubro (doctrina del "elemento
     dominante"; Sabel v. Puma, C-251/95). Generaliza el fix de la mañana
     (que solo detectaba genericos EXACTOS o su plural) a sinonimos
     ortograficos del mismo termino generico, sin necesitar que la otra
     marca lo comparta literalmente.

  2. Jaro-Winkler combinado con la metrica existente, en ambas senales, para
     darle mas peso al inicio de la palabra (ver config.PESO_JARO_WINKLER_*
     y _score_ortografico_base() / _score_fonetico_base()). Motivo: el
     consumidor real (y el modelo "cohort" de reconocimiento de habla,
     Marslen-Wilson 1987) presta mas atencion al comienzo de una palabra que
     a su final; Jaro-Winkler (Winkler, 1990) fue disenado exactamente para
     esto y ya viene incluido en rapidfuzz.

  3. N-gramas de caracteres (coeficiente de Dice, ver _similitud_ngramas()):
     se implemento y se probo como verificacion cruzada adicional sobre el
     residuo tras el descuento (agnostica a como estan segmentadas las
     palabras), pero se REVIRTIO antes de dejarla en el calculo del score.
     Al probarla contra una muestra de marcas reales con una sola letra
     insertada o borrada (la variante mas comun de "error de tipeo"), el
     coeficiente de Dice de n-gramas resulto muy inestable ante ese tipo de
     edicion especifico: una insercion desplaza todos los n-gramas
     posteriores al punto de insercion, y puede hacer caer el score 30
     puntos o mas en una palabra de 8-10 caracteres aunque el resto sea
     identico (ej. 'SEMINRIOS' vs 'SEMINARIOS': cae de ~95% a 66.67% solo
     por este piso). Usarla como min() habria reintroducido, con otro
     mecanismo, el mismo tipo de falso negativo que motivo el fix del
     05-ago-2026 (residuo demasiado corto). La funcion queda implementada y
     con test propio por si se retoma con un diseño mas robusto a
     inserciones/borrados; no participa del calculo de _similitud_ortografica
     ni _similitud_fonetica por ahora.

Fix 06-ago-2026 PM (continuacion, mismo dia): reportado "cervezas ricas" vs
"cerveza yal" dando un score alto pese a no tener relacion real. Con el fix
de genericidad por frecuencia ya activo, "cerveza"/"cervezas" se descuenta
de ambos lados (generico en clase 32) y el residuo queda en "ricas" vs
"yal" (3 caracteres, bajo config.LONGITUD_MINIMA_RESIDUO_DESCUENTO). El
ratio normalizado entre esos residuos (18.75%) es correcto -- son palabras
distintas -- pero _residuo_muy_corto() por si sola hacia que se ignorara
ese numero y se devolviera el score SIN descontar "cerveza" (76.31%), el
mismo mecanismo pensado para proteger 'rey'/'rei' (fix 05-ago-2026)
protegiendo por error un caso donde no habia nada que proteger. Se agrega
_residuos_variante_corta(): ademas de que el residuo sea corto, exige que
la distancia de edicion ABSOLUTA (Levenshtein, no normalizada) entre ambos
residuos sea baja (config.DISTANCIA_MAXIMA_RESIDUO_CORTO) para tratarlos
como la misma palabra con un error de tipeo. 'rey'/'rei' sigue protegido
(distancia 1); 'ricas'/'yal' ya no (distancia mucho mayor), y el descuento
se aplica con normalidad, dejando que el 18.75% baje el score como
corresponde.

Referencias completas de la literatura citada en las notas de diseño
entregadas el 06-ago-2026 (Cohen, Ravikumar y Fienberg 2003; Winkler 1990;
Marslen-Wilson 1987; Sabel v. Puma C-251/95; Lloyd Schuhfabrik C-342/97).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
from rapidfuzz import fuzz, process
from rapidfuzz.distance import JaroWinkler, Levenshtein

from . import config, normalizacion
from .indice import FrecuenciasPalabras, IndiceBusqueda

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


def _palabras_comunes_fuera(
    a: str,
    b: str,
    *,
    frecuencias: FrecuenciasPalabras | None = None,
    clases: list[int] | None = None,
) -> tuple[str, str]:
    """Quita de cada cadena las palabras genericas: las que aparecen en
    ambas (comparando por lema, no por cadena exacta: ver
    normalizacion.lema()) Y, si se entrega una tabla de frecuencias, las que
    son genericas/descriptivas por su frecuencia en el universo (ver
    indice.FrecuenciasPalabras.es_generica()), sin necesidad de que la otra
    marca la comparta literalmente.

    frecuencias/clases son opcionales: si no se entregan (por ejemplo en
    tests unitarios que llaman a esta funcion sin un indice real), el
    comportamiento es exactamente el de antes del fix 06-ago-2026 PM (solo
    descuenta palabras compartidas por lema entre las dos marcas).
    """
    wa, wb = a.split(), b.split()
    lemas_a, lemas_b = [normalizacion.lema(w) for w in wa], [normalizacion.lema(w) for w in wb]
    comunes = set(lemas_a) & set(lemas_b)

    def _es_generica(palabra: str, lema: str) -> bool:
        if lema in comunes:
            return True
        if frecuencias is not None:
            return frecuencias.es_generica(palabra, clases)
        return False

    fa = " ".join(w for w, lema in zip(wa, lemas_a) if not _es_generica(w, lema))
    fb = " ".join(w for w, lema in zip(wb, lemas_b) if not _es_generica(w, lema))
    return fa, fb


def _score_ortografico_base(a: str, b: str) -> float:
    """Similitud ortografica 0-100 SIN descuento de genericos: combina
    token_sort_ratio con Jaro-Winkler (fix 06-ago-2026 PM) sobre los tokens
    ya ordenados alfabeticamente (ver normalizacion.ordenar_tokens), para
    darle mas peso al inicio de cada palabra ademas de tolerar el
    reordenamiento de palabras. Es la funcion que usa tanto
    _similitud_ortografica() (sobre el residuo, tras el descuento) como el
    prefiltro vectorizado de MotorBusqueda.buscar() (sobre el universo
    completo, sin descuento): dos llamados a rapidfuzz.process.cdist con
    los mismos pesos contra idx.canonicos_ordenados, en vez de este calculo
    por par — ver ese metodo para el detalle.
    """
    oa, ob = normalizacion.ordenar_tokens(a), normalizacion.ordenar_tokens(b)
    token_sort = float(fuzz.ratio(oa, ob))  # == fuzz.token_sort_ratio(a, b)
    jaro_winkler = float(JaroWinkler.similarity(oa, ob)) * 100.0
    return (
        config.PESO_TOKEN_SORT_ORTOGRAFICO * token_sort
        + config.PESO_JARO_WINKLER_ORTOGRAFICO * jaro_winkler
    )


def _score_fonetico_base(a: str, b: str) -> float:
    """Similitud fonetica 0-100 SIN descuento de genericos: combina
    fuzz.ratio con Jaro-Winkler (fix 06-ago-2026 PM). A diferencia de la
    version ortografica, no ordena tokens: la senal fonetica nunca lo hizo
    (clave_fonetica fusiona toda la denominacion en un solo bloque sin
    espacios, ver normalizacion.py), asi que no hay tokens que ordenar a
    este nivel.
    """
    ratio = float(fuzz.ratio(a, b))
    jaro_winkler = float(JaroWinkler.similarity(a, b)) * 100.0
    return (
        config.PESO_RATIO_FONETICO * ratio
        + config.PESO_JARO_WINKLER_FONETICO * jaro_winkler
    )


def _ngramas(texto: str, n: int) -> set[str]:
    """Conjunto de fragmentos de n caracteres consecutivos de `texto`."""
    if len(texto) < n:
        return set()
    return {texto[i:i + n] for i in range(len(texto) - n + 1)}


def _similitud_ngramas(a: str, b: str, n: int = config.LONGITUD_NGRAMA) -> float:
    """Similitud 0-100 por coeficiente de Dice sobre n-gramas de caracteres
    (fix 06-ago-2026 PM). Complementa la comparacion por palabras
    (token_sort_ratio): mide superposicion de fragmentos de n caracteres en
    toda la cadena, sin depender de que las palabras esten bien segmentadas
    por espacios. Se usa unicamente como piso de seguridad adicional sobre
    el residuo ya descontado (ver _similitud_ortografica/_similitud_fonetica):
    el score final nunca puede superarlo, solo puede coincidir o ser menor,
    para no romper el invariante de seguridad del prefiltro (ver
    MotorBusqueda). Por eso no participa del prefiltro vectorizado: al ser
    un piso y no una señal que pueda subir el score, no necesita estar
    presente en el bruto para preservarlo como cota superior segura.
    """
    if not a or not b:
        return 0.0
    if a == b:
        return 100.0
    if (
        len(a.replace(" ", "")) < config.LONGITUD_MINIMA_RESIDUO_DESCUENTO
        or len(b.replace(" ", "")) < config.LONGITUD_MINIMA_RESIDUO_DESCUENTO
    ):
        # Cadenas muy cortas (mismo piso que _residuo_muy_corto): con tan
        # pocos caracteres, un par de n-gramas alcanza a cubrir toda la
        # palabra, y basta una letra de diferencia para que la interseccion
        # caiga a 0 aunque las palabras sean casi identicas (ej. 'rey' vs
        # 'rei' con n=3 tienen exactamente un trigrama cada una y no
        # coinciden). Se devuelve 100.0 (no restringe el minimo) para no
        # repetir, con n-gramas, el mismo problema que _residuo_muy_corto ya
        # resolvio para la comparacion por palabras (fix 05-ago-2026).
        return 100.0
    ga, gb = _ngramas(a, n), _ngramas(b, n)
    if not ga or not gb:
        return 0.0
    interseccion = len(ga & gb)
    return 200.0 * interseccion / (len(ga) + len(gb))


def _residuo_muy_corto(*residuos: str) -> bool:
    """True si algun residuo (tras descontar palabras/claves comunes) tiene
    menos caracteres alfabeticos que config.LONGITUD_MINIMA_RESIDUO_DESCUENTO.

    Los espacios no cuentan como caracteres de contenido (un residuo de dos
    palabras de 2 letras cada una sigue siendo "corto" en el sentido que nos
    importa: pocas letras sobre las que calcular un ratio confiable).
    """
    return any(
        len(r.replace(" ", "")) < config.LONGITUD_MINIMA_RESIDUO_DESCUENTO
        for r in residuos
    )


def _residuos_variante_corta(fa: str, fb: str) -> bool:
    """True si conviene IGNORAR el descuento de genericos entre fa y fb
    porque son residuos cortos que ademas son casi la misma palabra (una
    variante de tipeo), no dos palabras cortas pero distintas.

    Fix 06-ago-2026 PM (continuacion). Antes, `_residuo_muy_corto(fa, fb)`
    por si sola decidia esto: CUALQUIER residuo por debajo de
    config.LONGITUD_MINIMA_RESIDUO_DESCUENTO bastaba para descartar el
    descuento y devolver el score sin descontar (score_base), sin mirar si
    el otro residuo se parecia o no. Caso reportado: "cervezas ricas" vs
    "cerveza yal". Tras descontar "cerveza" (generico en clase 32 por
    frecuencia), el residuo queda en "ricas" vs "yal" (3 caracteres, bajo el
    piso). El ratio normalizado entre ellos es 18.75%, que es el numero
    CORRECTO: "ricas" y "yal" no se parecen. Pero como "yal" es corto, la
    version anterior ignoraba ese 18.75% y devolvia 76.31% (el score de
    "cervezas ricas" vs "cerveza yal" SIN descontar "cerveza"/"cervezas"),
    como si ambas marcas fueran esencialmente la misma.

    La distincion correcta no es "el residuo es corto" sino "el residuo es
    corto Y ADEMAS se parece mucho al otro residuo" (ej. 'rey'/'rei': misma
    palabra, un error de tipeo). Solo en ese caso el ratio normalizado es el
    que esta mal (cae desproporcionado por el largo tan corto, ver fix
    05-ago-2026) y conviene ignorarlo. Cuando los residuos cortos son
    palabras distintas (ej. 'ricas'/'yal'), el ratio bajo ya es correcto y
    no hay nada que proteger: dejar que el descuento baje el score es lo
    esperado.

    Se mide "parecido" con distancia de edicion ABSOLUTA (Levenshtein, sin
    normalizar), no con el ratio normalizado: el ratio normalizado es
    precisamente la metrica inestable en cadenas cortas que este mecanismo
    existe para esquivar. Con distancia absoluta, una sola letra distinta
    siempre cuenta como 1, sin importar el largo de la palabra (ver
    config.DISTANCIA_MAXIMA_RESIDUO_CORTO).
    """
    if not _residuo_muy_corto(fa, fb):
        return False
    return Levenshtein.distance(fa, fb) <= config.DISTANCIA_MAXIMA_RESIDUO_CORTO


def _similitud_ortografica(
    a: str,
    b: str,
    *,
    frecuencias: FrecuenciasPalabras | None = None,
    clases: list[int] | None = None,
) -> float:
    """Similitud ortografica 0-100 sobre formas canonicas.

    Usa _score_ortografico_base() como base: token_sort_ratio (tolera
    reordenamiento de palabras, ej. 'CASA BLANCA' / 'BLANCA CASA') combinado
    con Jaro-Winkler (fix 06-ago-2026 PM, mas peso al inicio de palabra).
    Para evitar que una palabra generica compartida ('BEER', 'CHILE', etc.)
    infle el parecido entre marcas cuyo elemento distintivo es en realidad
    muy distinto, se calcula tambien el score quitando las palabras
    genericas de cada marca (ver _palabras_comunes_fuera(): por lema
    compartido entre ambas, o por frecuencia en la clase NCL del candidato
    si se entrega `frecuencias`/`clases`) y se usa el minimo de los dos. Si
    quitar las genericas deja una cadena vacia (una marca es casi
    subconjunto de la otra, ej. 'SKAAL BEER' vs 'SKAAL'), no se aplica el
    castigo: se mantiene el score base.

    `frecuencias`/`clases` son opcionales (ver _palabras_comunes_fuera): sin
    ellos, el comportamiento es el mismo de antes del fix 06-ago-2026 PM.

    Tampoco se aplica el descuento si el residuo (lo que queda de cada
    marca tras quitar las palabras genericas) es corto Y ademas se parece
    mucho al residuo del otro lado (variante de tipeo, ej. 'rey'/'rei'): ver
    _residuos_variante_corta(), fix 05-ago-2026 y su continuacion el
    06-ago-2026 PM. Si el residuo es corto pero es una palabra distinta del
    otro lado (ej. 'ricas'/'yal'), el descuento SI se aplica: el ratio bajo
    entre residuos cortos pero distintos ya es el numero correcto, no hay
    que protegerlo.

    NO se usa _similitud_ngramas() como piso adicional aqui (a diferencia de
    lo planeado originalmente en el fix 06-ago-2026 PM): al probarlo contra
    una muestra de marcas reales con una sola letra insertada o borrada (el
    tipo de variante mas comun y mas importante de detectar), el coeficiente
    de Dice de n-gramas resulto ser mucho mas inestable de lo esperado ante
    inserciones/borrados (no ante sustituciones): una sola letra insertada a
    mitad de palabra desplaza todos los trigramas posteriores y puede hacer
    caer el score 30 puntos o mas en palabras de 8-10 caracteres, aunque el
    resto de la palabra sea identico (ej. 'SEMINRIOS' vs 'SEMINARIOS' cae de
    ~95% a 66.67% solo por el piso de n-gramas). Usarlo como min() habria
    reintroducido, con otro mecanismo, el mismo tipo de falso negativo que
    motivo el fix del 05-ago-2026. Se deja _similitud_ngramas() implementada
    y probada por si se retoma con un diseno mas robusto a inserciones/
    borrados (ej. n-gramas posicionales, o promediarlo en vez de tomar el
    minimo), pero no se usa en el calculo del score por ahora.
    """
    if not a or not b:
        return 0.0

    score_base = _score_ortografico_base(a, b)

    if " " not in a and " " not in b:
        return score_base  # una sola palabra cada una: nada que descontar

    fa, fb = _palabras_comunes_fuera(a, b, frecuencias=frecuencias, clases=clases)
    if not fa or not fb:
        return score_base  # una marca es casi subconjunto de la otra
    if _residuos_variante_corta(fa, fb):
        return score_base  # residuo corto y ademas variante de tipeo del otro

    score_residuo = _score_ortografico_base(fa, fb)
    return min(score_base, score_residuo)


def _similitud_fonetica(
    texto_a: str,
    texto_b: str,
    *,
    frecuencias: FrecuenciasPalabras | None = None,
    clases: list[int] | None = None,
) -> float:
    """Similitud fonetica 0-100, comparando texto original (no clave ya
    fusionada) para poder descontar palabras foneticamente genericas.

    Mismo problema que la senal ortografica: una palabra compartida (p. ej.
    'BEER' en dos marcas de cerveza) infla el ratio aunque el elemento
    distintivo de cada marca suene distinto. Se descuentan las palabras
    genericas (por clave fonetica compartida entre ambas marcas, o por
    frecuencia en la clase NCL del candidato: ver _palabras_comunes_fuera())
    antes de comparar.

    IMPORTANTE: texto_a y texto_b deben ser el texto CRUDO de la
    denominacion (con espacios), no el resultado de clave_fonetica(). Esta
    funcion calcula la clave fonetica internamente. Si se le pasa una clave
    ya fusionada, texto_a.split() la trata como una sola palabra y el
    descuento pareado deja de funcionar correctamente para ese lado de la
    comparacion (bug corregido el 17-jul-2026 en MotorBusqueda.buscar()).

    Al igual que en _similitud_ortografica, el resultado final es el minimo
    entre el score base (_score_fonetico_base, fix 06-ago-2026 PM: fuzz.
    ratio combinado con Jaro-Winkler) y el score sin las palabras genericas.
    Sin el minimo, el score sin comunes podria en teoria superar al score
    base (nada garantiza que acortar dos cadenas suba o baje su ratio de
    edicion), lo que rompe la invariante de la que depende
    MotorBusqueda.buscar() para su prefiltro: que el descuento de genericos
    nunca puede aumentar un score por encima del bruto calculado por cdist
    (bug corregido 03-ago-2026; hasta entonces esta funcion devolvia
    fuzz.ratio(fa, fb) directamente, sin el minimo, y ese caso no estaba
    cubierto por tests porque los universos de prueba son mas chicos que
    config.CANDIDATOS_PREFILTRO).

    Tampoco se aplica el descuento si el residuo fonetico es corto Y ademas
    se parece mucho al residuo del otro lado (variante de tipeo): ver
    _residuos_variante_corta(), fix 05-ago-2026 y su continuacion el
    06-ago-2026 PM. Si es corto pero es una clave fonetica distinta del otro
    lado, el descuento SI se aplica.

    NO se usa _similitud_ngramas() aqui: ver la nota al respecto en el
    docstring de _similitud_ortografica (misma razon, mismo fix 06-ago-2026
    PM revertido tras probarlo contra marcas reales).
    """
    if not texto_a or not texto_b:
        return 0.0

    clave_completa_a = normalizacion.clave_fonetica(texto_a)
    clave_completa_b = normalizacion.clave_fonetica(texto_b)
    score_base = _score_fonetico_base(clave_completa_a, clave_completa_b)

    wa, wb = texto_a.split(), texto_b.split()
    if len(wa) <= 1 and len(wb) <= 1:
        return score_base  # una sola palabra cada lado: nada que descontar

    claves_a = [normalizacion.clave_fonetica(w) for w in wa]
    claves_b = [normalizacion.clave_fonetica(w) for w in wb]
    fa, fb = _palabras_comunes_fuera(
        " ".join(claves_a), " ".join(claves_b),
        frecuencias=frecuencias, clases=clases,
    )

    if not fa or not fb:
        return score_base  # una marca es subconjunto fonetico de la otra
    if _residuos_variante_corta(fa, fb):
        return score_base  # residuo corto y ademas variante de tipeo del otro

    score_residuo = _score_fonetico_base(fa, fb)
    return min(score_base, score_residuo)


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
        canonico_ordenado = normalizacion.ordenar_tokens(canonico)
        clave_fonetica_consulta = normalizacion.clave_fonetica(consulta)
        clases_consulta = clases_consulta or []
        set_clases = {int(c) for c in clases_consulta}

        # canonicos_ordenados/frecuencias_* son atributos de la version real
        # de IndiceBusqueda (ver indice.py). Se leen con getattr() y un
        # fallback en vez de exigirlos siempre, para que dobles de prueba
        # simples (ver IndiceFalso en test_busqueda.py) sigan funcionando
        # sin tener que replicar toda la logica de indice.py: sin
        # frecuencias, el descuento de genericos usa solo el mecanismo por
        # lema compartido (comportamiento previo al fix 06-ago-2026 PM).
        canonicos_ordenados = getattr(idx, "canonicos_ordenados", None)
        if canonicos_ordenados is None:
            canonicos_ordenados = [normalizacion.ordenar_tokens(c) for c in idx.canonicos]
        frecuencias_ort = getattr(idx, "frecuencias_ortograficas", None)
        frecuencias_fon = getattr(idx, "frecuencias_foneticas", None)

        # --- Paso 1: scoring bruto vectorizado (sin descuento de genericos) ---
        # Cuatro llamados a cdist (dos por senal: la metrica original +
        # Jaro-Winkler, fix 06-ago-2026 PM) en vez de dos, pero cada uno
        # sigue siendo un solo llamado vectorizado en C++ contra las 218k
        # marcas: el tiempo total por consulta se mantiene por debajo de
        # 1 segundo (medido: ~0.11s, igual orden de magnitud que antes).
        # Jaro-Winkler.similarity devuelve 0-1, se escala a 0-100 para que
        # la combinacion con los pesos de config sea consistente con el
        # resto del modulo. Se usa idx.canonicos_ordenados (no idx.canonicos)
        # para que Jaro-Winkler reciba el mismo tratamiento de tolerancia al
        # reordenamiento de palabras que token_sort_ratio ya tiene
        # incorporado (ver normalizacion.ordenar_tokens y
        # _score_ortografico_base, que hace exactamente este mismo calculo
        # para un solo par en el recalculo exacto mas abajo).
        s_ort_ts = process.cdist(
            [canonico_ordenado], canonicos_ordenados, scorer=fuzz.ratio,
        )[0]
        s_ort_jw = process.cdist(
            [canonico_ordenado], canonicos_ordenados, scorer=JaroWinkler.similarity,
        )[0] * 100.0
        s_ort_bruto = (
            config.PESO_TOKEN_SORT_ORTOGRAFICO * s_ort_ts
            + config.PESO_JARO_WINKLER_ORTOGRAFICO * s_ort_jw
        )

        s_fon_ratio = process.cdist(
            [clave_fonetica_consulta], idx.foneticos, scorer=fuzz.ratio,
        )[0]
        s_fon_jw = process.cdist(
            [clave_fonetica_consulta], idx.foneticos, scorer=JaroWinkler.similarity,
        )[0] * 100.0
        s_fon_bruto = (
            config.PESO_RATIO_FONETICO * s_fon_ratio
            + config.PESO_JARO_WINKLER_FONETICO * s_fon_jw
        )

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
            clases_cand = [int(c) for c in idx.clases[i]]

            s_ort = _similitud_ortografica(
                canonico, cand_canonico,
                frecuencias=frecuencias_ort, clases=clases_cand,
            )
            # Se pasa 'consulta' cruda (no clave_fonetica(consulta)): ver
            # docstring de _similitud_fonetica y nota de fix mas arriba.
            s_fon = _similitud_fonetica(
                consulta, idx.nombres[i],
                frecuencias=frecuencias_fon, clases=clases_cand,
            )

            combinado = (
                config.PESO_ORTOGRAFICO * s_ort
                + config.PESO_FONETICO * s_fon
            )

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