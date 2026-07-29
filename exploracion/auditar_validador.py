import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from buscador import config, validacion
from buscador.busqueda import MotorBusqueda
from buscador.indice import IndiceBusqueda

OBS = config.DATA_DIR / "observaciones_2025_parseadas.xlsx"
marcas = pd.read_parquet(config.MARCAS_PROCESADAS)

casos = validacion.preparar_casos(OBS, marcas)
print(f"Casos preparados: {len(casos)}")

# 1. Inspeccionar un caso conocido: SKAL LA PUREZA DEL AGUA -> registro 1300466
print("\n--- Tipos en un caso ---")
c = casos[0]
print("nombre_solicitud:", repr(c.nombre_solicitud))
print("clases:", c.clases, [type(x).__name__ for x in c.clases])
print("anterioridades_base:", c.anterioridades_base,
      [type(x).__name__ for x in c.anterioridades_base])

# 2. Esa anterioridad, ¿esta indexada? ¿con que solicitud_base?
print("\n--- ¿La anterioridad citada existe como marca indexada? ---")
for ant in c.anterioridades_base:
    hit = marcas[marcas["solicitudes"].apply(lambda lst: ant in {int(s) for s in lst})]
    if len(hit):
        fila = hit.iloc[0]
        print(f"  base {ant} -> marca '{fila['nombre']}' clases={[int(x) for x in fila['clases']]}")
    else:
        print(f"  base {ant} -> NO encontrada en marcas indexadas")

# 3. Correr el buscador para ese caso y ver que tipos devuelve
print("\n--- Resultados del buscador para el caso 0 ---")
motor = MotorBusqueda(IndiceBusqueda())
res = motor.buscar(c.nombre_solicitud, clases_consulta=c.clases, top=10)
for r in res[:10]:
    sols = {int(s) for s in r.solicitudes}
    match = "<-- MATCH" if (c.anterioridades_base & sols) else ""
    print(f"  {r.score:6.2f} {r.nombre[:30]:30} bases={sorted(sols)[:3]} "
          f"tipos={[type(s).__name__ for s in r.solicitudes][:1]} {match}")