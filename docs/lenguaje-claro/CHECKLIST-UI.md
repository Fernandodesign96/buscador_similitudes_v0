# Checklist Lenguaje Claro — UI del buscador

**Fecha revisión:** 31-07-2026  
**Revisión anterior:** 29-07-2026  
**Textos centralizados en:** `frontend/src/lib/copy.ts`  
**Fuentes PDF:** `docs/lenguaje-claro/`

| PDF | Uso |
|-----|-----|
| `lenguaje-claro-recomendaciones.pdf` | Pirámide invertida, voz activa, enlaces descriptivos |
| `instrumento-evaluacion-sitios-web.pdf` | Dimensión 1: Contenido y lenguaje claro |
| `meta-mei.pdf` | Contexto brecha calidad web INAPI (74 %) |
| `ui-kit-gobierno-3.0.1.pdf` | Referencia diseño Gobierno de Chile |

## Cambios 31-07-2026 (reunión Bernarda + Camila)

- H1 y breadcrumb: «Buscador de marcas» (antes «Buscador de anterioridades»).
- Revisión integral de copy en `copy.ts` (lead, ayuda, resultados, meta).
- Disclaimer legal acordado al **final del contenido principal**, siempre visible (con o sin búsqueda).
- Eliminado `disclaimerShort` antes del formulario (redundante con aviso legal).
- Selector NCL: sin cambios funcionales (mejora futura pendiente).

## A. Estructura y organización

| ID | Criterio | Estado | Implementación |
|----|----------|--------|----------------|
| A1 | Mensaje principal arriba | ✅ | `copy.page.lead` bajo el H1 |
| A2 | Pirámide invertida | ✅ | Lead → opciones → ayuda → formulario → resultados |
| A3 | Secciones con encabezados | ✅ | H1, H2 en ayuda y aviso legal |
| A4 | ≤110 palabras por sección | ✅ | Párrafos acortados en `copy.ts` y ayuda |
| A5 | Solo información necesaria | ✅ | Aviso legal siempre visible al final; ayuda colapsable |

## B. Lenguaje claro

| ID | Criterio | Estado | Implementación |
|----|----------|--------|----------------|
| B1 | Voz activa | ✅ | «Escribe», «Revisa», «Combinamos» |
| B2 | Palabras comunes | ✅ | «marca registrada» en vez de «anterioridad» |
| B3 | Siglas definidas | ✅ | «Clasificación Internacional de Niza (NCL)» |
| B4 | Sin extranjerismos | ✅ | Sin anglicismos en copy principal |
| B5 | Tono positivo | ✅ | Indica qué hacer según porcentaje |
| B6 | Tuteo consistente | ✅ | «tu marca», «escribiste» (aviso legal en tercera persona) |
| B7 | Sin relleno | ✅ | Eliminadas frases burocráticas |

## C. Redacción y concisión

| ID | Criterio | Estado | Implementación |
|----|----------|--------|----------------|
| C1 | Orden sujeto-verbo-predicado | ✅ | Oraciones directas |
| C2 | Presente simple | ✅ | «indica», «muestra», «combinamos» |
| C3 | Oraciones cortas | ✅ | Máx. ~25 palabras por oración (excepto aviso legal) |
| C4 | Una idea por párrafo | ✅ | Párrafos separados en ayuda y aviso legal |
| C5 | Párrafos cortos | ✅ | 2–4 líneas en desktop |
| C6 | Resumen al inicio (texto extenso) | ✅ | «Resumen:» en acordeón de ayuda |
| C7 | Listas para requisitos/niveles | ✅ | Lista de niveles de similitud |

## D. Ortografía y formato

| ID | Criterio | Estado | Implementación |
|----|----------|--------|----------------|
| D1 | Ortografía revisada | ✅ | Revisión manual 31-07-2026 |
| D2 | Puntuación correcta | ✅ | Puntos seguidos preferidos |
| D3 | Espacio entre párrafos | ✅ | `space-y-*`, márgenes |
| D4 | Alineación izquierda | ✅ | `text-left` en contenido |
| D5 | Listas para enumeraciones | ✅ | Niveles NCL, niveles similitud |
| D6 | Negritas puntuales | ✅ | Una negrita por bloque en ayuda |
| D7 | Sin MAYÚSCULAS decorativas | ✅ | Nav y labels sin `uppercase` |

## E. Objetividad y fiabilidad

| ID | Criterio | Estado | Implementación |
|----|----------|--------|----------------|
| E1 | Contenido objetivo | ✅ | Sin adjetivos promocionales |
| E2 | Autoría INAPI visible | ✅ | Header y footer institucional |
| E3 | Fecha de actualización | ✅ | Pie: «Última actualización: 31-07-2026» |
| E4 | Título fiel al contenido | ✅ | H1 = «Buscador de marcas» |

## F. Enlaces y referencias

| ID | Criterio | Estado | Implementación |
|----|----------|--------|----------------|
| F1 | Nombre enlace = destino | ⚠️ | Enlaces chrome son decorativos (`#`); pendiente URLs reales |
| F2 | Sin «clic aquí» | ✅ | Enlaces con texto descriptivo |
| F3 | Botones significativos | ✅ | «Buscar marcas parecidas», opciones A/B descriptivas |
| F4 | Documentos con formato/peso | N/A | Sin descargas en esta pantalla |
| F5 | Enlaces fuera del cuerpo | ✅ | Enlaces en footer, no en párrafos de ayuda |

## G. Datos personales y PI

| ID | Criterio | Estado | Implementación |
|----|----------|--------|----------------|
| G1 | Sin datos personales en HTML | ✅ | Solo datos institucionales INAPI |
| G2 | Derechos ARCO | ✅ | Enlace «Política de privacidad y derechos ARCO» |
| G3 | Condiciones de uso | ✅ | Licencia CC BY 4.0 en pie |

## H. Archivo

| ID | Criterio | Estado | Implementación |
|----|----------|--------|----------------|
| H1 | Versiones archivadas rotuladas | N/A | No aplica a esta pantalla |

**Total:** 37 aplicables · 35 cumplidos · 1 parcial (F1) · 1 N/A (F4) · 1 N/A (H1)
