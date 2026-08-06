"""Normalizacion de denominaciones de marca para busqueda de anterioridades.

Expone dos transformaciones, cada una al servicio de una senal de similitud:

- limpiar(): forma canonica ortografica (minusculas, sin acentos, sin
  puntuacion). Alimenta la comparacion ortografica (rapidfuzz) y sirve de
  entrada depurada al modelo de embeddings.

- clave_fonetica(): clave fonetica adaptada al espanol de Chile. Dos
  denominaciones homofonas producen la misma clave, lo que permite detectar
  similitud fonetica (p. ej. CAUQUENES / KAUKENES).

Reglas foneticas (espanol de Chile) -- auditables
--------------------------------------------------
Codifican equivalencias de pronunciacion reconocidas en el examen de marcas:

  - Seseo:    c (ante e,i), z, s     -> /s/   (cebra = sebra, zapato = sapato)
  - C dura:   c (ante a,o,u), qu, k  -> /k/   (casa = kasa, queso = keso)
  - G suave:  g (ante e,i)           -> /x/   (gente = jente)
  - G dura:   g (ante a,o,u), gu+e/i -> /g/   (guerra = /gera/)
  - Yeismo:   ll, y                  -> /j/   (llave = yave)
  - B = V:    b, v                   -> /b/   (baca = vaca)
  - H muda:   h se elimina (salvo 'ch')       (hola = ola, hecho = echo)
  - CH:       fonema unico
  - N tilde:  se conserva como fonema propio
  - Dobles:   letras repetidas se colapsan    (carro -> /karo/)

Limitaciones conocidas (aproximaciones documentadas)
----------------------------------------------------
  - La dieresis (ue con dos puntos) se pierde al remover acentos: 'gue/gui'
    con dieresis se trata como u muda (caso infrecuente en marcas).
  - 'x' se aproxima a /ks/ y 'w' a /u/ (letras de baja frecuencia, origen
    extranjero).
  - Los digitos no tienen representacion fonetica: una marca puramente
    numerica produce clave vacia (la similitud la cubren las otras senales).
"""
from __future__ import annotations

import re
import unicodedata

from . import config

__all__ = ["limpiar", "clave_fonetica", "lema", "ordenar_tokens"]

_RE_NO_ALFANUM = re.compile(r"[^a-z0-9ñ ]+")
_RE_ESPACIOS = re.compile(r"\s+")
_RE_SOLO_LETRAS = re.compile(r"[^a-zñ]")
_RE_GU_EI = re.compile(r"gu([ei])")
_RE_G_EI = re.compile(r"g([ei])")
_RE_C_EI = re.compile(r"c([ei])")
_RE_DOBLES = re.compile(r"(.)\1+")
# 'y' precedida de vocal y al final de palabra actua como semivocal /i/ que
# cierra un diptongo (rey, ley, buey, paraguay), no como consonante yeista
# (yave, mayo). Debe aplicarse ANTES de fusionar palabras (necesita el
# espacio o el fin de cadena para saber donde termina la palabra).
_RE_Y_DIPTONGO = re.compile(r"([aeiou])y(?=\s|$)")


def _quitar_acentos(texto: str) -> str:
    """Remueve diacriticos preservando la enie como letra propia."""
    texto = texto.replace("ñ", "\x00")
    descompuesto = unicodedata.normalize("NFD", texto)
    sin_marcas = "".join(c for c in descompuesto if not unicodedata.combining(c))
    return sin_marcas.replace("\x00", "ñ")


def limpiar(texto: str | None) -> str:
    """Devuelve la forma canonica ortografica de una denominacion.

    Minusculas, sin acentos (la enie se conserva), sin puntuacion, con
    espacios colapsados. Conserva los digitos.

    Args:
        texto: denominacion de marca (puede ser None o no-str).

    Returns:
        Cadena canonica; cadena vacia si la entrada es vacia o None.
    """
    if texto is None:
        return ""
    texto = str(texto).lower()
    texto = _quitar_acentos(texto)
    texto = _RE_NO_ALFANUM.sub(" ", texto)
    return _RE_ESPACIOS.sub(" ", texto).strip()


