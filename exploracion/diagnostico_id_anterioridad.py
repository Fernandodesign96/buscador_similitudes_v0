import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import re
import pandas as pd
from buscador import config

RAIZ = Path(__file__).resolve().parent.parent
obs = pd.read_excel(RAIZ / "data" / "observaciones_2025_parseadas.xlsx")
obs.columns = obs.columns.str.strip()
m10 = obs[obs["modulo"] == "M10"]

marcas = pd.read_parquet(config.MARCAS_PROCESADAS)

# Tomamos casos donde el texto cita "Registro NNNN. NOMBRE." y verificamos
# si el NOMBRE citado coincide con el nombre de la marca que tiene ese numero
# como mark_code o como solicitud_base.
patron = re.compile(r"[Rr]egistro[^\d]{0,15}0*(\d{5,8})[.\s;nbs]*([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ0-9\s]{2,30})")

mark_por_code = dict(zip(marcas["mark_code"].astype(int), marcas["nombre"]))
nombre_por_base = {}
for _, f in marcas.iterrows():
    for s in f["solicitudes"]:
        nombre_por_base[int(s)] = f["nombre"]

def norm(s):
    return re.sub(r"[^a-z]", "", str(s).lower())

coincide_code = coincide_base = total = 0
ejemplos = []
for t in m10["texto_observacion"].dropna():
    for num_str, nombre_citado in patron.findall(t):
        num = int(num_str)
        nc = norm(nombre_citado)
        if len(nc) < 3:
            continue
        total += 1
        n_code = norm(mark_por_code.get(num, ""))
        n_base = norm(nombre_por_base.get(num, ""))
        ok_code = n_code and (nc in n_code or n_code in nc)
        ok_base = n_base and (nc in n_base or n_base in nc)
        if ok_code:
            coincide_code += 1
        if ok_base:
            coincide_base += 1
        if len(ejemplos) < 12:
            ejemplos.append((num, nombre_citado.strip()[:20],
                             mark_por_code.get(num, "-"),
                             nombre_por_base.get(num, "-")))
        if total >= 3000:
            break
    if total >= 3000:
        break

print(f"Citas analizadas (numero + nombre): {total}")
print(f"  nombre citado coincide con mark_code : {coincide_code} ({coincide_code/total*100:.1f}%)")
print(f"  nombre citado coincide con sol_base  : {coincide_base} ({coincide_base/total*100:.1f}%)")
print("\nEjemplos (num citado | nombre citado | nombre via mark_code | nombre via sol_base):")
for num, cit, vc, vb in ejemplos:
    print(f"  {num:>10} | {cit:20} | {str(vc)[:20]:20} | {str(vb)[:20]}")