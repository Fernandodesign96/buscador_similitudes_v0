# Buscador de Anterioridades — Frontend (Next.js)

Documento maestro para **instalación**, **mantenimiento** y **conexión con el backend** del MVP INAPI.

| Campo | Valor |
|-------|-------|
| **Implementación inicial** | Fernando — 29-07-2026 |
| **Mantenimiento** | Camila Henzi |
| **Stack** | Next.js 16 · React 19 · TypeScript · Tailwind 4 · shadcn/ui · Bun |
| **Backend asociado** | Flask (`api.py`) en la raíz del repo |
| **Repositorio** | `https://github.com/cihenzi/buscador_anterioridades` |

---

## Índice

0. [Clonar desde GitHub (primera vez)](#0-clonar-desde-github-primera-vez)
1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Arquitectura FE ↔ BE](#2-arquitectura-fe--be)
3. [Contrato de API (endpoints)](#3-contrato-de-api-endpoints)
4. [Cómo conectar el frontend con el backend](#4-cómo-conectar-el-frontend-con-el-backend)
5. [Guía de mantenimiento para Camila](#5-guía-de-mantenimiento-para-camila)
6. [Especificaciones finales de la UI](#6-especificaciones-finales-de-la-ui)
7. [Instalación y arranque](#7-instalación-y-arranque)
8. [Registro por fases (qué se hizo)](#8-registro-por-fases-qué-se-hizo)
9. [Pendientes opcionales](#9-pendientes-opcionales)
10. [Troubleshooting](#10-troubleshooting)
11. [Changelog](#11-changelog)

---

## 0. Clonar desde GitHub (primera vez)

El proyecto se entrega vía **repositorio Git** (no como carpeta comprimida) porque el peso local supera ~1,3 GB si se incluyen artefactos generados (`node_modules`, `.venv`, `.next`). Esos directorios **no están en GitHub**; cada persona los recrea en su máquina tras clonar.

### Requisitos previos en el PC de Camila

| Herramienta | Versión mínima | Para qué |
|-------------|----------------|----------|
| **Git** | cualquiera reciente | Clonar y actualizar el repo |
| **Python** | 3.11+ (probado 3.12) | Backend Flask + motor de búsqueda |
| **Bun** | 1.3+ | Dependencias y scripts del frontend |

Instalar Bun (si no lo tiene):

```bash
curl -fsSL https://bun.sh/install | bash
```

En Windows se recomienda **WSL2** (Ubuntu) o usar el instalador de Bun para Windows. El desarrollo se validó en WSL2.

### Clonar manteniendo el nombre de carpeta

```bash
git clone https://github.com/cihenzi/buscador_anterioridades.git
cd buscador_anterioridades
```

La carpeta resultante se llama `buscador_anterioridades`, igual que en el entorno original.

### Revisar la entrega en una rama (sin tocar `main`)

La implementación del 29-07-2026 está en la rama **`feat/frontend-nextjs-mvp-2026-07-29`**, integrada vía pull request a `main`. Para revisarla en local **sin afectar `main`**:

```bash
git clone https://github.com/cihenzi/buscador_anterioridades.git
cd buscador_anterioridades

# Traer ramas del remoto
git fetch origin

# Cambiar a la rama de la entrega (no mergear a main todavía)
git checkout feat/frontend-nextjs-mvp-2026-07-29

# Seguir con el setup de dependencias (venv + bun install) más abajo
```

Si ya tenías el repo clonado en `main`:

```bash
git fetch origin
git checkout feat/frontend-nextjs-mvp-2026-07-29
```

Para volver a `main` en cualquier momento: `git checkout main`.

### Qué trae el repositorio y qué hay que instalar

| Incluido en Git | No incluido — instalar localmente |
|-----------------|-----------------------------------|
| Código fuente (`frontend/src/`, `buscador/`, `api.py`) | `frontend/node_modules/` → `bun install` |
| `frontend/package.json` + `bun.lock` | `frontend/.next/` → se genera con `bun run build` |
| `requirements.txt` | `.venv/` → `python3 -m venv .venv` + `pip install` |
| `data/marcas_oponibles.parquet` (~6 MB) | Excel original (`data/Datos Marcas.xlsx`) — opcional |
| PDFs Lenguaje Claro en `docs/lenguaje-claro/` | — |
| Scripts `scripts/dev.sh`, `monitoring/` | — |

> **Importante:** Sin `bun install` y sin el entorno virtual Python, el frontend **no arranca**. Eso es normal: las dependencias no se versionan en Git.

### Setup completo tras clonar (copiar y pegar)

Desde la raíz `buscador_anterioridades/`:

```bash
# 1. Backend — entorno virtual e dependencias Python
python3 -m venv .venv
source .venv/bin/activate          # Windows/WSL: igual; Git Bash: source .venv/Scripts/activate
pip install --upgrade pip
pip install -r requirements.txt

# 2. Verificar motor de búsqueda (deben pasar 61 tests)
pytest -v

# 3. Frontend — dependencias Node (Bun)
cd frontend
bun install

# 4. Verificar que compila
bun run build

# 5. Volver a la raíz y arrancar todo
cd ..
bash scripts/dev.sh
```

Abrir en el navegador: **http://localhost:3000** (UI) · API en **http://127.0.0.1:5001/api/health**

### Arranque sin el script conjunto

```bash
# Terminal 1 — desde la raíz
source .venv/bin/activate
python api.py

# Terminal 2 — desde frontend/
bun dev
```

### Tras cada `git pull`

```bash
# Raíz: por si cambió requirements.txt
source .venv/bin/activate
pip install -r requirements.txt

# Frontend: por si cambió package.json o bun.lock
cd frontend && bun install
```

### Alternativa sin Bun (solo si Bun no está disponible)

```bash
cd frontend
npm install    # o: pnpm install
npm run dev
npm run build
```

Se prefiere **Bun** porque el proyecto usa `bun.lock` y `scripts/dev.sh` invoca `bun dev`.

---

## 1. Resumen ejecutivo

Este proyecto migró el piloto monolítico `index.html` a una aplicación **Next.js** en `frontend/`, manteniendo el **motor de búsqueda en Python** (`buscador/` + `api.py`) sin reescribirlo.

**Entregables del 29-07-2026:**

- Entorno WSL funcional (Python + Bun).
- Frontend React con dos modos de producto: **Opción A** (1 resultado) y **Opción B** (listado paginado).
- Textos en **Lenguaje Claro** centralizados y revisados con 4 PDFs oficiales.
- API Flask extendida (paginación, filtro NCL, healthcheck).
- Scripts de monitoreo y arranque conjunto.
- Ajustes finales de UI: alineación de formulario, ancho consistente y bordes del acordeón de ayuda.

El `index.html` de la raíz **se conserva como referencia histórica**; la interfaz activa es `http://localhost:3000`.

---

## 2. Arquitectura FE ↔ BE

```
Usuario
   │
   ▼
Next.js (frontend/)          Puerto 3000 en desarrollo
   │  fetch("/api/buscar")
   ▼
Rewrite en next.config.ts    /api/* → http://127.0.0.1:5001/api/*
   │
   ▼
Flask (api.py)               Puerto 5001
   │
   ▼
MotorBusqueda + parquet      data/marcas_oponibles.parquet
```

| Capa | Responsabilidad | No debe |
|------|-----------------|---------|
| **Frontend** | UI, textos, paginación visual, llamadas HTTP | Reimplementar lógica de similitud |
| **Backend** | Búsqueda, filtro NCL, paginación de resultados | Servir la UI de Next en producción final* |

\* En producción se recomienda que nginx sirva el build estático de Next y proxee `/api/*` a Flask/gunicorn (ver §4).

### Mapa de archivos clave

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Página principal
│   │   ├── layout.tsx            # Layout + fuentes Roboto
│   │   └── globals.css           # Tokens INAPI + Tailwind
│   ├── components/
│   │   ├── BuscadorApp.tsx       # Estado, búsqueda, Opción A/B
│   │   ├── layout/               # Header, footer, breadcrumb
│   │   ├── search/ClassPicker.tsx
│   │   ├── results/              # ResultCard, paginación
│   │   ├── help/HelpAccordion.tsx
│   │   └── ui/                   # shadcn (no editar a mano salvo necesidad)
│   └── lib/
│       ├── api.ts                # Cliente HTTP → backend
│       ├── types.ts              # Contrato TypeScript de la API
│       ├── copy.ts               # TODOS los textos visibles (Lenguaje Claro)
│       ├── ncl-classes.ts        # 45 clases Niza
│       ├── similarity.ts         # Colores semáforo
│       └── search-layout.ts      # Alturas/alineación del formulario
├── public/uploads/inapi_logo.jpg
├── next.config.ts                # Proxy /api → Flask
└── package.json
```

---

## 3. Contrato de API (endpoints)

El frontend **solo** consume estos endpoints. Si Camila modifica el backend, debe respetar este contrato o actualizar `types.ts` y `api.ts` en paralelo.

### `GET /api/health`

Monitoreo de disponibilidad.

**Respuesta 200:**

```json
{
  "status": "ok",
  "marcas_cargadas": 218369,
  "uptime_seconds": 120.5
}
```

### `GET /api/buscar`

Búsqueda de marcas similares.

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `q` | string | ✅ | — | Nombre de la marca a evaluar |
| `clases` | string | ❌ | — | Clases NCL separadas por coma (`25,35`) |
| `top` | int | ❌ | `10` | Máximo de candidatos que devuelve el motor antes de paginar |
| `modo_clases` | string | ❌ | `atenuar` | `atenuar` u `filtrar` (ver abajo) |
| `page` | int | ❌ | `1` | Página (Opción B) |
| `per_page` | int | ❌ | `20` | `10` o `20` resultados por página |

**Modos de clase:**

| Valor | Uso en UI | Comportamiento |
|-------|-----------|----------------|
| `atenuar` | Opción A | Sin intersección NCL → score × 0.7; **no excluye** marcas |
| `filtrar` | Opción B | Solo marcas que **comparten al menos una** clase NCL seleccionada |

**Respuesta 200:**

```json
{
  "consulta": "SOLYMAR",
  "clases": [25],
  "total": 87,
  "page": 1,
  "per_page": 20,
  "total_pages": 5,
  "resultados": [
    {
      "nombre": "POLYMAR",
      "clases": [21, 22, 39, 42, 44],
      "similitud": 85.71,
      "desglose": {
        "ortografica": 85.71,
        "fonetica": 85.71
      },
      "clase_relacionada": true
    }
  ]
}
```

**Errores:**

| Código | Cuerpo | Cuándo |
|--------|--------|--------|
| 400 | `{"error": "Falta el parametro 'q'."}` | Sin consulta |
| 400 | `{"error": "Parametro 'clases' invalido."}` | Clases mal formateadas |
| 400 | `{"error": "Parametro 'modo_clases' invalido."}` | Valor distinto de atenuar/filtrar |

### Llamadas que hace el frontend hoy

**Opción A** (`BuscadorApp.tsx`):

```
GET /api/buscar?q={consulta}&top=1&modo_clases=atenuar&clases={opcional}&page=1&per_page=1
```

**Opción B:**

```
GET /api/buscar?q={consulta}&top=200&modo_clases=filtrar&clases={opcional}&page={n}&per_page={10|20}
```

> **Límite del motor:** `CANDIDATOS_PREFILTRO = 200` en `buscador/config.py` (no modificado). Opción B pagina como máximo 200 marcas similares.

---

## 4. Cómo conectar el frontend con el backend

### Desarrollo local (configuración actual)

1. Terminal 1 — backend:

```bash
cd /ruta/al/buscador_anterioridades
source .venv/bin/activate
python api.py
# → http://127.0.0.1:5001
```

2. Terminal 2 — frontend:

```bash
cd frontend
bun dev
# → http://localhost:3000
```

3. El proxy en `next.config.ts` reenvía `/api/*` a Flask. **No hace falta CORS** en desarrollo.

**Alternativa:** `bash scripts/dev.sh` desde la raíz (levanta ambos).

### Si Camila cambia el puerto del backend

Editar `frontend/next.config.ts`:

```typescript
destination: "http://127.0.0.1:PUERTO/api/:path*",
```

Reiniciar `bun dev`.

### Producción (recomendado)

Opción A — **nginx** como reverse proxy único:

```nginx
# Frontend (build estático de Next)
location / {
    proxy_pass http://127.0.0.1:3000;   # o servir out/ con next start
}

# API Python
location /api/ {
    proxy_pass http://127.0.0.1:5001/api/;
    proxy_read_timeout 120s;
}
```

Opción B — **solo Next en producción** con rewrite al host del API:

```typescript
// next.config.ts — producción
destination: `${process.env.API_URL}/api/:path*`,
```

Y definir `API_URL=https://buscador.inapi.cl` (sin `/api` al final).

### Checklist al integrar un endpoint nuevo

1. Implementar ruta en `api.py` (o confirmar que existe).
2. Probar con `curl` directo a `:5001`.
3. Agregar tipos en `src/lib/types.ts`.
4. Agregar función en `src/lib/api.ts` (o extender `buscarMarcas`).
5. Consumir desde el componente React.
6. Probar vía `:3000` (pasa por el rewrite).
7. Documentar en este README.

### Si el backend y frontend están en dominios distintos (sin proxy)

Habría que añadir `flask-cors` en `api.py` y cambiar `fetch` a URL absoluta. **No es necesario** con la arquitectura actual de rewrite.

---

## 5. Guía de mantenimiento para Camila

### Regla de oro

| Quiero cambiar… | Editar este archivo | No editar |
|-----------------|---------------------|-----------|
| Textos visibles (títulos, ayuda, errores) | `src/lib/copy.ts` | Componentes sueltos |
| Colores semáforo de similitud | `src/lib/similarity.ts` | `ResultCard.tsx` |
| Clases Niza (descripciones) | `src/lib/ncl-classes.ts` | — |
| Lógica Opción A / B | `src/components/BuscadorApp.tsx` | `api.py` (salvo cambio de contrato) |
| Altura/alineación del formulario | `src/lib/search-layout.ts` | — |
| Llamadas HTTP / parámetros API | `src/lib/api.ts` + `types.ts` | — |
| Estilos globales INAPI | `src/app/globals.css` | — |
| Componentes shadcn base | `src/components/ui/*` | Preferir wrappers en `components/` |

### Lenguaje Claro

- PDFs de referencia: `docs/lenguaje-claro/`
- Checklist de 37 criterios aplicables: `docs/lenguaje-claro/CHECKLIST-UI.md`
- Cualquier cambio de copy debe revisarse contra ese checklist.

### Comandos habituales

```bash
# Instalar dependencias (primera vez o tras pull)
cd frontend && bun install

# Desarrollo con hot-reload
bun dev

# Verificar que compila (obligatorio antes de entregar)
bun run build

# Lint
bun run lint
```

### Backend antes de tocar el frontend

```bash
cd ..   # raíz del repo
source .venv/bin/activate
pytest -v          # deben pasar 61 tests
python api.py      # API en :5001
```

### Qué no romper

1. **`copy.ts`** es la única fuente de textos — evita strings hardcodeados en JSX.
2. **`CANDIDATOS_PREFILTRO = 200`** — no aumentar sin acordarlo con el equipo (afecta rendimiento y Opción B).
3. **Proxy `/api`** — si el frontend no encuentra la API, revisar que Flask corre y que `next.config.ts` apunta al puerto correcto.
4. **`index.html` raíz** — legacy; no es la UI activa.

### Monitoreo

```bash
bash monitoring/healthcheck.sh     # ¿API viva?
bash monitoring/watchdog.sh        # Reinicio tras fallos (plantilla)
```

Plantilla systemd: `monitoring/buscador.service`

---

## 6. Especificaciones finales de la UI

### Orden de la página (de arriba a abajo)

1. Header + breadcrumb (chrome INAPI)
2. H1 + mensaje principal (`copy.page.lead`)
3. Botones **Opción A** / **Opción B** + descripción del modo activo
4. **«Cómo leer los resultados»** (acordeón — el usuario lee antes de buscar)
5. Formulario de búsqueda (nombre + NCL + botón)
6. Disclaimer breve
7. Resultados (si ya buscó)
8. Footer

### Opción A vs Opción B

| | Opción A | Opción B |
|---|----------|----------|
| **Botón** | «Opción A — Marca más parecida» | «Opción B — Todas las parecidas» |
| **Resultados** | 1 marca (la más similar) | Hasta 200, paginados |
| **Filtro NCL** | Opcional; atenúa score | Opcional; **excluye** marcas sin clase en común |
| **Paginación** | No | Sí (10 mobile / 20 desktop) |

### Formulario de búsqueda

- Input, selector NCL y botón comparten **altura `h-11` (44px)**.
- Etiquetas alineadas con **`min-h-11`** (`search-layout.ts`).
- Panel de búsqueda y acordeón de ayuda: **mismo ancho** (`w-full` dentro de `max-w-[1140px]`).

### Acordeón de ayuda

- Un solo borde exterior (`border-inapi-blue` + `overflow-hidden` + `rounded-lg`).
- Sin doble borde al desplegar (el contenido blanco no lleva borde lateral propio).

### Colores INAPI (`globals.css`)

| Token | Hex |
|-------|-----|
| `inapi-navy` | `#092039` |
| `inapi-blue` | `#0f69c4` |
| `inapi-blue-dark` | `#0051a8` |
| `inapi-amber` | `#ffbe5c` |
| Semáforo alto / medio / bajo | `#d32f2f` / `#ff9800` / `#43a047` |

---

## 7. Instalación y arranque

> **Si acabas de clonar el repo:** sigue primero la [§0 Clonar desde GitHub](#0-clonar-desde-github-primera-vez). Esta sección resume lo mismo para quien ya tiene el código en disco.

### Requisitos

- Git
- Python 3.11+ (probado con 3.12.3)
- Bun 1.3+ (o npm/pnpm como respaldo)
- `data/marcas_oponibles.parquet` — **ya viene en el repo**; no hace falta regenerarlo salvo que se actualice el Excel fuente

### Primera instalación (raíz + frontend)

```bash
cd buscador_anterioridades   # carpeta clonada

# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v

# Frontend
cd frontend
bun install
bun run build
```

### Arranque diario

```bash
# Opción recomendada (desde la raíz, con .venv ya creado)
bash scripts/dev.sh

# O por separado:
source .venv/bin/activate && python api.py    # :5001
cd frontend && bun dev                         # :3000
```

### Build de producción (frontend)

```bash
cd frontend
bun run build
bun run start    # sirve en :3000
```

### Subir cambios a GitHub (mantenedores)

El remoto configurado es `origin` → `https://github.com/cihenzi/buscador_anterioridades.git`.

Antes de hacer push, confirmar que **no** se van a commitear carpetas pesadas:

```bash
git status   # no debe listar .venv/, frontend/node_modules/ ni frontend/.next/
```

Esas rutas están en `.gitignore` de la raíz del proyecto.

---

## 8. Registro por fases (qué se hizo)

Resumen de cada fase acordada en la reunión de corrección del MVP.

### Fase 0 — Preparación del entorno WSL

**Objetivo:** Poder ejecutar el MVP Python en WSL antes de migrar el frontend.

**Qué se hizo:**
- Entorno virtual `.venv` con dependencias de `requirements.txt` + `pytest` + `openpyxl`.
- Validación: **61 tests** en verde.
- API Flask corriendo en `:5001` con parquet de 218.369 marcas.

**Resultado:** Base estable para desarrollo local.

---

### Fase 1 — Scaffold Next.js + shadcn + Bun

**Objetivo:** Crear el proyecto frontend moderno y conectarlo al backend existente.

**Qué se hizo:**
- App Next.js 16 con TypeScript, Tailwind 4, App Router.
- shadcn/ui (componentes en `src/components/ui/`).
- Proxy `/api/*` → Flask en `next.config.ts`.
- Cliente HTTP tipado (`api.ts`, `types.ts`).
- Logo INAPI en `public/uploads/`.

**Resultado:** Frontend compilable y comunicado con la API sin CORS.

---

### Fase 2 — Migración UI a React

**Objetivo:** Trasladar el piloto `index.html` a componentes React manteniendo el look INAPI.

**Qué se hizo:**
- Componentes de layout (header, footer, breadcrumb).
- Formulario de búsqueda, selector NCL, tarjetas de resultado, paginación.
- Fuentes Roboto / Roboto Slab.
- `index.html` original conservado en la raíz como referencia.

**Resultado:** Paridad funcional con el piloto HTML, base para Opción A/B.

---

### Fase 3 — Opción A vs Opción B

**Objetivo:** Dos propuestas de producto para validación con INAPI.

**Qué se hizo:**
- Botones bajo el H1 para alternar modos.
- **Opción A:** `top=1`, `modo_clases=atenuar`.
- **Opción B:** `top=200`, `modo_clases=filtrar`, paginación con botones numéricos.
- Extensión de `api.py`: `modo_clases`, `page`, `per_page`, metadatos `total` / `total_pages`.
- `CANDIDATOS_PREFILTRO = 200` **sin modificar** (límite acordado del motor).

**Resultado:** Dos flujos de usuario distinguibles, listos para revisión con el equipo INAPI.

---

### Fase 4 — Lenguaje Claro

**Objetivo:** Textos comprensibles según criterios oficiales de calidad web INAPI.

**Qué se hizo:**
- Carpeta `docs/lenguaje-claro/` con 4 PDFs oficiales.
- Reescritura completa en `src/lib/copy.ts` (tuteo, voz activa, siglas definidas).
- Checklist de 37 criterios aplicables documentado en `CHECKLIST-UI.md` (35 cumplidos, 1 parcial F1).
- Reordenamiento: ayuda **antes** del formulario; mensaje principal en la parte superior.

**Resultado:** UI alineada con Lenguaje Claro; textos centralizados para futuras revisiones.

---

### Fase 5 — Monitoreo

**Objetivo:** Continuidad del servicio ante caídas.

**Qué se hizo:**
- Endpoint `GET /api/health`.
- Scripts `monitoring/healthcheck.sh` y `watchdog.sh`.
- Plantilla `monitoring/buscador.service` (systemd).
- `scripts/dev.sh` para arranque conjunto FE + BE.

**Resultado:** Herramientas listas para operación; falta desplegar en servidor real con TIC.

---

### Ajustes finales de UI (29-07-2026)

**Objetivo:** Consistencia visual señalada en revisión.

**Qué se hizo:**
- Mismo ancho para acordeón de ayuda y panel de búsqueda (`w-full`).
- Alturas unificadas del formulario (`search-layout.ts`: `h-11`, etiquetas `min-h-11`).
- Bordes del acordeón: un solo contenedor con `overflow-hidden` (sin doble borde al desplegar).

**Resultado:** Jerarquía visual coherente en desktop y mobile.

---

## 9. Pendientes opcionales

| Ítem | Prioridad | Notas |
|------|-----------|-------|
| Tests automatizados de `modo_clases` y paginación en `tests/` | Media | El motor ya tiene 61 tests; faltan tests de capa API |
| URLs reales en header/footer (hoy `#`) | Baja | Criterio F1 del checklist Lenguaje Claro |
| Despliegue producción (nginx + gunicorn + systemd) | Alta para go-live | Ver README raíz §12 y `monitoring/buscador.service` |
| Decisión INAPI: ¿Opción A, B o ambas en producción? | Producto | La UI soporta ambas hoy |
| Elegir una sola vista y ocultar el toggle | Post-validación | Editar `BuscadorApp.tsx` |

---

## 10. Troubleshooting

| Problema | Solución |
|----------|----------|
| `SSL_CERT_FILE` en pip | `unset SSL_CERT_FILE` |
| Puerto 5001 ocupado | `fuser -k 5001/tcp` → reiniciar `python api.py` |
| Búsqueda falla en `:3000` | Verificar Flask en `:5001` y `next.config.ts` |
| `Failed to fetch` / error de red | Backend apagado o proxy mal configurado |
| Tras clonar, `bun: command not found` | Instalar Bun (§0) o usar `npm install` en `frontend/` |
| Tras clonar, `Module not found` en Next | Falta `bun install` en `frontend/` |
| Tras clonar, API no arranca | Falta `.venv` + `pip install -r requirements.txt` |
| `scripts/dev.sh` falla al inicio | Crear `.venv` antes: `python3 -m venv .venv && pip install -r requirements.txt` |
| Parquet faltante | `python construir_datos.py` (requiere Excel) |
| `bun run build` falla | Leer error TypeScript; suele ser desajuste con `types.ts` tras cambio de API |
| Doble borde en acordeón | No agregar `border` al panel interior; usar patrón de `HelpAccordion.tsx` |

---

## 11. Changelog

| Fecha | Cambio |
|-------|--------|
| 29-07-2026 | Fase 0: entorno WSL, venv, 61 tests OK |
| 29-07-2026 | Fase 1: Next.js 16 + shadcn + Bun, proxy API |
| 29-07-2026 | Fase 2: migración UI a React |
| 29-07-2026 | Fase 3: Opción A/B, API paginada, filtro NCL estricto |
| 29-07-2026 | Fase 4: Lenguaje Claro + 4 PDFs + checklist 37 criterios |
| 29-07-2026 | Fase 5: `/api/health`, scripts monitoreo, `dev.sh` |
| 29-07-2026 | UI: alineación formulario, ancho unificado, bordes acordeón |
| 29-07-2026 | README ampliado: guía mantenimiento Camila + contrato API |
| 29-07-2026 | §0: clonado GitHub, dependencias locales (Bun + venv), qué no va en el repo |
| 29-07-2026 | §0: revisión en rama `feat/frontend-nextjs-mvp-2026-07-29` vía PR |

---

## Checklist de entrega

- [x] `pytest`: 61 passed
- [x] Backend en `:5001` + `/api/health`
- [x] Frontend build (`bun run build`)
- [x] Opción A y Opción B validadas en navegador
- [x] Lenguaje Claro + `CHECKLIST-UI.md`
- [x] Monitoreo (scripts + plantilla systemd)
- [x] Documentación FE ↔ BE para mantenimiento
- [x] Instrucciones de clonado GitHub + instalación de dependencias (§0)
- [ ] Despliegue en servidor INAPI (pendiente TIC)
- [ ] Decisión final de vista (A / B / ambas) tras revisión INAPI
