/**
 * Genera public/data/ncl-coberturas.json desde el CSV del clasificador INAPI
 * (carpeta local gitignored: claseniza_y_coberturas/).
 * Uso (desde frontend/): bun run build:ncl
 */
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const src = path.join(
  raiz,
  "claseniza_y_coberturas",
  "ClasificadorINAPI_2026-08-12.csv",
);
const dst = path.join(raiz, "public", "data", "ncl-coberturas.json");

function parseCsvLine(line: string): string[] {
  const out: string[] = [];
  let current = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }
    if (ch === ";" && !inQuotes) {
      out.push(current);
      current = "";
      continue;
    }
    current += ch;
  }
  out.push(current);
  return out;
}

type Item = {
  id: number;
  clase: number;
  cobertura: string;
  tipo: "Producto" | "Servicio";
};

async function main() {
  const raw = await readFile(src, "utf8");
  const text = raw.charCodeAt(0) === 0xfeff ? raw.slice(1) : raw;
  const lines = text.split(/\r?\n/).filter((line) => line.trim().length > 0);
  const header = parseCsvLine(lines[0] ?? "");
  const idxClase = header.indexOf("Clase");
  const idxEs = header.indexOf("Descripción en Español");
  const idxTipo = header.indexOf("Tipo");
  if (idxClase < 0 || idxEs < 0 || idxTipo < 0) {
    throw new Error("El CSV no tiene las columnas esperadas.");
  }

  const seen = new Set<string>();
  const items: Item[] = [];

  for (const line of lines.slice(1)) {
    const cols = parseCsvLine(line);
    const claseRaw = (cols[idxClase] ?? "").trim();
    const cobertura = (cols[idxEs] ?? "").trim().replace(/\s+/g, " ");
    const tipo = (cols[idxTipo] ?? "").trim();
    if (!/^\d+$/.test(claseRaw) || !cobertura) continue;
    const clase = Number(claseRaw);
    if (clase < 1 || clase > 45) continue;
    if (tipo !== "Producto" && tipo !== "Servicio") continue;
    const key = `${clase}|${cobertura.toLowerCase()}|${tipo}`;
    if (seen.has(key)) continue;
    seen.add(key);
    items.push({ id: items.length + 1, clase, cobertura, tipo });
  }

  await mkdir(path.dirname(dst), { recursive: true });
  await writeFile(dst, JSON.stringify(items), "utf8");
  console.log(`Guardado ${items.length} coberturas en ${dst}`);
}

void main();
