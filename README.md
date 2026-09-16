# Buscador de similitudes v0 — clone de prueba (variante B)

Este repositorio **no es el MVP oficial**. Es un **clone de prueba** de Fernando, creado solo para **pilotar una versión antigua del frontend** (búsqueda solo por nombre de marca) y recoger inputs de usuario, como un **A/B testing** frente al producto oficial.

| | **A — original** | **B — este clone** |
|---|---|---|
| Carpeta local | `buscador_anterioridades` | `buscador_similitudes_v0` |
| GitHub | `cihenzi/buscador_anterioridades` | Repo **privado** bajo la cuenta de Fernando |
| Qué prueba | UI actual: marca **+** producto/servicio (CoverageSearch / Fuse / NCL) | UI “vieja” de flujo: **solo nombre de marca** (+ clase Niza opcional) |
| Resultados | Cards, bandas de severidad, detalle, aviso legal | Los **mismos** (nivel HEAD del oficial) |
| Motor Python | Ortográfica + fonética, parquet de marcas | **Idéntico** (no se toca) |
| Hugging Face | Space de Camila | **No se toca.** Este clone no publica en ese Space |

**A** sigue siendo la fuente oficial. **B** sirve para comparar si el flujo “solo marca” es más claro para el usuario, sin mezclar productos ni hacer `git push` al repo de Camila.

El frontmatter de Hugging Face (`sdk: docker`, `app_port: 7860`) se quitó de este README a propósito: un push a un repo nuevo no debe enganchar Spaces.

## Qué hace la variante B (frontend)

- Un campo: **Nombre de tu marca**.
- **Continuar** no exige producto/servicio ni coberturas NCL.
- ClassPicker opcional: “si ya sabes la clase”; si no, se busca en todas.
- Cards expandibles, bandas escribir/pronunciar, paginación, detalle, aviso legal, header/footer/breadcrumb: como el HEAD del oficial.
- `CoverageSearch` **no** está en el flujo.

El motor (`api.py`, `buscador/`) se mantiene igual que en A.

## Arranque local

Python 3.11+ (probado 3.12), Bun, Git LFS. El parquet `data/marcas_oponibles.parquet` debe ser el archivo real (~varios MB), no un puntero LFS de pocos KB (`git lfs install && git lfs pull` si hace falta).

```bash
cd /home/fernando/projects/buscador_similitudes_v0
python3 -m venv .venv          # si aún no existe
source .venv/bin/activate
pip install -r requirements.txt
cd frontend && bun install
```

Dos procesos:

```bash
# terminal 1 — API
source .venv/bin/activate
python api.py                  # http://127.0.0.1:5001

# terminal 2 — UI
cd frontend
bun dev                        # http://localhost:3000
```

En local el browser llama `/api/buscar` y Next reescribe a Flask en `127.0.0.1:5001`. Ese rewrite **no sirve** en Vercel.

No versionar: `.venv`, `frontend/node_modules`, `frontend/.next`, `.env`, Excel/CSV de claseniza.

## Git: este clone vs el original

| Remote | Debe apuntar a | Uso |
|---|---|---|
| `camila` | `https://github.com/cihenzi/buscador_anterioridades.git` | Solo lectura. **Nunca** `git push camila`. |
| `origin` | `https://github.com/TU_USUARIO/buscador_similitudes_v0.git` | Repo propio. |

Mientras `origin` siga siendo `cihenzi/buscador_anterioridades`, **no hagas** `git push origin`.

## Deploy (Vercel no es el Dockerfile de HF)

Stack: Flask + gunicorn + parquet grande + Next. El Dockerfile del oficial asume **API y front en la misma máquina**.

- **Vercel no hospeda ese Docker** (gunicorn + parquet persistente).
- **Prohibido:** `next build` en Vercel **sin** una API pública: la búsqueda se rompe (`127.0.0.1:5001` no existe en el browser del usuario).
- **Preferido:** frontend en Vercel (`Root Directory = frontend`, `bun install` / `bun run build`) **y** API Flask+parquet en Railway, Render, Fly, Cloud Run o un VPS. En el front: `NEXT_PUBLIC_API_URL`. En Flask: CORS al dominio de Vercel (hoy el backend de B es idéntico a A y **aún no tiene CORS**; hay que añadirlo cuando exista el split).
- **Un solo URL:** el mismo `Dockerfile` de este repo en Railway/Fly/Render, no en Vercel.

El Space de Camila y este deploy pueden convivir. No reconfigurar el Space.
