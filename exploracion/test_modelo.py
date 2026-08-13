from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

print("Cargando modelo (la primera vez se descarga, ~470 MB)...")
modelo = SentenceTransformer(MODELO)
print("Modelo cargado. Dimension de los vectores:",
      modelo.get_sentence_embedding_dimension())

marcas = [
    "CHALLENGER",
    "CHALENGER",          # mismo signo con un typo
    "CHALLENGER LIGHTS",  # mismo signo + palabra extra
    "SAMSUNG",            # sin relacion
    "ZAPATILLAS VELOZ",   # sin relacion
]

emb = modelo.encode(marcas, normalize_embeddings=True)
sim = cos_sim(emb, emb)

print("\nMatriz de similitud coseno (1.0 = identico):\n")
print(f"{'':<20}" + "".join(f"{i:>9}" for i in range(len(marcas))))
for i, nombre in enumerate(marcas):
    fila = "".join(f"{sim[i][j]:>9.3f}" for j in range(len(marcas)))
    print(f"{nombre:<20}{fila}")