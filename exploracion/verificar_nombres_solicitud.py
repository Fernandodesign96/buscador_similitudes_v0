import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from buscador import config

RAIZ = Path(__file__).resolve().parent.parent
obs = pd.read_excel(RAIZ / "data" / "observaciones_2025_parseadas.xlsx")
obs.columns = obs.columns.str.strip()
m10 = obs[obs["modulo"] == "M10"].copy()

grande = pd.read_excel(config.ARCHIVO_MARCAS)
grande.columns = grande.columns.str.strip()

# Derivar solicitud_base en el archivo grande (Nro_sol sin sufijo de clase)
nro = grande[config.COL_NRO_SOL].astype(str).str.strip()
clase = grande[config.COL_CLASE].astype(str).str.strip()
grande["solicitud_base"] = [
    int(n[:-len(c)]) if n.endswith(c) else int(n)
    for n, c in zip(nro, clase)
]

# File_Nbr de la observacion = solicitud_base (no Nro_sol completo)
nombres_por_base = (
    grande.dropna(subset=[config.COL_NOMBRE])
    .groupby("solicitud_base")[config.COL_NOMBRE]
    .first()
)

m10["nombre_solicitud"] = m10["File_Nbr"].astype(int).map(nombres_por_base)
con_nombre = m10["nombre_solicitud"].notna().sum()
print(f"Observaciones M10                 : {len(m10)}")
print(f"Con nombre de solicitud recuperado: {con_nombre} ({con_nombre/len(m10)*100:.1f}%)")
print("\nEjemplos (File_Nbr -> nombre de la solicitud rechazada):")
print(m10[m10["nombre_solicitud"].notna()][["File_Nbr", "nombre_solicitud"]].head(15).to_string(index=False))