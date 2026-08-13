"""Validacion rapida usando el motor REAL de produccion (buscador/busqueda.py).

Historial de esta version (17-jul-2026):

v1 (original): usaba fuzz.token_sort_ratio puro sobre texto normalizado,
sin ningun descuento ni senal fonetica. Sobreestimaba el ruido de palabras
genericas y no reflejaba el motor real.

v2 (descartada): intento de correccion con una lista GLOBAL de palabras
genericas calculada por frecuencia (IDF) contra el universo de marcas.
Se descarta porque no es como funciona el motor real: busqueda.py no usa una
lista global, usa un DESCUENTO PAREADO (por cada par consulta-candidata,
quita las palabras exactas que comparten esos dos textos especificos, y
toma el minimo entre el score con y sin esas palabras). Son mecanismos
distintos; medir con una lista global no reproducia el comportamiento real
del motor.

v3 (esta version): usa directamente las funciones de produccion
(_similitud_ortografica, _similitud_fonetica de buscador.motor) combinadas
con los pesos reales de config.py (PESO_ORTOGRAFICO / PESO_FONETICO). Asi
esta validacion mide exactamente lo que el motor real le devolveria al
examinador, no una aproximacion.

Fix 17-jul-2026 (aplicado tambien en busqueda.py): _similitud_fonetica recibe
el texto CRUDO de la consulta (no clave_fonetica(consulta), que fusiona
todas las palabras en un solo bloque sin espacios y rompe el descuento
pareado del lado de la consulta para marcas multi-palabra). Este script se
actualizo en el mismo cambio que busqueda.py para no medir un comportamiento
distinto al que corre en produccion.

Problema de rendimiento y como se resuelve:
El motor real recorre el universo completo de ~218.369 marcas en un loop
Python por consulta (ver busqueda.py). Para miles de consultas eso es
inviable en validacion masiva. Se resuelve en dos etapas:

  1. PREFILTRO vectorizado (rapidfuzz.process.cdist, C++) con DOS senales
     baratas y sin descuento: token_sort_ratio ortografico y fuzz.ratio
     sobre la clave fonetica completa. Se toma la UNION de los top-K de
     cada senal por separado (no solo la ortografica), porque el descuento
     pareado real puede hacer que un candidato con score ortografico
     mediocre pero fonetico muy alto termine rankeando arriba, y un
     prefiltro solo-ortografico lo dejaria afuera antes de llegar a la
     etapa 2.

  2. RECALCULO EXACTO sobre esa union de candidatos: se llama a las mismas
     funciones que usa busqueda.py en produccion (descuento pareado +
     combinacion con los pesos reales), y se ordena por ese score final.

Nota: el descuento pareado del score final NUNCA puede ser mayor al score
base sin descuento (es un minimo). Por lo tanto, si un candidato quedo
fuera de la union de top-K del prefiltro (con scores SIN descuento, mas
altos o iguales a los que tendria con descuento), es matematicamente
imposible que el recalculo exacto lo hubiera rankeado mejor que los
candidatos que si pasaron el prefiltro. La union de top-K es un limite
superior seguro, no una aproximacion con riesgo de falso negativo por
el propio diseno del descuento (salvo el caso de clase_relacionada, que
esta version no aplica — ver limitaciones abajo).

Limitaciones de esta version (no implementadas, fuera de alcance por ahora):
  - No aplica la atenuacion por clase NCL no relacionada
    (config.FACTOR_CLASE_NO_RELACIONADA) porque requiere cruzar clases de
    la marca rechazada con las clases de cada candidata, y el Excel de
    rechazos no siempre trae la clase NCL en un formato directamente
    comparable con el de marcas_oponibles.parquet. Se puede agregar si
    se necesita.
  - Reproduce tal cual el posible doble-encoding fonetico de la consulta
    en busqueda.py (fonetico_consulta = clave_fonetica(consulta), pasado a
    una funcion que vuelve a aplicar clave_fonetica). No se corrige aqui:
    si es un bug, hay que corregirlo en busqueda.py, no solo en esta
    validacion, para no medir algo distinto de lo que corre en produccion.
"""
import argparse
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process

from buscador import config, normalizacion
from buscador.busqueda import _similitud_ortografica, _similitud_fonetica

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)

UMBRAL_ROJO = 75.0
UMBRAL_AMBAR = 50.0
TOP_PREFILTRO_DEFAULT = 50


