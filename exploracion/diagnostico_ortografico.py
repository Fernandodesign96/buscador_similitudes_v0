import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rapidfuzz import fuzz
from buscador import normalizacion

casos = [
    ("SKAAL BEER", "SVAJG BEER"),
    ("SKAAL BEER", "KURLA BEER"),
    ("SKAAL BEER", "CHARLY BEER"),
    ("SKAAL BEER", "SKAAL"),       # deberia ser muy alto
    ("SKAAL", "SVAJG"),            # sin "BEER", deberia ser bajo
]

print(f"{'A':20} {'B':20} {'token_sort':10} {'ratio_simple':12} {'token_set':10}")
for a, b in casos:
    ca, cb = normalizacion.limpiar(a), normalizacion.limpiar(b)
    ts = fuzz.token_sort_ratio(ca, cb)
    rs = fuzz.ratio(ca, cb)
    tset = fuzz.token_set_ratio(ca, cb)
    print(f"{a:20} {b:20} {ts:10.1f} {rs:12.1f} {tset:10.1f}")

def quitar_palabras_comunes(a, b):
    """Quita de cada cadena las palabras que aparecen en ambas, exactas."""
    wa, wb = a.split(), b.split()
    comunes = set(wa) & set(wb)
    fa = " ".join(w for w in wa if w not in comunes)
    fb = " ".join(w for w in wb if w not in comunes)
    return fa, fb

print("\n--- Sin palabras comunes ---")
for a, b in casos:
    ca, cb = normalizacion.limpiar(a), normalizacion.limpiar(b)
    fa, fb = quitar_palabras_comunes(ca, cb)
    score_sin = fuzz.token_sort_ratio(fa, fb) if fa and fb else (
        100.0 if fa == fb else 0.0
    )
    print(f"{a:20} {b:20} sin_comunes=({fa!r:15},{fb!r:15}) -> {score_sin:.1f}")

print("\n--- Claves foneticas ---")
for nombre in ["SKAAL", "SVAJG", "KURLA", "CHARLY"]:
    print(f"{nombre:10} -> {normalizacion.clave_fonetica(nombre)!r}")