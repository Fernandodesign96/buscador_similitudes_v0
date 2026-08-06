---
title: Buscador de Anterioridades INAPI
emoji: 🔍
colorFrom: blue
colorTo: red
sdk: docker
app_port: 7860
pinned: false
---

# Buscador de Anterioridades — INAPI

Herramienta pública que permite a un solicitante de marca comparar su denominación propuesta con las marcas ya inscritas en Chile antes de presentar la solicitud.

No es un predictor de aceptación o rechazo. Es una herramienta orientativa; la resolución final corresponde al examinador de INAPI.

# Buscador de Anterioridades Denominativas — INAPI
## Estado del proyecto · Julio 2026 (actualizado 20 jul)

**Responsable:** Camila Henzi  
**Repositorio:** `G:\Mi unidad\01. IA en examen de fondo\buscador_anterioridades`  
**Entorno conda:** `buscador` (Python 3.11)  
**Objetivo:** Herramienta pública que permite a un solicitante de marca comprobar qué tan similar es su denominación propuesta respecto a las marcas ya inscritas en Chile, antes de presentar la solicitud ante INAPI.

---

## 1. Qué es y para qué sirve

El buscador es una **aplicación web local** (Flask + HTML) que expone un motor de búsqueda por similitud denominativa. El usuario escribe el nombre de una marca que quiere inscribir, opcionalmente indica las clases de Niza (categorías de productos o servicios), y el sistema devuelve las marcas ya inscritas más parecidas, con un porcentaje de similitud y un desglose por dos señales (ortográfica y fonética).

**No es un predictor de aceptación o rechazo.** Es una herramienta orientativa para el solicitante. La resolución final siempre corresponde al examinador de INAPI.

---

## 2. Contexto dentro del proyecto mayor

Este buscador es el **Track 2** de un proyecto más amplio de automatización del examen de fondo de marcas en INAPI:

| Track | Nombre | Objetivo | Entorno conda | Repositorio |
|---|---|---|---|---|
| **Track 1** | Sistema de asistencia al examinador | Análisis de las 11 causales del Art. 20 LPI + semáforo por módulo para uso interno | `inapi` | `cihenzi/inapi-examen-fondo` |
| **Track 2** | Buscador de anterioridades (este documento) | Herramienta pública de similitud denominativa | `buscador` | carpeta local en Google Drive |

Ambos tracks son independientes. Este documento cubre exclusivamente el Track 2.

---

## 3. Arquitectura del sistema

### 3.1 Componentes

```
buscador_anterioridades/
│
├── buscador/               ← Paquete Python (lógica de negocio)
│   ├── config.py           ← Rutas, pesos y parámetros del motor
│   ├── datos.py            ← Lectura y filtrado del Excel de marcas
│   ├── normalizacion.py    ← Limpieza de texto, clave fonética española y lema (singularización)
│   ├── indice.py           ← Carga el universo en memoria + tablas de frecuencia por clase NCL
│   ├── busqueda.py         ← Motor de búsqueda (combina las 2 señales, rapidfuzz.cdist)
│   └── validacion.py       ← Módulo de validación de recall (uso interno)
│
├── tests/                  ← Suite de tests automatizados (79 tests)
│   ├── test_datos.py
│   ├── test_normalizacion.py
│   ├── test_busqueda.py
│   ├── test_indice.py
│   └── test_validacion.py
│
├── exploracion/            ← Scripts de análisis y diagnóstico (desechables)
│   ├── inspeccionar_datos.py
│   ├── diagnostico_anterioridades.py
│   ├── verificar_nombres_solicitud.py
│   └── ...
│
├── data/                   ← Datos de entrada y artefactos generados
│   ├── Datos Marcas.xlsx           ← Fuente: export de marcas de INAPI (619.806 filas)
│   └── marcas_oponibles.parquet    ← Marcas oponibles agrupadas (218.369 marcas)
│
├── construir_datos.py      ← Script: genera marcas_oponibles.parquet desde el Excel
├── validar.py              ← Script: mide recall contra observaciones M10 (uso interno)
├── validar_rapido.py       ← Script: valida contra rechazos_2026.xlsx usando rapidfuzz.cdist
├── api.py                  ← Servidor Flask + endpoint de búsqueda
├── index.html              ← Interfaz web legacy (no es la que está en uso, ver nota)
├── frontend/               ← Interfaz web actualmente en uso
├── requirements.txt
└── pytest.ini
```

> **Nota (ago 2026):** el equipo dejó de servir `index.html` como interfaz y usa la carpeta `frontend/` en su lugar. `index.html` se mantiene en el repositorio sin modificar (no se toca al hacer cambios en el motor de búsqueda); todos los fixes de este documento son exclusivamente sobre `buscador/` (backend) y no requieren ni implican ningún cambio en `frontend/`.

### 3.2 Flujo de datos

```
Excel de marcas (619.806 filas)
        │
        ▼ construir_datos.py
marcas_oponibles.parquet (218.369 marcas únicas vigentes)
        │
        ▼ api.py  [carga el parquet en memoria al arrancar]
Motor de búsqueda disponible
        │
        ▼ index.html  [interfaz del usuario]
Consulta: nombre + clases NCL → 10 resultados con % de similitud
```

---

## 4. El motor de búsqueda: cómo funciona

### 4.1 Las dos señales

El motor combina dos señales para evaluar el parecido entre dos denominaciones:

