# Propuesta para Camila — ficha de detalle de cada marca

**Para:** Camila (backend / motor de búsqueda)  
**De:** frontend Next.js (`feat/frontend-nextjs-mvp-2026-07-29`)  
**Fecha:** 12-08-2026  
**Alcance:** este documento **no pide que cambies el modelo matemático**. Pide exponer datos que el índice ya tiene (o que están en el Excel) y, más adelante, los que solo existen en la base de TI.

El frontend **ya está preparado**: las cards y la ficha leen campos opcionales. Si no llegan, muestran «Dato no disponible en este MVP». Cuando el API los envíe, aparecen solos.

---

## 1. Qué hace el frontend hoy (sin tocar Python)

Flujo: aviso legal → buscador → resultados → ficha.

En cada card se muestra:

| Dato | Origen actual |
|------|----------------|
| Nombre | API `nombre` |
| Parecido al escribir / al pronunciar | API `desglose` (barras **sin número ni color semáforo**) |
| Clases y cobertura breve | API `clases` + catálogo NCL del frontend (45 clases) |
| «Misma clase de productos o servicios» | API `clase_relacionada` |
| Estado (Registrada, caducada, etc.) | **No llega.** Placeholder. |
| Botón «Ver detalle de la marca» | Abre ficha con lo anterior + placeholders |

El porcentaje combinado **ya no se muestra** (decisión UX: el rojo se leía como rechazo). El umbral interno `similitud_min=75` se mantiene en la consulta; el usuario no ve el 75.

No se implementó «Contiene / Empieza con / Termina con»: el motor compara similitud, no coincidencia de texto. Si más adelante se quiere, es un filtro **nuevo** en Python, no un cambio de pesos.

---

## 2. Cómo trabaja el MVP hoy (resumen del modelo)

No hay que reescribir esto. Solo para alinear la ficha con lo que el motor ya calcula.

### Pipeline de datos

```
data/Datos Marcas.xlsx
        ↓  buscador/datos.py
filtrar ESTADOS_OPONIBLES  →  agrupar por Mark Code
        ↓
data/marcas_oponibles.parquet
        ↓  buscador/indice.py
listas en memoria: mark_codes, nombres, clases, solicitudes, canónicos, fonéticos
        ↓  buscador/busqueda.py
score combinado → api.py serializa JSON
```

`agrupar_por_marca()` deja **una fila por marca** con:

- `mark_code`
- `nombre`
- `clases` (lista de enteros NCL)
- `solicitudes` (números de solicitud base)

El **estado** (`Status Name`) se usa para filtrar y **después se descarta**. No está en el parquet.

### Universo buscable (importante para UX)

`ESTADOS_OPONIBLES` en `buscador/config.py` solo incluye marcas **vivas**, por ejemplo:

- Registrada
- Aguardando renovación / aceptación a registro (varios estados de espera)

**No** entran: caducada, anulada, denegada, abandonada, desistida, vencida, en trámite, en oposición.

Por eso el frontend **no puede** mostrar «Caducada» o «En oposición» con los datos actuales: esas marcas no están en el índice. Incluirlas es una **decisión de dominio** (¿el público debe ver marcas extintas?). Si se amplía el universo, cambia el sentido de «anterioridad oponible» y hay que recalibrar.

### Score (no cambiar)

- Ortográfico 0,58 + fonético 0,42 (`PESO_ORTOGRAFICO` / `PESO_FONETICO`)
- Si no comparten clase NCL: se atenúa con `FACTOR_CLASE_NO_RELACIONADA` (0,7), salvo que el API use `modo_clases=filtrar` (el frontend envía **filtrar**)
- Prefiltro vectorizado: `CANDIDATOS_PREFILTRO = 200`
- Umbral de listado web: `SIMILITUD_MIN_RESULTADOS = 75`

El frontend sigue pidiendo `top=200` y `similitud_min=75`. No hace falta tocar esos números para la ficha.

---

## 3. Qué pide la ficha (y de dónde puede salir)

### Fase A — solo tablas actuales (Excel / parquet). Sin base TI.

El índice **ya tiene** en memoria `mark_codes` y `solicitudes`, pero `api.py` no los manda.

| Campo en UI | ¿Existe hoy? | Qué hacer en Python |
|-------------|--------------|---------------------|
| Nombre | Sí | Ya se envía |
| Clases NCL | Sí | Ya se envía |
| Cobertura (título de clase) | Parcial | El FE usa el catálogo de 45 clases. La **lista de productos** del registro no está en el Excel. |
| Parecido escribir / pronunciar | Sí | Ya se envía `desglose` |
| `mark_code` | En índice, no en JSON | Añadir al serializado |
| N.° de solicitud | En índice (`solicitudes`), no en JSON | Añadir al serializado |
| Estado | En Excel `Status Name`, no en parquet | Conservarlo al agrupar (p. ej. el estado más reciente o el de la fila oponible) y enviarlo |
| N.° de registro | No en columnas requeridas | Fase B (TI) |
| Tipo de marca (palabra, mixta, figurativa…) | No | Fase B |
| Fechas (presentación, publicación, registro, vigencia) | No | Fase B |
| Titular | No | Fase B |
| Línea de tiempo del trámite | No | Fase B |
| Imagen / logo | No (el MVP es denominativo) | Fase B; la ficha hoy muestra el **nombre** como «cómo se ve» |

