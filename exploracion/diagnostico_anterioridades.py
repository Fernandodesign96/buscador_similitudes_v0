import re
import pandas as pd
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO_OBS = RAIZ / "data" / "observaciones_2025_parseadas.xlsx"
ARCHIVO_GRANDE = RAIZ / "data" / "Datos Marcas.xlsx"   # ajusta si difiere

obs = pd.read_excel(ARCHIVO_OBS)
obs.columns = obs.columns.str.strip()
m10 = obs[obs["modulo"] == "M10"]

patron = re.compile(r"[Rr]egistro[^\d]{0,15}0*(\d{5,8})")
citados = set()
for t in m10["texto_observacion"].dropna():
    citados.update(int(x) for x in patron.findall(t))

grande = pd.read_excel(ARCHIVO_GRANDE)
grande.columns = grande.columns.str.strip()

mark_codes_grande = set(grande["Mark Code (Ip Name)"].astype(int))

# Solicitudes base derivadas sobre TODO el archivo grande (sin filtrar estado)
nro = grande["Nro_sol"].astype(str).str.strip()
clase = grande["Nice Class Code"].astype(str).str.strip()
base_grande = set()
for n, c in zip(nro, clase):
    base_grande.add(int(n[:-len(c)]) if n.endswith(c) else int(n))

print("Universo de registros citados (anterioridades):", len(citados))
print()

hit_mc = citados & mark_codes_grande
hit_base = citados & base_grande
en_alguno = citados & (mark_codes_grande | base_grande)
print(f"Citados presentes en el archivo grande (cualquier estado):")
print(f"  por Mark Code        : {len(hit_mc)} ({len(hit_mc)/len(citados)*100:.1f}%)")
print(f"  por solicitud_base   : {len(hit_base)} ({len(hit_base)/len(citados)*100:.1f}%)")
print(f"  por cualquiera de los dos: {len(en_alguno)} ({len(en_alguno)/len(citados)*100:.1f}%)")

# De los que SI estan por solicitud_base, que estado tienen
print("\nEstado (Status Name) de las anterioridades que SI aparecen, por solicitud_base:")
grande2 = grande.copy()
grande2["solicitud_base"] = [
    int(n[:-len(c)]) if n.endswith(c) else int(n)
    for n, c in zip(nro, clase)
]
presentes = grande2[grande2["solicitud_base"].isin(citados)]
print(presentes["Status Name"].value_counts().head(15))

# Cuantos citados quedan completamente fuera del archivo
fuera = citados - (mark_codes_grande | base_grande)
print(f"\nCitados que NO estan en el archivo grande de ninguna forma: {len(fuera)} "
      f"({len(fuera)/len(citados)*100:.1f}%)")
print("Ejemplos:", sorted(fuera)[:15])