| Señal | Peso | Qué detecta | Ejemplo |
|---|---|---|---|
| **Ortográfica** | 58% | Parecido visual letra por letra, tolerando reordenamiento de palabras | "CASA BLANCA" ↔ "BLANCA CASA" |
| **Fonética** | 42% | Parecido al pronunciar en español-Chile (seseo, yeísmo, h muda, b=v, etc.) | "CAUQUENES" ↔ "KAUKENES" |

**La señal semántica (embeddings) se eliminó del motor.** Durante la validación se detectó que, para denominaciones cortas o inventadas típicas del registro marcario, los vectores de embeddings se agrupan en un cono muy estrecho (anisotropía), lo que genera un piso de similitud coseno artificialmente alto y poco confiable. El motor actual usa exclusivamente señales ortográfica y fonética vía rapidfuzz.

### 4.2 Corrección de palabras genéricas compartidas

Un problema detectado y corregido durante el desarrollo: si dos marcas comparten una palabra genérica del rubro (ej. "BEER" en clase 32, "CHILE" en marcas nacionales), esa palabra compartida infla artificialmente el score ortográfico y fonético, aunque los elementos distintivos de cada marca sean completamente distintos.

La corrección aplicada: antes de calcular el score, se identifican las palabras genéricas de cada marca y se descuentan de la comparación. Si al descontar las palabras genéricas una de las cadenas queda vacía (es decir, una marca es casi subconjunto de la otra, ej. "SKAAL BEER" vs "SKAAL"), se mantiene el score original sin penalización. Esta corrección se aplica tanto a la función ortográfica como a la fonética, ya que ambas usan `token_sort_ratio` internamente y ambas mostraban el mismo problema de inflación.

Una palabra se considera genérica de dos formas, que se combinan (ver `busqueda._palabras_comunes_fuera()`):

1. **Por lema compartido entre las dos marcas comparadas** (mecanismo original): se compara por `normalizacion.lema()`, no por cadena exacta, para que un plural y su singular (ej. "cervezas" / "cerveza") cuenten como la misma palabra — ver 4.2.1.
2. **Por frecuencia en el universo real**, condicionada por clase NCL (fix 06-ago-2026 PM, ver 4.2.2): una palabra que aparece en una fracción alta de las marcas de la clase del candidato se descuenta aunque la consulta no la comparta letra por letra.

Adicionalmente, el descuento no se aplica si el residuo que queda tras quitar las palabras genéricas es demasiado corto (ver 4.2.3), porque el ratio de edición normalizado es estadísticamente inestable sobre 2-3 caracteres.

#### 4.2.1 Fix 06-ago-2026 AM — plural/singular ("cervezas ricas" vs "cerveza tribal")

Reportado por el equipo: "cervezas ricas" obtenía 77% de similitud con "cerveza tribal", sin relación real entre ambas. Causa: "cervezas" (plural) y "cerveza" (singular) no son la misma cadena, así que el mecanismo de descuento por coincidencia exacta no las detectaba como comunes, y el término genérico del rubro ("cerveza"/"cervezas") dominaba el ratio de caracteres frente a las palabras que sí distinguen a cada marca ("ricas" / "tribal").

Corrección: `normalizacion.lema()`, una singularización naive que cubre el patrón de plural más común del español (vocal + "s": "cervezas" → "cerveza", "casas" → "casa"). Se usa **solo** para decidir qué palabras cuentan como "la misma" al detectar términos comunes; el residuo que efectivamente se compara sigue usando las palabras originales, no el lema. No cubre el patrón consonante + "es" (ej. "flores" → "flor"): se deja documentado como limitación conocida en vez de arriesgar una regla más agresiva sin evidencia empírica de que sea necesaria.

#### 4.2.2 Fix 06-ago-2026 PM — genericidad por frecuencia en la clase NCL, no solo por coincidencia exacta

El mecanismo de 4.2.1 solo detecta como genérica una palabra si **ambas** marcas la comparten (exactamente o por lema). No detecta que "cerveza" es genérico en clase 32 si la consulta usa un sinónimo, ni pondera cuán descriptiva es realmente una palabra para el rubro del candidato.

Fundamento doctrinal: un examinador humano no le da el mismo peso a cada palabra de una marca; identifica el elemento distintivo y descuenta lo meramente descriptivo del rubro (doctrina del "elemento dominante"; *Sabel v. Puma*, C-251/95). Esto se generaliza calculando, para cada palabra (por su lema), qué fracción de las marcas de una clase NCL la contienen — ver `indice.FrecuenciasPalabras` — y considerándola genérica en esa comparación si supera un umbral.

Se condiciona **por clase**, no globalmente, porque una frecuencia global confunde "palabra genérica del rubro" con "palabra común del español": por ejemplo "sur" aparece en cientos de marcas del universo completo (clases tan distintas como alimentos, transporte y servicios financieros) pero no supera ~0.7% de las marcas dentro de ninguna clase individual, mientras que "cerveza" es ~4.7% de las marcas de la clase 32. Una palabra se considera genérica si:

- aparece en al menos `config.CONTEO_MINIMO_GENERICO` (20) marcas de esa clase — evita que una clase pequeña con pocas marcas totales produzca porcentajes ruidosos, y
- esa cantidad representa al menos `config.UMBRAL_FRECUENCIA_GENERICO` (1%) de las marcas de la clase.

Basta con que sea genérica en **una sola** de las clases del candidato (no en todas) para descontarla en esa comparación, igual que en la doctrina marcaria basta con que un término sea descriptivo de uno de los productos o servicios en juego para debilitar su aporte a la distintividad. Las tablas de frecuencia (`IndiceBusqueda.frecuencias_ortograficas` / `frecuencias_foneticas`) se precalculan una sola vez al cargar el índice, no en cada consulta.

