"""API Flask del buscador de anterioridades.

Expone el motor de busqueda por similitud denominativa para uso publico:
un solicitante ingresa una denominacion y recibe las marcas ya inscritas
mas similares, con su porcentaje de similitud.

Uso:
    python api.py
"""
from __future__ import annotations

import logging
import os

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
logger.info("Buscador listo.")


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


@app.get("/api/buscar")
def buscar():
    """Busca anterioridades para una denominacion.

    Query params:
        q      (str, requerido): denominacion a evaluar.
        clases (str, opcional): clases NCL separadas por coma (ej. "25,35").
        top    (int, opcional): numero de resultados (default config.TOP_RESULTADOS).
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

    try:
        top = int(request.args.get("top", config.TOP_RESULTADOS))
    except ValueError:
        top = config.TOP_RESULTADOS

    resultados = _motor.buscar(consulta, clases_consulta=clases, top=top)
    return jsonify({
        "consulta": consulta,
        "clases": clases,
        "resultados": [
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
        ],
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)