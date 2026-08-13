import time
import pandas as pd
from rapidfuzz import process, fuzz
from buscador import config, normalizacion

marcas = pd.read_parquet(config.MARCAS_PROCESADAS)
canonicos = marcas["nombre"].map(normalizacion.limpiar).tolist()

consulta = normalizacion.limpiar("CHALLENGER")

start = time.time()
for _ in range(10):
    scores = process.cdist([consulta], canonicos, scorer=fuzz.token_sort_ratio)[0]
elapsed = time.time() - start
print(f"Por consulta: {elapsed/10:.2f}s -> Estimado 2567 marcas: {elapsed/10*2567/60:.0f} min")