Esta fuente de genericidad es **opcional** en `_palabras_comunes_fuera()`: si no se entrega (por ejemplo, tests unitarios simples), el comportamiento es exactamente el de antes de este fix (solo descuento por lema compartido entre las dos marcas).

#### 4.2.3 Fix 05-ago-2026 — residuo demasiado corto tras el descuento

Reportado con "brasas del rey" vs "brasas del rei" (0% de coincidencia, cuando debería ser alto por fonética/semántica). Al descontar las palabras comunes ("brasas", "del"), el residuo queda en "rey" vs "rei" (3 caracteres). El ratio de edición normalizado es muy inestable sobre residuos tan cortos: una sola letra distinta hace caer el score de ~93% a 66.67%, castigando de forma desproporcionada una variante casi idéntica de una marca multi-palabra.

Corrección: un piso de longitud (`config.LONGITUD_MINIMA_RESIDUO_DESCUENTO`, 4 caracteres sin contar espacios). Si el residuo de cualquiera de los dos lados queda por debajo de ese piso, se omite el descuento de genéricos y se devuelve el score base (sin descontar) — ver `busqueda._residuo_muy_corto()`. Esto no reabre el problema original que motivó el descuento de genéricos (ej. "SKAAL BEER" vs "SVAJG BEER": el residuo "skaal"/"svajg" tiene 5 caracteres, por encima del piso), solo evita aplicarlo cuando el residuo es demasiado corto para que el porcentaje sea confiable.

Relacionado con este mismo fix: `clave_fonetica()` no trataba la "y" final de palabra tras vocal (rey, ley, buey) como el diptongo /ei/ que es en español, sino como consonante yeísta — por eso "rey" y "rei" no coincidían ni fonéticamente. Se agregó la regla `_RE_Y_DIPTONGO` en `normalizacion.py` para tratar "vocal + y" en fin de palabra como "vocal + i".

#### 4.2.3.1 Fix 06-ago-2026 PM (continuación) — el piso de longitud protegía también residuos cortos pero distintos

Reportado con "cervezas ricas" vs "cerveza yal", que aparecía como coincidencia muy alta sin relación real. Con la genericidad por frecuencia (4.2.2) ya activa, "cerveza"/"cervezas" se descuenta de ambos lados (genérico en clase 32) y el residuo queda en "ricas" vs "yal" (3 caracteres, bajo el piso de 4.2.3). El ratio normalizado entre esos residuos es 18.75%, que es el número **correcto** — "ricas" y "yal" no se parecen — pero el piso de longitud de 4.2.3 no distinguía "residuo corto porque es una variante de tipeo" (rey/rei) de "residuo corto porque simplemente es una palabra corta y distinta" (ricas/yal): en ambos casos ignoraba el ratio y devolvía el score sin descontar "cerveza" (76.31%), como si las dos marcas fueran básicamente la misma.

Corrección: `busqueda._residuos_variante_corta()` exige, además de que el residuo sea corto, que la distancia de edición **absoluta** (Levenshtein, sin normalizar) entre ambos residuos sea baja (`config.DISTANCIA_MAXIMA_RESIDUO_CORTO`, 1 carácter) para tratarlos como la misma palabra con un error de tipeo. Se usa distancia absoluta y no el ratio normalizado porque el ratio normalizado es precisamente la métrica inestable en cadenas cortas que este mecanismo existe para esquivar: con distancia absoluta, una letra distinta siempre cuenta como 1, sin importar el largo de la palabra. Resultado: "rey"/"rei" (distancia 1) sigue protegido y da ~94%; "ricas"/"yal" (distancia mucho mayor) ya no se protege, y el 18.75% baja el score final como corresponde.

#### 4.2.4 Fix 06-ago-2026 PM — Jaro-Winkler (peso al inicio de palabra)

Se combina la métrica de similitud existente en cada señal (`token_sort_ratio` para la ortográfica, `fuzz.ratio` para la fonética) con **Jaro-Winkler** (Winkler, 1990), que da un bono adicional cuando dos cadenas comparten el inicio. Ver `busqueda._score_ortografico_base()` / `_score_fonetico_base()` y los pesos `config.PESO_*_JARO_WINKLER_*`.

Fundamento: un consumidor real presta más atención al comienzo de una palabra que a su final — el modelo "cohort" de reconocimiento de habla (Marslen-Wilson, 1987) describe cómo el oyente reduce el conjunto de palabras candidatas progresivamente desde el primer fonema. Jaro-Winkler fue diseñado exactamente para capturar esto y ya viene incluido en `rapidfuzz.distance.JaroWinkler`, sin necesidad de agregar una dependencia nueva.

Los pesos (`0.75` para la métrica original, `0.25` para Jaro-Winkler, en ambas señales) le dan un peso menor a Jaro-Winkler porque es un ajuste, no un reemplazo, de la métrica ya validada por los tests existentes. Dado que Jaro-Winkler no tolera por sí solo el reordenamiento de palabras (a diferencia de `token_sort_ratio`), se le pasan los tokens ya ordenados alfabéticamente por `normalizacion.ordenar_tokens()` (precalculado en el índice como `IndiceBusqueda.canonicos_ordenados` para el prefiltro vectorizado) para que ambas métricas reciban el mismo tratamiento de tolerancia al reordenamiento (ej. "CASA BLANCA" ↔ "BLANCA CASA").

#### 4.2.5 Explorado y descartado — n-gramas de caracteres

