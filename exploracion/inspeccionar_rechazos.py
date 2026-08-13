import re
import pandas as pd
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO = RAIZ / "data" / "observaciones_2025_parseadas.xlsx"   # ajusta si el nombre difiere

df = pd.read_excel(ARCHIVO)
df.columns = df.columns.str.strip()

print("=" * 60)
print("1. DIMENSIONES Y COLUMNAS")
print("=" * 60)
print("Filas:", len(df))
print("Columnas:", list(df.columns))

print("\n" + "=" * 60)
print("2. DISTRIBUCION POR MODULO")
print("=" * 60)
print(df["modulo"].value_counts(dropna=False))

print("\n" + "=" * 60)
print("3. DISTRIBUCION POR letra_art20")
print("=" * 60)
print(df["letra_art20"].value_counts(dropna=False))

print("\n" + "=" * 60)
print("4. UNICIDAD DE SOLICITUDES (File_Nbr)")
print("=" * 60)
print("Filas totales      :", len(df))
print("File_Nbr unicos    :", df["File_Nbr"].nunique())
print("(una solicitud puede tener varias filas: una por modulo)")

print("\n" + "=" * 60)
print("5. M10: EXTRACCION DEL REGISTRO CITADO (anterioridad)")
print("=" * 60)
m10 = df[df["modulo"] == "M10"].copy()
print("Filas M10:", len(m10))

# El numero de registro citado sobrevive a la corrupcion del texto.
# Captura digitos que aparecen despues de la palabra 'Registro',
# saltando ruido intermedio (nbs;, strong, ceros a la izquierda).
patron = re.compile(r"[Rr]egistro[^\d]{0,15}0*(\d{5,8})")

def registros_citados(texto):
    if not isinstance(texto, str):
        return []
    return patron.findall(texto)

m10["registros"] = m10["texto_observacion"].apply(registros_citados)
m10["n_registros"] = m10["registros"].apply(len)

con_registro = (m10["n_registros"] > 0).sum()
print(f"Filas M10 con al menos un registro extraido: {con_registro} "
      f"({con_registro / len(m10) * 100:.1f}%)")
print(f"Filas M10 sin ningun registro extraido     : {len(m10) - con_registro}")
print("\nDistribucion de cantidad de registros citados por fila:")
print(m10["n_registros"].value_counts().sort_index())

print("\nRango de los numeros de registro extraidos (para inferir el tipo de ID):")
todos = [int(r) for lst in m10["registros"] for r in lst]
if todos:
    s = pd.Series(todos)
    print(f"  min={s.min()}  max={s.max()}  cantidad={len(s)}  unicos={s.nunique()}")

print("\n" + "=" * 60)
print("6. MUESTRA DE TEXTO CRUDO (ver corrupcion de codificacion)")
print("=" * 60)
muestra = m10["texto_observacion"].dropna().iloc[0]
print(repr(muestra[:400]))