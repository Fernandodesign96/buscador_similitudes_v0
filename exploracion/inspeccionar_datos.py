import pandas as pd
from pathlib import Path

# Raiz del proyecto: la carpeta padre de /exploracion
RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO = RAIZ / "data" / "Datos Marcas.xlsx"   # <-- ajusta la extension si no es .xlsx

df = pd.read_excel(ARCHIVO)
df.columns = df.columns.str.strip()

print("=" * 60)
print("1. DIMENSIONES Y COLUMNAS")
print("=" * 60)
print("Filas totales:", len(df))
print("Columnas:", list(df.columns))
print()
print(df.dtypes)

print("\n" + "=" * 60)
print("2. DISTRIBUCION DE 'Status Name'  <-- clave para el filtro")
print("=" * 60)
print(df["Status Name"].value_counts(dropna=False))

print("\n" + "=" * 60)
print("3. CRUCE Wcode x Status Name")
print("=" * 60)
print(pd.crosstab(df["Nice Class Status Wcode"], df["Status Name"]))

print("\n" + "=" * 60)
print("4. UNICIDAD (confirma el grano de los datos)")
print("=" * 60)
print("Filas totales :", len(df))
print("Mark Code unicos:", df["Mark Code (Ip Name)"].nunique())
print("Nro_sol unicos  :", df["Nro_sol"].nunique())
print("Mark Name unicos:", df["Mark Name"].nunique())

print("\n" + "=" * 60)
print("5. NULOS EN CAMPOS CLAVE")
print("=" * 60)
cols = ["Mark Code (Ip Name)", "Mark Name", "Nice Class Code", "Nro_sol", "Status Name"]
print(df[cols].isna().sum())

print("\n" + "=" * 60)
print("6. ¿El nombre es constante por Mark Code?")
print("=" * 60)
nombres_por_code = df.groupby("Mark Code (Ip Name)")["Mark Name"].nunique()
inconsistentes = nombres_por_code[nombres_por_code > 1]
print("Mark Codes con mas de un nombre distinto:", len(inconsistentes))
if len(inconsistentes) > 0:
    print(inconsistentes.head(10))

print("\n" + "=" * 60)
print("7. DISTRIBUCION DE CLASES NICE")
print("=" * 60)
print(df["Nice Class Code"].value_counts().sort_index())

print("\n" + "=" * 60)
print("8. EJEMPLO: marca con mas clases")
print("=" * 60)
conteo = df.groupby("Mark Code (Ip Name)").size().sort_values(ascending=False)
print("Mark Codes con mas filas (clases):")
print(conteo.head(5))
top = conteo.index[0]
print(f"\nDetalle del Mark Code {top}:")
print(df[df["Mark Code (Ip Name)"] == top][
    ["Mark Name", "Nice Class Code", "Nro_sol", "Status Name"]])