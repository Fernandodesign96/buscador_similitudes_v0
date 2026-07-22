import pandas as pd
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO = RAIZ / "data" / "Datos Marcas.xlsx"   # ajusta extension si corresponde

df = pd.read_excel(ARCHIVO)
df.columns = df.columns.str.strip()

conteo = (df["Status Name"]
          .value_counts(dropna=False)
          .rename_axis("Status Name")
          .reset_index(name="cantidad"))
conteo["oponible"] = ""   # <-- la llenas tu: S / N

pd.set_option("display.max_rows", None)
pd.set_option("display.max_colwidth", None)
print(conteo[["Status Name", "cantidad"]].to_string(index=False))

salida = RAIZ / "data" / "estados_para_clasificar.xlsx"
conteo.to_excel(salida, index=False)
print(f"\nExportado: {salida}")
print("Llena la columna 'oponible' con S (es anterioridad) o N (no lo es).")