def nivel(score):
    if score >= UMBRAL_ROJO:
        return "rojo"
    if score >= UMBRAL_AMBAR:
        return "ambar"
    return "verde"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("excel", type=Path)
    parser.add_argument("--salida", type=Path, default=None)
    parser.add_argument("--col-nombre", default="Mark_Name")
    parser.add_argument("--col-status", default="Status_Name")
    parser.add_argument("--valor-rechazada", default="Rechazada")
    parser.add_argument("--hoja", type=str, default=None,
                         help="Nombre de la pestana del Excel a leer (ej. 'Causal_H'). "
                              "Si no se especifica, lee la primera pestana del archivo, "
                              "lo cual es INCORRECTO si el archivo tiene varias pestanas "
                              "como el que genera filtrar_causal_h.py (usar --hoja Causal_H).")
    parser.add_argument("--top-n", type=int, default=5,
                         help="Candidatos finales a guardar por marca (default: 5)")
    parser.add_argument("--top-prefiltro", type=int, default=TOP_PREFILTRO_DEFAULT,
                         help="Candidatos que pasan de CADA senal del prefiltro "
                              f"vectorizado al recalculo exacto (default: {TOP_PREFILTRO_DEFAULT}). "
                              "El total real por consulta es la union de ambas senales, "
                              "hasta 2x este numero.")
    args = parser.parse_args()

    log.info("Cargando marcas oponibles...")
    marcas = pd.read_parquet(config.MARCAS_PROCESADAS)
    nombres_marcas = marcas["nombre"].tolist()
    canonicos_marcas = [normalizacion.limpiar(n) for n in nombres_marcas]
    claves_fon_marcas = [normalizacion.clave_fonetica(n) for n in nombres_marcas]
    log.info("Universo: %d marcas", len(canonicos_marcas))

    log.info("Cargando rechazos desde %s%s", args.excel,
              f" (hoja '{args.hoja}')" if args.hoja else " (primera hoja)")
    df = pd.read_excel(args.excel, sheet_name=args.hoja) if args.hoja else pd.read_excel(args.excel)
    df.columns = df.columns.str.strip()

    rechazadas = df[df[args.col_status] == args.valor_rechazada]
    nombres = (
        rechazadas[args.col_nombre]
        .dropna()
        .astype(str)
        .str.strip()
        .drop_duplicates()
        .tolist()
    )
    log.info("Marcas unicas a evaluar: %d", len(nombres))

    canonicos_consulta = [normalizacion.limpiar(n) for n in nombres]
    # Solo para el prefiltro vectorizado (etapa 1). El recalculo exacto
    # (etapa 2) usa el texto crudo 'nombre', no esta clave precomputada.
    claves_fon_consulta = [normalizacion.clave_fonetica(n) for n in nombres]

    top_prefiltro = max(args.top_prefiltro, args.top_n)
    top_n = max(1, args.top_n)

    log.info("Etapa 1/2: prefiltro vectorizado (ortografico + fonetico, universo completo)...")
    start = time.time()
    matriz_ort = process.cdist(canonicos_consulta, canonicos_marcas, scorer=fuzz.token_sort_ratio)
    matriz_fon = process.cdist(claves_fon_consulta, claves_fon_marcas, scorer=fuzz.ratio)
    log.info("Prefiltro completado en %.1fs", time.time() - start)

    log.info("Etapa 2/2: recalculo exacto (descuento pareado + score combinado real) "
             "sobre union de top-%d por senal...", top_prefiltro)
    start = time.time()
    resultados = []
    for i, nombre in enumerate(nombres):
        idx_ort = np.argsort(-matriz_ort[i])[:top_prefiltro]
        idx_fon = np.argsort(-matriz_fon[i])[:top_prefiltro]
        idx_candidatos = np.unique(np.concatenate([idx_ort, idx_fon]))

        canonico_consulta = canonicos_consulta[i]

        candidatos = []
        for j in idx_candidatos:
            j = int(j)
            s_ort = _similitud_ortografica(canonico_consulta, canonicos_marcas[j])
            # Texto crudo (no la clave fonetica pre-fusionada): ver nota de
            # fix en el docstring del modulo y en busqueda.py.
            s_fon = _similitud_fonetica(nombre, nombres_marcas[j])
            combinado = (
                config.PESO_ORTOGRAFICO * s_ort
                + config.PESO_FONETICO * s_fon
            )
            candidatos.append((combinado, nombres_marcas[j], s_ort, s_fon))

        candidatos.sort(key=lambda t: t[0], reverse=True)
        for rango, (score, nombre_cand, s_ort, s_fon) in enumerate(candidatos[:top_n], start=1):
            resultados.append({
                "marca_rechazada": nombre,
                "rango": rango,
                "mejor_match": nombre_cand,
                "score": round(score, 1),
                "score_ortografico": round(s_ort, 1),
                "score_fonetico": round(s_fon, 1),
                "nivel": nivel(score),
            })

        if (i + 1) % 250 == 0:
            log.info("  %d / %d marcas procesadas...", i + 1, len(nombres))

    log.info("Recalculo completado en %.1fs", time.time() - start)

    resultado_df = pd.DataFrame(resultados)

    top1_df = resultado_df[resultado_df["rango"] == 1]
    total = len(top1_df)
    conteo = top1_df["nivel"].value_counts()

    print()
    print("=" * 42)
    print("VALIDACION DE SENAL — RECHAZOS REALES")
    print("=" * 42)
    print(f"Rechazos evaluados: {total}")
    print(f"Motor: score combinado real (ortografico {config.PESO_ORTOGRAFICO} / "
          f"fonetico {config.PESO_FONETICO}), descuento pareado de busqueda.py")
    print(f"Prefiltro: union top-{top_prefiltro} ortografico + top-{top_prefiltro} fonetico")
    print(f"Candidatos guardados por marca: {top_n}")
    print("-" * 42)
    rojo  = conteo.get("rojo", 0)
    ambar = conteo.get("ambar", 0)
    verde = conteo.get("verde", 0)
    print(f"Rojo  (>={UMBRAL_ROJO:.0f}%): {rojo:4d}  ({rojo/total*100:5.1f}%)")
    print(f"Ambar (>={UMBRAL_AMBAR:.0f}%): {ambar:4d}  ({ambar/total*100:5.1f}%)")
    print(f"Verde  (<{UMBRAL_AMBAR:.0f}%): {verde:4d}  ({verde/total*100:5.1f}%)")
    print("-" * 42)
    print(f"Habria alertado (rojo+ambar): {(rojo+ambar)/total*100:.1f}%")

    if args.salida:
        resultado_df.to_excel(args.salida, index=False)
        log.info("Detalle (top-%d por marca) exportado a %s", top_n, args.salida)


if __name__ == "__main__":
    main()