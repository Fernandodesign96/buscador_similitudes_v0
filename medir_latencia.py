import time
from buscador.indice import IndiceBusqueda
from buscador.busqueda import MotorBusqueda

print("Cargando indice...")
t0 = time.time()
idx = IndiceBusqueda()
print(f"Indice cargado en {time.time()-t0:.1f}s, {len(idx)} marcas")

motor = MotorBusqueda(idx)
t0 = time.time()
resultados = motor.buscar("CHALLENGER", clases_consulta=[34])
print(f"Busqueda: {time.time()-t0:.3f}s")
for r in resultados[:5]:
    print(f"  {r.nombre} - score={r.score}")