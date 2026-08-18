# Lenguaje Claro — Documentación de referencia

Carpeta con los criterios oficiales de calidad web y Lenguaje Claro para INAPI.

## Archivos PDF

> **Nota:** Los PDF siguientes no se versionan en Git (están en `.gitignore` por su tamaño).  
> Colócalos manualmente en esta carpeta en cada máquina de desarrollo.

| Archivo | Descripción |
|---------|-------------|
| `lenguaje-claro-recomendaciones.pdf` | Recomendaciones de Lenguaje Claro para la web (pirámide invertida, voz activa, enlaces) |
| `instrumento-evaluacion-sitios-web.pdf` | Instrumento de evaluación de calidad para sitios web (Secretaría de Gobierno Digital) |
| `meta-mei.pdf` | Plan de transformación digital INAPI — brechas de calidad web |
| `ui-kit-gobierno-3.0.1.pdf` | UI Kit Gobierno de Chile 3.0.1 |

## Aplicación en este MVP

- **Textos de la interfaz:** [`frontend/src/lib/copy.ts`](../../frontend/src/lib/copy.ts)
- **Checklist de cumplimiento (39 criterios):** [CHECKLIST-UI.md](./CHECKLIST-UI.md)

## Dimensiones guía (resumen)

1. **Claridad** — Frases cortas, una idea por oración.
2. **Concisión** — Solo lo necesario para completar la tarea (buscar marcas parecidas).
3. **Estructura** — Mensaje principal arriba; detalles en acordeón colapsable.
4. **Voz activa y tuteo** — «Escribe tu marca», «Revisa los resultados».
5. **Siglas definidas** — NCL explicada en la primera mención.
6. **Transparencia** — El porcentaje orienta; no reemplaza el examen de INAPI.

## Cómo leer los PDFs desde el proyecto

Los agentes y desarrolladores pueden extraer texto con:

```bash
source .venv/bin/activate
pip install pypdf
python3 -c "
from pypdf import PdfReader
r = PdfReader('docs/lenguaje-claro/lenguaje-claro-recomendaciones.pdf')
print(r.pages[0].extract_text())
"
```
