"""API Flask del buscador de anterioridades.

Expone el motor de busqueda por similitud denominativa para uso publico:
un solicitante ingresa una denominacion y recibe las marcas ya inscritas
mas similares, con su porcentaje de similitud.

Uso:
    python api.py
"""
from __future__ import annotations

import logging
import math
import os
import time

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from flask import Flask, jsonify, request, send_from_directory

from buscador import config
from buscador.busqueda import MotorBusqueda
from buscador.indice import IndiceBusqueda

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(levelname)-7s  %(name)s | %(message)s",
                    datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=None)

logger.info("Cargando indice y motor (una sola vez al arrancar)...")
_motor = MotorBusqueda(IndiceBusqueda())
_inicio = time.time()
logger.info("Buscador listo.")


def _serializar_resultados(resultados):
    return [
        {
            "nombre": r.nombre,
            "clases": r.clases,
            "similitud": r.score,
            "desglose": {
                "ortografica": r.score_ortografico,
                "fonetica": r.score_fonetico,
            },
            "clase_relacionada": r.clase_relacionada,
        }
        for r in resultados
    ]


def _filtrar_por_clases_estricto(resultados, clases: list[int]):
    """Opcion B: solo marcas que comparten al menos una clase NCL."""
    if not clases:
        return resultados
    set_clases = set(clases)
    return [r for r in resultados if set_clases & set(r.clases)]


def _filtrar_por_similitud_minima(resultados, min_score: float):
    """Solo marcas con score combinado >= min_score (porcentaje)."""
    if min_score <= 0:
        return resultados
    return [r for r in resultados if r.score >= min_score]


def _paginar(resultados, page: int, per_page: int):
    total = len(resultados)
    total_pages = max(1, math.ceil(total / per_page)) if total else 0
    page = max(1, min(page, total_pages)) if total_pages else 1
    offset = (page - 1) * per_page
    return resultados[offset:offset + per_page], total, page, per_page, total_pages


@app.get("/")
def index():
    return send_from_directory(str(config.RAIZ), "index.html")


@app.get("/uploads/<path:filename>")
def uploads(filename):
    """Sirve archivos estaticos referenciados por index.html (logo, etc.).

    Necesario porque la app se crea con static_folder=None (no hay manejo
    automatico de estaticos de Flask); sin esta ruta, cualquier <img
    src="uploads/..."> en index.html devuelve 404 aunque el archivo exista
    en disco.
    """
    return send_from_directory(str(config.RAIZ / "uploads"), filename)


@app.get("/api/health")
def health():
    """Estado del servicio para monitoreo."""
    return jsonify({
        "status": "ok",
        "marcas_cargadas": len(_motor.indice),
        "uptime_seconds": round(time.time() - _inicio, 1),
    })


@app.get("/api/buscar")
def buscar():
    """Busca anterioridades para una denominacion.

    Query params:
        q           (str, requerido): denominacion a evaluar.
        clases      (str, opcional): clases NCL separadas por coma (ej. "25,35").
        top         (int, opcional): numero de resultados del motor (default config.TOP_RESULTADOS).
        modo_clases (str, opcional): "atenuar" (default) o "filtrar" (excluye sin clase en comun).
        page        (int, opcional): pagina para listados (default 1).
        per_page    (int, opcional): resultados por pagina, 10 o 20 (default 20).
        similitud_min (float, opcional): porcentaje minimo de similitud (default 0).
    """
    consulta = (request.args.get("q") or "").strip()
    if not consulta:
        return jsonify({"error": "Falta el parametro 'q'."}), 400

    clases_raw = (request.args.get("clases") or "").strip()
    clases = []
    if clases_raw:
        try:
            clases = [int(c) for c in clases_raw.split(",") if c.strip()]
        except ValueError:
            return jsonify({"error": "Parametro 'clases' invalido."}), 400

    modo_clases = (request.args.get("modo_clases") or "atenuar").strip().lower()
    if modo_clases not in ("atenuar", "filtrar"):
        return jsonify({"error": "Parametro 'modo_clases' invalido."}), 400

    try:
        top = int(request.args.get("top", config.TOP_RESULTADOS))
    except ValueError:
        top = config.TOP_RESULTADOS

    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1

    try:
        per_page = int(request.args.get("per_page", 20))
    except ValueError:
        per_page = 20
    if per_page not in (10, 20):
        per_page = 20

    try:
        similitud_min = float(request.args.get("similitud_min", 0))
    except ValueError:
        similitud_min = 0

    resultados = _motor.buscar(consulta, clases_consulta=clases, top=top)

    if modo_clases == "filtrar":
        resultados = _filtrar_por_clases_estricto(resultados, clases)

    resultados = _filtrar_por_similitud_minima(resultados, similitud_min)

    paginados, total, page, per_page, total_pages = _paginar(
        resultados, page, per_page,
    )

    return jsonify({
        "consulta": consulta,
        "clases": clases,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "resultados": _serializar_resultados(paginados),
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)