Se implementó (y se dejó con tests propios, sin usarse en el cálculo del score) un coeficiente de Dice sobre n-gramas de caracteres (`busqueda._similitud_ngramas()`, trigrama por defecto vía `config.LONGITUD_NGRAMA`), pensado como verificación cruzada adicional sobre el residuo, agnóstica a cómo están segmentadas las palabras.

Al validarlo contra una muestra de marcas reales con una sola letra insertada o borrada (la variante más común de "error de tipeo"), resultó muy inestable ante ese tipo de edición específico: una inserción desplaza todos los n-gramas posteriores al punto de inserción, y puede hacer caer el score 30 puntos o más en una palabra de 8-10 caracteres aunque el resto sea idéntico. Caso concreto detectado en la validación: "SEMINRIOS INSIGHT, MEJORES PERSONAS, MEJORES RESULTADOS" (typo de una marca real registrada) caía de ~95% a 66.67% frente al original solo por el piso de n-gramas, y en otro caso una consulta con typo ("AKIDA") dejaba de encontrar la marca real correcta ("AKILDA") y encontraba una marca no relacionada en su lugar.

Usarlo como mínimo (igual que el descuento de genéricos) habría reintroducido, con otro mecanismo, el mismo tipo de falso negativo que motivó el fix de 4.2.3 (residuo demasiado corto). Se decidió **no** incorporarlo al cálculo del score, documentar la razón y dejar la función implementada y probada por si se retoma en el futuro con un diseño más robusto a inserciones/borrados (ej. n-gramas posicionales, o promediar en vez de tomar el mínimo).

### 4.3 Relación de clase NCL

Si el usuario especifica clases de Niza, el motor aplica un factor de atenuación (×0.7) al score de marcas que no comparten ninguna clase con la consulta. Esto refleja que el riesgo de confusión es menor entre marcas que operan en rubros distintos.

### 4.4 Comparación vectorizada contra el universo completo

El motor ya no usa un índice FAISS ni recuperación previa de candidatos. En su lugar, compara la consulta contra las 218.369 marcas de forma exhaustiva usando `rapidfuzz.process.cdist` (implementación en C++ vectorizada), tanto para la señal ortográfica como para la fonética.

Esto elimina la limitación anterior del MVP (marcas ortográficamente similares que quedaban fuera del recorte de candidatos semánticos) y a la vez es más rápido: el tiempo por consulta bajó de ~13 segundos (loop en Python) a ~0.11 segundos con `cdist`.

---

## 5. El universo de marcas oponibles

### 5.1 Fuente de datos

El Excel de origen (`Datos Marcas.xlsx`) es un export del sistema de marcas de INAPI con **619.806 filas** (registro histórico universal). Cada fila representa una marca en una clase NCL.

### 5.2 Criterio de oponibilidad

Solo se incluyen en el índice las marcas **vigentes** (oponibles). La decisión de qué estados incluir se tomó empíricamente, analizando qué estados tenían efectivamente las anterioridades que los examinadores citaron en sus observaciones M10 de 2025.

Estados incluidos como oponibles:

| Estado | Descripción |
|---|---|
| Registrada | Marca concedida y vigente |
| Aguardando por renovación de marca nacional | En proceso de renovación, sigue vigente |
| Aguardando que resolución de aceptación parcial a registro quede en firme | Aceptación en curso |
| Aguardando que resolución de aceptación a registro sea publicada | Ídem |
| Aguardando que fallo de aceptación a registro quede en firme | Ídem |
| Aguardando que fallo de aceptación parcial a registro quede en firme | Ídem |

Estados **excluidos** (marca extinta o en proceso definitivamente terminado):

Rechazada, Abandonada, Por no presentada, Desistida, Cancelada voluntariamente, y similares.

### 5.3 Resultado

Tras filtrar y agrupar por marca (una marca puede tener múltiples filas por clase):

| Cifra | Valor |
|---|---|
| Filas en el Excel original | 619.806 |
| Filas con estado oponible | 402.221 |
| Marcas únicas vigentes (Mark Code) | **218.369** |

### 5.4 Nota sobre el número de registro oficial

Durante el desarrollo se descubrió que el "número de registro oficial" que citan los examinadores en las observaciones de Art. 20 h) **no corresponde a ningún campo del Excel** (ni `Mark Code` ni `Nro_sol` ni `solicitud_base`). Es un cuarto identificador que existe en SQL Server pero no se exportó en este archivo. Esto impide la validación automática del recall contra los rechazos reales de 2025, y es uno de los argumentos concretos para solicitar acceso a SQL Server.

---

## 6. Rendimiento del motor

El motor ya no depende de un modelo de embeddings ni de caché de HuggingFace (ambos se eliminaron junto con la señal semántica). La comparación es puramente algorítmica vía `rapidfuzz.process.cdist`, lo que simplifica el despliegue: no hay descarga de modelo ni dependencia de conectividad a `huggingface.co`.

Tiempo por consulta: ~0.11 segundos contra las 218.369 marcas del universo completo (antes ~13 segundos con loop en Python puro).

---

## 7. Cómo arrancar el sistema

### 7.1 Requisitos previos

- Miniconda instalado
- Entorno `buscador` creado con las dependencias de `requirements.txt`
- Archivo `data/Datos Marcas.xlsx` en su lugar

### 7.2 Primera vez (instalación desde cero)

```bash
# 1. Activar entorno
conda activate buscador

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Generar la base de marcas oponibles
python construir_datos.py

# 4. Verificar que todo funciona
pytest

# 5. Arrancar la API
python api.py
```

Abrir en el navegador: **http://127.0.0.1:5001**

### 7.3 Uso normal (después de la primera instalación)

