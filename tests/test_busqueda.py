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
from buscador.busqueda import _score_fonetico_base
from buscador.busqueda import _score_ortografico_base
from buscador.busqueda import _similitud_fonetica
from buscador.busqueda import _similitud_ngramas
from buscador.busqueda import _similitud_ortografica
from buscador.indice import FrecuenciasPalabras


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


def test_palabra_generica_en_plural_tambien_se_descuenta():
    # Caso reportado 06-ago-2026: "cervezas ricas" vs "cerveza tribal" daba
    # 77% pese a no tener relacion real, porque "cervezas" (plural) no
    # coincidia EXACTO con "cerveza" (singular) y el descuento nunca se
    # activaba. "ricas" y "tribal" no se parecen: el score con el generico
    # en plural descontado debe acercarse al score sin el generico en
    # absoluto (singular), y quedar bien por debajo del score bruto (que
    # incluye "cerveza"/"cervezas" sin descontar).
    s_bruto = _similitud_ortografica("cervezas", "cerveza")  # referencia
    assert s_bruto > 85.0  # confirma que son casi la misma palabra

    s_con_plural = _similitud_ortografica("cervezas ricas", "cerveza tribal")
    s_sin_generico = _similitud_ortografica("ricas", "tribal")
    assert s_con_plural == pytest.approx(s_sin_generico, abs=0.5)


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

    El "bruto" de referencia usa _score_fonetico_base(), no fuzz.ratio()
    directo: desde el fix 06-ago-2026 PM ese es el calculo real que hace el
    prefiltro vectorizado de MotorBusqueda.buscar() (fuzz.ratio combinado
    con Jaro-Winkler, no fuzz.ratio solo), asi que es la cota superior real
    contra la que hay que verificar el invariante.
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
        score_bruto = _score_fonetico_base(
            normalizacion.clave_fonetica(a), normalizacion.clave_fonetica(b),
        )
        score_exacto = _similitud_fonetica(a, b)
        assert score_exacto <= score_bruto + 1e-9, (a, b, score_exacto, score_bruto)


def test_residuo_corto_no_castiga_variante_casi_identica():
    # Caso reportado 05-ago-2026: "brasas del rey" vs "brasas del rei".
    # Tras descontar "brasas" y "del" (comunes), el residuo "rey"/"rei" (3
    # caracteres) es demasiado corto para que el ratio sea confiable: se
    # omite el descuento y se usa el score base (bruto, sin descontar).
    s_ort = _similitud_ortografica(
        normalizacion.limpiar("brasas del rey"),
        normalizacion.limpiar("brasas del rei"),
    )
    s_fon = _similitud_fonetica("brasas del rey", "brasas del rei")
    assert s_ort > 90.0
    assert s_fon > 90.0


def test_residuo_largo_sigue_descontandose():
    # Control: si el residuo tras descontar comunes es largo (>= al piso),
    # el descuento de genericos sigue aplicandose como antes.
    s_con = _similitud_ortografica("skaal beer", "svajg beer")
    s_sin = _similitud_ortografica("skaal", "svajg")
    assert s_con == pytest.approx(s_sin, abs=0.5)


def test_genericidad_por_frecuencia_no_requiere_coincidencia_exacta():
    # Caso reportado 06-ago-2026 PM: "cerveza"/"cervezas" son genericas
    # PARA LA CLASE 32 por su frecuencia en el universo, sin necesidad de
    # que ambas marcas la compartan literalmente (ya se resolvia el caso
    # exacto/plural con el fix de la mañana; esto generaliza a cualquier
    # termino frecuente en la clase real del candidato).
    frecuencias = FrecuenciasPalabras(
        conteo_por_clase={32: {"cerveza": 50}},
        total_por_clase={32: 100},
    )
    s_con_generico = _similitud_ortografica(
        "cervezas ricas", "cerveza tribal",
        frecuencias=frecuencias, clases=[32],
    )
    s_sin_generico = _similitud_ortografica("ricas", "tribal")
    assert s_con_generico == pytest.approx(s_sin_generico, abs=0.5)


def test_genericidad_por_frecuencia_respeta_piso_de_conteo_y_clase():
    # Sin clases del candidato, o con una clase demasiado chica para
    # superar config.CONTEO_MINIMO_GENERICO, no se descuenta nada: evita
    # que una clase con pocas marcas produzca porcentajes ruidosos.
    frecuencias = FrecuenciasPalabras(
        conteo_por_clase={32: {"cerveza": 3}},  # bajo el piso de conteo (20)
        total_por_clase={32: 10},
    )
    assert frecuencias.es_generica("cerveza", [32]) is False
    assert frecuencias.es_generica("cerveza", None) is False
    assert frecuencias.es_generica("cerveza", []) is False


def test_typo_en_palabra_distintiva_no_se_castiga_por_genericos_alrededor():
    """Caso reportado 06-ago-2026 PM: en un nombre largo donde varias
    palabras son genericas por frecuencia, el descuento las quita a todas
    dejando solo la palabra con el error de tipeo como residuo. Un error de
    una sola letra en esa palabra (10 caracteres) no deberia hacer caer el
    score a ~67% (eso fue precisamente el bug que motivo revertir el piso
    de n-gramas, ver docstring del modulo: 'SEMINRIOS' vs 'SEMINARIOS').
    """
    frecuencias = FrecuenciasPalabras(
        conteo_por_clase={41: {
            "insight": 40, "mejor": 40, "persona": 40, "resultado": 40,
        }},
        total_por_clase={41: 100},
    )
    a = normalizacion.limpiar("SEMINRIOS INSIGHT MEJORES PERSONAS MEJORES RESULTADOS")
    b = normalizacion.limpiar("SEMINARIOS INSIGHT MEJORES PERSONAS MEJORES RESULTADOS")
    s = _similitud_ortografica(a, b, frecuencias=frecuencias, clases=[41])
    assert s > 90.0


def test_jaro_winkler_favorece_coincidencia_de_inicio():
    # Dos pares con la misma distancia de edicion (una sustitucion), uno
    # difiere al inicio de la palabra y el otro al final: Jaro-Winkler da
    # un bono al prefijo compartido, asi que el que difiere al final debe
    # obtener un score igual o mayor.
    s_dif_inicio = _score_ortografico_base("xolgar", "solgar")
    s_dif_final = _score_ortografico_base("solgar", "solgax")
    assert s_dif_final >= s_dif_inicio


def test_similitud_ngramas_identicas_da_100():
    assert _similitud_ngramas("solgar", "solgar") == 100.0


def test_similitud_ngramas_cadena_corta_no_restringe():
    # Por debajo de config.LONGITUD_MINIMA_RESIDUO_DESCUENTO, no es una
    # señal confiable (ver docstring de _similitud_ngramas): no debe
    # devolver 0 aunque las cadenas no compartan ningun trigrama.
    assert _similitud_ngramas("rey", "rei") == 100.0


def test_similitud_ngramas_detecta_insercion_como_baja_similitud():
    # Documenta por que no se usa como piso en el pipeline (ver docstring
    # del modulo): una insercion de una letra puede hacer caer el
    # coeficiente de Dice bastante mas de lo que cae token_sort_ratio para
    # el mismo par.
    assert _similitud_ngramas("seminrios", "seminarios") < 70.0
    assert _score_ortografico_base("seminrios", "seminarios") > 90.0


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