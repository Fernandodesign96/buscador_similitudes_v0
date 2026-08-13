import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from buscador.indice import IndiceBusqueda
from buscador.busqueda import MotorBusqueda

indice = IndiceBusqueda()
motor = MotorBusqueda(indice)

for consulta, clases in [("CHALLENGER", [34]), ("KAUKENES", [33]), ("SOLYMAR", [25])]:
    print(f"\n=== {consulta} (clases {clases}) ===")
    for r in motor.buscar(consulta, clases_consulta=clases, top=5):
        print(f"  {r.score:6.2f}  {r.nombre[:30]:30}  clases={str(r.clases)[:20]:20}  "
              f"sem={r.score_semantico:5.1f} ort={r.score_ortografico:5.1f} "
              f"fon={r.score_fonetico:5.1f} rel={'si' if r.clase_relacionada else 'no'}")