```bash
conda activate buscador
python api.py
```

Eso es todo. El parquet ya está generado en `data/`; no hace falta regenerarlo salvo que cambie la base de marcas.

### 7.4 Cuándo regenerar los datos

`marcas_oponibles.parquet` debe regenerarse cuando:
- Se actualiza el Excel de marcas (`Datos Marcas.xlsx`)
- Se cambian los estados oponibles en `config.py`

```bash
python construir_datos.py
```

### 7.5 Variable de entorno SSL (entornos institucionales)

En el entorno `buscador` dentro de la red de INAPI, la variable `SSL_CERT_FILE` puede apuntar a un archivo inexistente y causar errores en pip y en la API. Si ocurre, ejecutar antes de arrancar:

```bash
# En Anaconda Prompt (Windows CMD):
set SSL_CERT_FILE=

# En bash/zsh:
unset SSL_CERT_FILE
```

---

## 8. La interfaz web

### 8.1 Estructura de la pantalla

La interfaz (`index.html`) tiene cuatro secciones:

1. **Panel de ayuda desplegable** — explica qué significan el porcentaje, las tres señales y los niveles de color. Orientado al usuario final que no conoce el sistema.

2. **Panel de búsqueda** — campo de texto para la denominación + dropdown multi-selección de las 45 clases NCL (con sus descripciones) + botón Buscar. Las clases seleccionadas aparecen como chips removibles.

3. **Resultados** — tarjetas con: nombre de la marca, porcentaje combinado con colores semáforo (rojo ≥75 / ámbar ≥50 / verde <50), clases en que está inscrita, etiqueta "clase relacionada" si corresponde, y tres barras de progreso para el desglose de señales.

4. **Disclaimer** — texto claro que el porcentaje es orientativo y no constituye una resolución de INAPI.

### 8.2 Niveles de similitud

| Color | Rango | Significado para el usuario |
|---|---|---|
| 🔴 Rojo | 75% – 100% | Similitud alta. Conviene revisar con atención antes de presentar |
| 🟡 Ámbar | 50% – 74% | Similitud media. Hay parecido parcial; depende del contexto |
| 🟢 Verde | 0% – 49% | Similitud baja. Poco probable que constituya conflicto relevante |

---

## 9. API disponible

El servidor Flask expone dos endpoints:

### `GET /`
Sirve el frontend `index.html`.

### `GET /api/buscar`

Parámetros:

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `q` | string | ✅ | Denominación a evaluar |
| `clases` | string | ❌ | Clases NCL separadas por coma (ej. `25,35`) |
| `top` | int | ❌ | Número de resultados (default: 10) |

Respuesta JSON:

```json
{
  "consulta": "SOLYMAR",
  "clases": [25],
  "resultados": [
    {
      "nombre": "SOLGAR",
      "clases": [5],
      "similitud": 62.5,
      "desglose": {
        "ortografica": 76.9,
        "fonetica": 76.9
      },
      "clase_relacionada": false
    }
  ]
}
```

---

## 10. Tests automatizados

El proyecto tiene tests que cubren:

| Módulo | Qué verifican |
|---|---|
| `test_datos.py` | Lectura del Excel, derivación de solicitud_base, filtrado de estados, agrupación por marca |
| `test_normalizacion.py` | Limpieza de texto (limpiar), reglas fonéticas (clave_fonetica, incl. "vocal+y" final como diptongo), lema (singularización) y ordenar_tokens, casos borde con tildes/ñ/puntuación |
| `test_busqueda.py` | Combinación de señales (incl. blend con Jaro-Winkler), corrección de palabras genéricas (por lema compartido y por frecuencia de clase), residuo demasiado corto, modulación por clase, ordenamiento, similitud por n-gramas (probada pero no usada en el score — ver 4.2.5), invariante de seguridad del prefiltro (descuento nunca supera el score bruto), regresión "SEMINRIOS" (typo en palabra distintiva no se castiga por genéricos alrededor) y cobertura de la rama de prefiltro con universo grande |
| `test_indice.py` | Construcción de `FrecuenciasPalabras` por clase NCL (no globalmente), uso de lema en vez de cadena exacta al contar, umbral y piso de conteo mínimo |
| `test_validacion.py` | Preparación de casos de validación y conteo de recall |

Para correr:
```bash
pytest
```

Output esperado: `79 passed`.

---

## 11. Dependencias (requirements.txt)

```
rapidfuzz
pandas
openpyxl
pyarrow
pytest
flask
flask-cors
```

Instalación:
```bash
pip install -r requirements.txt
```

**Nota sobre Fortinet/proxy institucional:** al eliminarse la señal semántica, el motor ya no depende de `sentence-transformers` ni de descargar nada desde `huggingface.co`. El bloqueo del firewall de INAPI a ese dominio dejó de ser un bloqueante para este proyecto.

---

## 12. Próximos pasos: despliegue en Linux y migración a SQL Server

### 12.1 Despliegue en servidor Linux

El buscador corre hoy en localhost en Windows. Para producción se desplegará en un servidor Linux (Ubuntu 22.04 recomendado). A continuación los pasos completos, en orden.

---

#### 12.1.1 Requisitos del servidor

| Recurso | Mínimo | Recomendado |
|---|---|---|
| RAM | 2 GB | 4 GB |
| Disco | 2 GB libres | 5 GB |
| CPU | 1 vCPU | 2 vCPU |
| SO | Ubuntu 20.04+ | Ubuntu 22.04 LTS |
| Puerto | 5001 (o 80/443 con proxy) | 80/443 vía nginx |

