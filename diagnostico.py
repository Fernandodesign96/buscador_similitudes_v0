from buscador.indice import IndiceBusqueda
from buscador.busqueda import MotorBusqueda

idx = IndiceBusqueda()
motor = MotorBusqueda(idx)

resultados = motor.buscar("CHALLENGER", clases_consulta=[34])

print("Top 5 con detalle completo:")
for r in resultados[:5]:
    print(f"  nombre={r.nombre!r}")
    print(f"    mark_code={r.mark_code}")
    print(f"    clases={r.clases}")
    print(f"    clase_relacionada={r.clase_relacionada}")
    print(f"    score_ortografico={r.score_ortografico}")
    print(f"    score_fonetico={r.score_fonetico}")
    print(f"    score_combinado={r.score}")
    print()

# Ademas: cuantas marcas se llaman exactamente "CHALLENGER" en el indice?
exactas = [i for i, n in enumerate(idx.nombres) if n.strip().upper() == "CHALLENGER"]
print(f"Marcas con nombre exacto 'CHALLENGER': {len(exactas)}")
for i in exactas:
    print(f"  mark_code={idx.mark_codes[i]}, clases={idx.clases[i]}, canonico={idx.canonicos[i]!r}, fonetico={idx.foneticos[i]!r}")