def clave_fonetica(texto: str | None) -> str:
    """Devuelve la clave fonetica (espanol de Chile) de una denominacion.

    Dos denominaciones homofonas producen la misma clave. Ver el encabezado
    del modulo para el detalle de las reglas y sus limitaciones.

    Args:
        texto: denominacion de marca.

    Returns:
        Clave fonetica en minusculas; cadena vacia si no hay contenido
        alfabetico (p. ej. marcas puramente numericas).
    """
    limpio_con_espacios = limpiar(texto)
    # Regla vocalica de 'y' final de palabra: debe correr mientras los
    # espacios todavia delimitan cada palabra (se pierden en el paso
    # siguiente). Ej.: "rey carlos" -> "rei carlos".
    limpio_con_espacios = _RE_Y_DIPTONGO.sub(r"\1i", limpio_con_espacios)
    s = _RE_SOLO_LETRAS.sub("", limpio_con_espacios)
    if not s:
        return ""

    # Digrafos y contextos. Se usan sentinelas en mayuscula para impedir que
    # una sustitucion vuelva a ser capturada por una regla posterior.
    s = s.replace("ch", "X")          # /tʃ/
    s = s.replace("ll", "Y")          # yeismo /ʝ/
    s = s.replace("qu", "K")          # /k/
    s = _RE_GU_EI.sub(r"G\1", s)      # gue/gui -> g dura
    s = _RE_G_EI.sub(r"J\1", s)       # ge/gi   -> jota
    s = s.replace("g", "G")           # g dura restante
    s = _RE_C_EI.sub(r"S\1", s)       # ce/ci   -> seseo
    s = s.replace("c", "K")           # c dura restante
    s = s.replace("q", "K")           # q residual
    s = s.replace("z", "S")           # seseo
    s = s.replace("v", "B")           # b = v
    s = s.replace("w", "u")           # aproximacion
    s = s.replace("x", "ks")          # aproximacion
    s = s.replace("y", "Y")           # yeismo
    s = s.replace("h", "")            # h muda (ch ya protegido)

    s = s.lower()                     # unifica sentinelas al alfabeto fonetico
    return _RE_DOBLES.sub(r"\1", s)   # colapsa letras repetidas


_VOCALES = frozenset("aeiouñ")


def lema(palabra: str) -> str:
    """Singularizacion naive de una palabra: quita la 's' final de plural
    cuando va precedida de vocal (cervezas -> cerveza, casas -> casa, rosas
    -> rosa, marcas -> marca), que es el patron de plural mas frecuente del
    espanol. No intenta el patron consonante + 'es' (flores -> flor):
    distinguirlo del caso "la palabra ya terminaba en 'es'" (clases ->
    clase) sin diccionario es ambiguo, y una regla equivocada podria fusionar
    palabras que no deberian considerarse la misma.

    Se usa en busqueda.py tanto para decidir que palabras cuentan como
    "la misma" al detectar terminos comunes/genericos entre dos marcas (fix
    06-ago-2026 AM, caso 'cervezas ricas' vs 'cerveza tribal'), como para
    calcular la frecuencia de cada palabra en el universo de marcas (fix
    06-ago-2026 PM, ponderacion por genericidad segun frecuencia de corpus).
    Vive en este modulo (no en busqueda.py) porque tanto busqueda.py como
    indice.py la necesitan, y busqueda.py ya importa indice.py: ponerla en
    busqueda.py crearia un import circular.

    Args:
        palabra: una palabra individual (no una frase completa).

    Returns:
        La palabra singularizada si aplica la regla; si no, la palabra sin
        modificar.
    """
    if (
        len(palabra) >= config.LONGITUD_MINIMA_PALABRA_LEMA
        and palabra.endswith("s")
        and palabra[-2] in _VOCALES
    ):
        return palabra[:-1]
    return palabra


def ordenar_tokens(texto: str) -> str:
    """Ordena alfabeticamente las palabras de una cadena y las vuelve a unir
    con un espacio.

    Reproduce el preprocesamiento que rapidfuzz.fuzz.token_sort_ratio hace
    internamente. Se necesita como funcion propia (no solo implicita dentro
    de token_sort_ratio) porque busqueda.py combina esa metrica con
    Jaro-Winkler (fix 06-ago-2026 PM), que a diferencia de token_sort_ratio
    no reordena tokens por si solo: para que ambas reciban el mismo
    tratamiento de tolerancia al reordenamiento de palabras (ej. 'CASA
    BLANCA' / 'BLANCA CASA'), hay que ordenarlas ANTES de pasarlas a
    cualquiera de las dos metricas. indice.py tambien la usa para
    precalcular la forma ordenada de cada marca una sola vez al cargar el
    indice, en vez de reordenar el universo completo en cada consulta.
    """
    return " ".join(sorted(texto.split()))