Al eliminarse el índice FAISS y el modelo de embeddings, el consumo de memoria bajó considerablemente: solo se carga en memoria el parquet de marcas oponibles.

---

#### 12.1.2 Transferir el proyecto al servidor

Desde la máquina local, copiar todo el proyecto al servidor:

```bash
# Opción A: desde Windows con scp
scp -r "G:\Mi unidad\01. IA en examen de fondo\buscador_anterioridades" usuario@ip-servidor:/opt/buscador

# Opción B: clonar desde GitHub si se sube el repositorio
git clone https://github.com/cihenzi/buscador-anterioridades /opt/buscador
```

El artefacto pesado `data/marcas_oponibles.parquet` también debe transferirse porque no se regenera automáticamente. Si el servidor tiene buena conexión, se puede regenerar directamente ahí con `construir_datos.py`.

**Estructura de carpetas esperada en el servidor:**

```
/opt/buscador/
├── buscador/
├── data/
│   ├── Datos Marcas.xlsx
│   └── marcas_oponibles.parquet
├── api.py
├── index.html
├── requirements.txt
└── ...
```

---

#### 12.1.3 Instalar dependencias en Linux

```bash
# 1. Instalar Miniconda (si no está instalado)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc

# 2. Crear el entorno
conda create -n buscador python=3.11 -y
conda activate buscador

# 3. Instalar dependencias
cd /opt/buscador
pip install -r requirements.txt

# 4. Instalar gunicorn (reemplaza a python api.py en producción)
pip install gunicorn
```

---

#### 12.1.4 Verificar que todo funciona antes de configurar el servicio

```bash
conda activate buscador
cd /opt/buscador

# Correr los tests
pytest    # debe dar 79 passed

# Probar la API manualmente
gunicorn --bind 0.0.0.0:5001 --workers 1 --timeout 120 api:app
# Abrir http://ip-servidor:5001 desde el navegador
```

> **Por qué `--workers 1`:** el universo de marcas (parquet + representaciones canónica/fonética precalculadas) se carga en memoria por cada worker. Con 1 worker es más que suficiente para el volumen esperado de usuarios públicos; las consultas son instantáneas (<1 segundo).

---

#### 12.1.5 Configurar como servicio systemd (arranque automático)

Para que el buscador quede corriendo permanentemente y se reinicie solo si el servidor se reinicia:

```bash
sudo nano /etc/systemd/system/buscador.service
```

Contenido del archivo:

```ini
[Unit]
Description=Buscador de Anterioridades INAPI
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/buscador
Environment="PATH=/home/usuario/miniconda3/envs/buscador/bin"
ExecStart=/home/usuario/miniconda3/envs/buscador/bin/gunicorn \
    --bind 127.0.0.1:5001 \
    --workers 1 \
    --timeout 120 \
    --access-logfile /var/log/buscador/access.log \
    --error-logfile /var/log/buscador/error.log \
    api:app
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

> **Importante:** reemplaza `/home/usuario/miniconda3` con la ruta real de Miniconda en el servidor (`which python` dentro del entorno activado lo confirma). Reemplaza `www-data` con el usuario que corresponda.

Crear el directorio de logs y activar el servicio:

```bash
sudo mkdir -p /var/log/buscador
sudo chown www-data:www-data /var/log/buscador

sudo systemctl daemon-reload
sudo systemctl enable buscador
sudo systemctl start buscador

# Verificar que está corriendo
sudo systemctl status buscador
```

---

#### 12.1.6 Configurar nginx como proxy inverso (acceso por puerto 80)

Para que el buscador sea accesible por `http://dominio.inapi.cl` en lugar de `http://ip:5001`:

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/buscador
```

Contenido:

```nginx
server {
    listen 80;
    server_name buscador.inapi.cl;   # reemplazar con el dominio real

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 120s;
    }
}
```

Activar y recargar:

```bash
sudo ln -s /etc/nginx/sites-available/buscador /etc/nginx/sites-enabled/
sudo nginx -t          # verificar que la config es válida
sudo systemctl reload nginx
```

---

#### 12.1.7 Diferencias de comportamiento entre Windows y Linux

| Aspecto | Windows (desarrollo) | Linux (producción) |
|---|---|---|
| Variable SSL | `set SSL_CERT_FILE=` | `unset SSL_CERT_FILE` (normalmente no necesaria) |
| Separador de rutas | `\` | `/` (el código usa `pathlib.Path`, es transparente) |
| Servidor de desarrollo | `python api.py` | `gunicorn --bind 0.0.0.0:5001 --workers 1 api:app` |
| Arranque automático | Manual | systemd |

El código no requiere modificaciones para correr en Linux gracias al uso de `pathlib.Path` en todo el proyecto. Las únicas diferencias son operativas (cómo se arranca y cómo se gestiona el servicio).

---

#### 12.1.8 Actualización de los datos en Linux

Cuando lleguen datos nuevos, el proceso en Linux es el mismo que en Windows:

```bash
conda activate buscador
cd /opt/buscador

# 1. Reemplazar data/Datos Marcas.xlsx con el archivo nuevo
# 2. Regenerar marcas_oponibles.parquet
python construir_datos.py

