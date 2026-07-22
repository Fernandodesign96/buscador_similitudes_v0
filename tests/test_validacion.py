"""Tests de la logica de validacion (preparacion de casos y conteo de recall)."""
from __future__ import annotations

from dataclasses import dataclass

from buscador.validacion import CasoValidacion, evaluar


@dataclass
class ResultadoFake:
    solicitudes: list


class MotorFake:
    """Motor que devuelve resultados predefinidos por nombre consultado."""
    def __init__(self, mapa):
        self._mapa = mapa  # nombre -> lista de listas de solicitudes_base

    def buscar(self, consulta, clases_consulta=None, top=10):
        listas = self._mapa.get(consulta, [])
        return [ResultadoFake(solicitudes=s) for s in listas[:top]]


def test_acierto_en_top1():
    casos = [CasoValidacion(1, "MARCA X", [25], {999})]
    motor = MotorFake({"MARCA X": [[999], [111], [222]]})
    r = evaluar(casos, motor, tops=(1, 3))
    assert r.aciertos[1] == 1
    assert r.recall[1] == 1.0


def test_acierto_en_top3_no_top1():
    casos = [CasoValidacion(1, "MARCA X", [25], {999})]
    motor = MotorFake({"MARCA X": [[111], [222], [999]]})
    r = evaluar(casos, motor, tops=(1, 3))
    assert r.aciertos[1] == 0
    assert r.aciertos[3] == 1


def test_no_acierto():
    casos = [CasoValidacion(1, "MARCA X", [25], {999})]
    motor = MotorFake({"MARCA X": [[111], [222]]})
    r = evaluar(casos, motor, tops=(1, 3))
    assert r.aciertos[1] == 0
    assert r.aciertos[3] == 0


def test_recall_agregado_varios_casos():
    casos = [
        CasoValidacion(1, "A", [1], {10}),
        CasoValidacion(2, "B", [1], {20}),
    ]
    motor = MotorFake({"A": [[10]], "B": [[99]]})
    r = evaluar(casos, motor, tops=(1,))
    assert r.aciertos[1] == 1
    assert r.recall[1] == 0.5