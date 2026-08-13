import re
import pandas as pd
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO_OBS = RAIZ / "data" / "observaciones_2025_parseadas.xlsx"
MARCAS = RAIZ / "data" / "marcas_oponibles.parquet"
ARCHIVO_GRANDE = RAIZ / "data" / "Datos Marcas.xlsx"   # ajusta el nombre si difiere

# --- 1. Registros citados en M10 ------------------------------------------
obs = pd.read_excel(ARCHIVO_OBS)
obs.columns = obs.columns.str.strip()
m10 = obs[obs["modulo"] == "M10"]

patron = re.compile(r"[Rr]egistro[^\d]{0,15}0*(\d{5,8})")
citados = set()
for t in m10["texto_observacion"].dropna():
    citados.update(int(x) for x in patron.findall(t))
print(f"Registros citados unicos (anterioridades): {len(citados)}")

# --- 2. Candidatos de ID en la base de marcas agrupada --------------------
marcas = pd.read_parquet(MARCAS)
mark_codes = set(marcas["mark_code"].astype(int))
solicitudes_base = set()
for lst in marcas["solicitudes"]:
    solicitudes_base.update(int(x) for x in lst)

print("\nMatch de los registros citados contra la base de marcas agrupada:")
hit_mc = citados & mark_codes
hit_sb = citados & {int(s) for s in solicitudes_base}
print(f"  vs mark_code      : {len(hit_mc)} de {len(citados)} ({len(hit_mc)/len(citados)*100:.1f}%)")
print(f"  vs solicitud_base : {len(hit_sb)} de {len(citados)} ({len(hit_sb)/len(citados)*100:.1f}%)")

# --- 3. Contra el archivo grande crudo (todas las filas, todos los Nro_sol)-
grande = pd.read_excel(ARCHIVO_GRANDE)
grande.columns = grande.columns.str.strip()
nro_sol_full = set(grande["Nro_sol"].astype(int))
mark_code_full = set(grande["Mark Code (Ip Name)"].astype(int))

hit_nro_full = citados & nro_sol_full
hit_mc_full = citados & mark_code_full
print("\nMatch contra el archivo grande crudo (todas las marcas, no solo Registradas):")
print(f"  vs Nro_sol completo : {len(hit_nro_full)} de {len(citados)} ({len(hit_nro_full)/len(citados)*100:.1f}%)")
print(f"  vs Mark Code        : {len(hit_mc_full)} de {len(citados)} ({len(hit_mc_full)/len(citados)*100:.1f}%)")

# --- 4. Ejemplos para inspeccion visual -----------------------------------
print("\nEjemplos de registros citados que NO matchean con mark_code:")
no_match = sorted(citados - mark_codes)[:10]
print(no_match)
print("\nEjemplos de mark_code reales en la base:")
print(sorted(mark_codes)[:10])