# 3. Reiniciar el servicio para que cargue el parquet nuevo
sudo systemctl restart buscador
```

---

### 12.2 Migración a SQL Server

Cuando llegue el acceso a SQL Server gestionado por TIC, la transición del buscador está diseñada para ser mínima: **el motor, la API y el frontend no cambian nada**. El único punto de contacto con la fuente de datos es `construir_datos.py` + `datos.py`.

#### Paso 1 — Confirmar el esquema con TIC

Antes de tocar código, TIC debe proporcionar el nombre exacto de la tabla y sus columnas:

| Dato necesario | Valor actual (Excel) | Valor SQL Server (a confirmar) |
|---|---|---|
| Nombre de la tabla | `data/Datos Marcas.xlsx` | ej. `dbo.marcas_vigentes` |
| Columna identificador de marca | `Mark Code (Ip Name)` | a confirmar |
| Columna nombre de la marca | `Mark Name` | a confirmar |
| Columna clase NCL | `Nice Class Code` | a confirmar |
| Columna número de solicitud | `Nro_sol` | a confirmar |
| Columna estado | `Status Name` | a confirmar |
| **Columna número de registro oficial** | **No existe en el Excel** | **a confirmar — crítico** |

La última fila es la más importante: el número de registro oficial (el que los examinadores citan en observaciones de Art. 20 h) no está en el export Excel actual. Con SQL Server sí estará disponible, lo que por fin permitirá medir el recall del buscador contra rechazos reales.

#### Paso 2 — Actualizar `config.py`

Descomentar y completar el bloque SQL que ya existe al final del archivo:

```python
# Descomentar cuando TIC confirme los nombres reales:
SQL_SERVER_CONN: str = (
    "mssql+pyodbc://usuario:password@servidor/base"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)