### Fase B — cuando exista acceso a la base TI

Un endpoint de ficha, por ejemplo:

```http
GET /api/marca/{mark_code}
```

Respuesta sugerida (nombres en español, estables para el FE):

```json
{
  "mark_code": 123,
  "nombre": "OPTIMAR",
  "tipo": "Marca de palabra",
  "estado": "Registrada",
  "solicitudes": ["1188342"],
  "nro_registro": "1289451",
  "clases": [7, 11, 37, 42],
  "cobertura": [
    { "clase": 42, "texto": "Servicios científicos y tecnológicos; …" }
  ],
  "titular": "Optimar AS",
  "fechas": {
    "presentacion": "03-05-2016",
    "publicacion": "18-09-2016",
    "registro": "02-02-2017",
    "vigencia": "02-02-2027"
  },
  "timeline": [
    { "label": "Presentada", "date": "2016" },
    { "label": "Registrada", "date": "2017" }
  ]
}
```

El frontend ya declara estos campos como **opcionales** en `frontend/src/lib/types.ts`. No hace falta un contrato rígido de un día para otro: se pueden ir llenando.

---

## 4. Cambio mínimo sugerido en el API de búsqueda (Fase A)

Hoy `_serializar_resultados` en `api.py` envía:

```python
{
  "nombre": r.nombre,
  "clases": r.clases,
  "similitud": r.score,
  "desglose": { "ortografica": ..., "fonetica": ... },
  "clase_relacionada": r.clase_relacionada,
}
```

**Propuesta (sin cambiar el score):**

1. En `IndiceBusqueda` / el resultado de `MotorBusqueda.buscar`, arrastrar `mark_code` y `solicitudes` (ya están en listas paralelas del índice).
2. En el parquet, agregar `estado` al agrupar (tomar `Status Name` de las filas oponibles de esa marca).
3. Ampliar el JSON:

```python
{
  "nombre": r.nombre,
  "clases": r.clases,
  "similitud": r.score,          # el FE no lo pinta; sirve para ordenar
  "desglose": { ... },
  "clase_relacionada": r.clase_relacionada,
  "mark_code": r.mark_code,
  "solicitudes": r.solicitudes,
  "estado": r.estado,            # texto claro, p. ej. "Registrada"
}
```

Con eso la card deja de decir «Estado no disponible» y la ficha muestra el n.° de solicitud.

No hace falta un endpoint extra para la Fase A: el detalle puede usar el mismo objeto del listado.

---

## 5. Estados: cómo mostrarlos en lenguaje claro

Si se expone `Status Name` crudo, el usuario verá textos de expediente («Aguardando que resolución de aceptación a registro sea publicada»). Mejor **mapear a etiquetas cortas** en Python (o en el FE si prefieres):

| Grupo sugerido (UI) | Ejemplos de Status Name |
|---------------------|-------------------------|
| Registrada | Registrada |
| En trámite | estados de espera de aceptación / publicación |
| En oposición | si algún día se indexan |
| Caducada / vencida | si algún día se indexan |
| Anulada / denegada / abandonada / desistida | si algún día se indexan |

Recomendación: **no ampliar `ESTADOS_OPONIBLES`** solo para rellenar la maqueta. El buscador público orienta sobre marcas que **pueden oponerse**. Caducadas y anuladas son otro producto (consulta de expediente).

---

## 6. Lo que el frontend no va a filtrar

- No pide «búsqueda exacta / contenga / empiece / termine». Eso sería un modo distinto al score fuzzy.
- No muestra el porcentaje combinado ni semáforo rojo.
- No modifica `CANDIDATOS_PREFILTRO`, pesos ni umbral.

Si TI más adelante entrega cobertura literal por clase, el FE puede pintar `cobertura[].texto` en lugar del título genérico NCL.

---

## 7. Cómo probar cuando esté listo

1. Reiniciar `python api.py` (carga el parquet al arrancar).
2. En el frontend, buscar un nombre y abrir «Ver detalle».
3. Debe verse al menos: nombre, clases, n.° de solicitud, estado.
4. El resto puede seguir como «no disponible» hasta Fase B.

Archivos frontend ya alineados con este contrato:

- `frontend/src/lib/types.ts` — campos opcionales
- `frontend/src/components/results/ResultCard.tsx`
- `frontend/src/components/results/MarkDetail.tsx`