SQL_TABLE_MARCAS: str   = "dbo.marcas_vigentes"   # confirmar con TIC
SQL_COL_MARK_CODE: str  = "mark_code"              # confirmar con TIC
SQL_COL_NOMBRE: str     = "nombre_marca"           # confirmar con TIC
SQL_COL_CLASE: str      = "clase_ncl"              # confirmar con TIC
SQL_COL_NRO_SOL: str    = "nro_solicitud"          # confirmar con TIC
SQL_COL_ESTADO: str     = "estado"                 # confirmar con TIC
SQL_COL_NRO_REGISTRO: str = "nro_registro"         # confirmar con TIC
```

#### Paso 3 — Reconstruir el índice desde SQL Server

```bash
python construir_datos.py --fuente sql
sudo systemctl restart buscador
```

El parámetro `--fuente sql` ya está implementado en `construir_datos.py`. Internamente llama a `datos.cargar_desde_sql()`, que también ya existe en `datos.py`. No hay que escribir código nuevo.

#### Paso 4 — Validar el recall

Con el número de registro oficial disponible, medir el rendimiento real del motor:

```bash
python validar.py
```

Esto ejecuta el buscador contra las ~9.000 observaciones de Art. 20 h) de 2025 y reporta cuántas veces encuentra la anterioridad correcta en el top-1/3/5/10. El script ya existe y está listo; solo faltaba el campo de cruce.

#### Paso 5 — Ampliar el universo de anterioridades (opcional)

SQL Server también permite incluir **solicitudes en trámite** que aún no están concedidas pero que son oponibles según Art. 20 h). Hoy el Excel solo tiene marcas concedidas. Para incluirlas, agregar los estados de trámite vigente al conjunto `ESTADOS_OPONIBLES` en `config.py` y reconstruir el índice.

---

### 12.3 Resumen de esfuerzo estimado

| Tarea | Quién | Tiempo estimado |
|---|---|---|
| Despliegue en Linux (pasos 12.1.1 a 12.1.7) | TIC + Camila | Medio día |
| Configuración de nginx y dominio | TIC | 1-2 horas |
| Transferencia del modelo offline (si hay firewall) | TIC | 1 hora |
| Transición a SQL Server (pasos 12.2.1 a 12.2.3) | Camila | 1 hora una vez confirmado el esquema |
| Validación de recall | Camila | 2 horas |
| Actualización automática nocturna del índice (cron job) | TIC | 2 horas |


---
## 13. Decisiones de diseño relevantes

Estas decisiones se tomaron durante el desarrollo y vale la pena que TI las conozca antes de intervenir en el código:

**Señal semántica eliminada, comparación vectorizada con rapidfuzz.** El motor pasó de un enfoque de embeddings + FAISS a una comparación exhaustiva ortográfica/fonética con `rapidfuzz.process.cdist`. Motivo: anisotropía de los embeddings en denominaciones cortas/inventadas (piso de similitud artificialmente alto) y una ganancia de rendimiento de ~13s a ~0.11s por consulta al vectorizar en C++.

**SQLite → no hay base de datos.** El buscador no usa base de datos. El único artefacto es el Parquet de marcas oponibles. Esto simplifica el despliegue enormemente: copiar la carpeta es suficiente.

**Google Drive + archivos binarios grandes no mezclan bien.** Esto fue un riesgo real cuando el proyecto usaba un índice FAISS de ~335 MB (se corrompió una vez por sincronización durante la escritura). Ya no aplica al haberse eliminado ese artefacto, pero se mantiene como precaución general: pausar Drive durante operaciones de archivos grandes en `data/`.

**Frontend single-file.** El archivo `index.html` contiene CSS, JavaScript y las 45 descripciones de clases NCL incrustadas. No depende de npm, webpack ni CDN externos. Esto simplifica el despliegue: basta con que Flask sirva ese archivo.

**Pesos del motor son configurables sin tocar lógica.** Los parámetros `PESO_ORTOGRAFICO`, `PESO_FONETICO`, `CANDIDATOS_PREFILTRO`, `TOP_RESULTADOS`, `FACTOR_CLASE_NO_RELACIONADA`, los umbrales de genericidad por frecuencia (`UMBRAL_FRECUENCIA_GENERICO`, `CONTEO_MINIMO_GENERICO`) y los pesos de Jaro-Winkler (`PESO_*_JARO_WINKLER_*`) están en `config.py`. Cambiarlos no requiere reconstruir el dataset (los umbrales de genericidad sí requieren que el índice recalcule sus tablas de frecuencia, lo que ocurre automáticamente al reiniciar la API, sin necesidad de correr `construir_datos.py`).

**El invariante de seguridad del prefiltro se mantiene aunque se agreguen señales nuevas.** Cualquier ajuste o descuento que se agregue al recálculo exacto (paso 2) debe poder solo *bajar* un score, nunca subirlo por encima del score bruto calculado en el prefiltro vectorizado (paso 1, `MotorBusqueda.buscar()`). Es la razón concreta por la que los n-gramas de caracteres (ver 4.2.5) se descartaron del cálculo final en vez de solo bajarles el peso: al usarse con `min()`, cualquier señal nueva que sea inestable en casos borde puede introducir falsos negativos aunque el resto del motor esté bien calibrado. Antes de sumar una señal nueva al score, validarla contra una muestra de marcas reales con variantes de un solo carácter (inserción, borrado y sustitución), no solo contra los casos que motivaron el cambio.

**Genericidad condicionada por clase NCL, no global.** Ver 4.2.2. Una tabla de frecuencia global de palabras confundiría "término descriptivo de un rubro" con "palabra común del español que aparece en marcas de rubros muy distintos sin describir ninguno en particular".

---

## 14. Bitácora de cambios — agosto 2026

Cambios al motor de búsqueda hechos en respuesta a casos reportados por el equipo, en orden cronológico. Todos preservan el invariante de seguridad del prefiltro (ver sección 13) y están cubiertos por tests (`pytest` → 79 passed al cierre de esta bitácora).

| Fecha | Caso reportado | Causa | Corrección | Dónde |
|---|---|---|---|---|
| 05-ago-2026 | "brasas del rey" (100%) vs "brasas del rei" (0%) | (a) `clave_fonetica()` no trataba "vocal+y" final de palabra como diptongo /ei/; (b) el residuo tras descontar palabras comunes ("rey"/"rei", 3 caracteres) era demasiado corto para un ratio de edición confiable | (a) regla `_RE_Y_DIPTONGO`; (b) piso `LONGITUD_MINIMA_RESIDUO_DESCUENTO` (4 caracteres) que omite el descuento sobre residuos cortos | `normalizacion.py`, `busqueda._residuo_muy_corto()`, `config.py` |
| 06-ago-2026 AM | "cervezas ricas" vs "cerveza tribal" → 77% | "cervezas"/"cerveza" no son la misma cadena exacta, así que el descuento de palabra genérica compartida nunca se activaba | `normalizacion.lema()`: singularización naive (vocal + "s") usada solo para decidir qué palabras cuentan como "la misma" al detectar términos comunes | `normalizacion.py`, `busqueda._palabras_comunes_fuera()`, `config.LONGITUD_MINIMA_PALABRA_LEMA` |
| 06-ago-2026 PM | Solicitud de acercar el motor al criterio de un examinador humano (revisión de literatura académica y doctrina marcaria — *Sabel v. Puma* C-251/95, Winkler 1990, Marslen-Wilson 1987) | El descuento de genéricos de la mañana solo cubría coincidencia exacta/de lema entre las dos marcas comparadas, no sinónimos ortográficos del mismo término genérico; ninguna señal ponderaba especialmente el inicio de palabra | (1) Genericidad por frecuencia de la palabra en la clase NCL real del candidato (`indice.FrecuenciasPalabras`); (2) Jaro-Winkler combinado con la métrica existente en ambas señales (`_score_ortografico_base` / `_score_fonetico_base`); (3) n-gramas de caracteres: implementados y probados, **descartados** del score tras detectar que reintroducían el problema del 05-ago-2026 en casos de inserción/borrado de una letra (ver 4.2.5) | `indice.py` (nuevo), `busqueda.py`, `config.py` |
| 06-ago-2026 PM (continuación) | "cervezas ricas" vs "cerveza yal" → score muy alto pese a no tener relación real | El piso de longitud del 05-ago-2026 (`_residuo_muy_corto`) ignoraba el descuento de genéricos apenas UN residuo era corto, sin mirar si ese residuo corto se parecía o no al del otro lado: protegía por igual "rey"/"rei" (misma palabra, typo) y "ricas"/"yal" (palabras distintas que solo coinciden en ser cortas) | `busqueda._residuos_variante_corta()`: exige además que la distancia de edición absoluta (Levenshtein) entre ambos residuos sea baja (`config.DISTANCIA_MAXIMA_RESIDUO_CORTO`, 1 carácter) para considerarlos variante de tipeo; si son distintos, el descuento se aplica con normalidad | `busqueda.py`, `config.py` |

Ver la sección 4.2 para el detalle técnico y doctrinal de cada fix, y el docstring del módulo `buscador/busqueda.py` para la versión "para desarrolladores" de esta misma bitácora.

---

## 15. Contacto y mantenimiento

**Responsable técnica:** Camila Henzi  
**Unidad:** Departamento de Marcas, INAPI

Para cualquier intervención en el código o la infraestructura, el orden correcto es:

1. Leer este documento.
2. Correr `pytest` para verificar que el estado inicial es verde.
3. Hacer el cambio.
4. Correr `pytest` nuevamente para verificar que todo sigue verde.
5. Si cambia la base de marcas o la lógica de normalización/indexación, reconstruir el índice (ver sección 7.4).