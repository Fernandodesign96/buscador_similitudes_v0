/**
 * Genera public/marcas-meta.json desde Datos Marcas.xlsx (solo frontend).
 * Uso (desde frontend/): bun run build:marcas-meta
 */
import { readFile, writeFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as XLSX from "xlsx";

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const xlsxPath = path.join(raiz, "claseniza_y_coberturas", "Datos Marcas.xlsx");
const outPath = path.join(raiz, "public", "marcas-meta.json");

const COL_MARK_CODE = "Mark Code (Ip Name)";
const COL_NOMBRE = "Mark Name";
const COL_CLASE = "Nice Class Code";
const COL_NRO_SOL = "Nro_sol";
const COL_STATUS = "Status Name";
const COL_ANIO = "Año de Status Date";

const ESTADOS_OPONIBLES = new Set([
  "Registrada",
  "Aguardando por renovación de marca nacional",
  "Aguardando que resolución de aceptación parcial a registro quede en firme",
  "Aguardando que resolución de aceptación a registro sea publicada",
  "Aguardando que fallo de aceptación a registro quede en firme",
  "Aguardando que fallo de aceptación parcial a registro quede en firme",
]);

type Fila = {
  mark_code: number;
  nombre: string;
  clases: number | null;
  solicitudes: unknown;
  estado: string;
  anio_estado: number;
};

function esNumero(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function solicitudBase(nro: unknown, clase: number | null): string {
  let n = String(nro).trim();
  if (n.endsWith(".0")) n = n.slice(0, -2);
  const c = clase != null ? String(clase) : "";
  if (c && n.endsWith(c)) return n.slice(0, -c.length);
  return n;
}

function celdaNumero(value: unknown): number | null {
  if (esNumero(value)) return value;
  if (typeof value === "string" && value.trim()) {
    const n = Number(value.replace(",", "."));
    return Number.isFinite(n) ? n : null;
  }
  return null;
}

async function main() {
  const buffer = await readFile(xlsxPath);
  const workbook = XLSX.read(buffer, {
    type: "buffer",
    sheets: ["Hoja1"],
    cellDates: false,
  });
  const sheet = workbook.Sheets.Hoja1;
  if (!sheet) {
    throw new Error('No se encontró la hoja "Hoja1" en Datos Marcas.xlsx');
  }

  const rows = XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet, {
    defval: null,
    raw: true,
  });

  const filtradas: Fila[] = [];
  for (const row of rows) {
    const estado = String(row[COL_STATUS] ?? "").trim();
    if (!ESTADOS_OPONIBLES.has(estado)) continue;
    const code = celdaNumero(row[COL_MARK_CODE]);
    if (code == null) continue;
    const claseRaw = celdaNumero(row[COL_CLASE]);
    const anioRaw = celdaNumero(row[COL_ANIO]);
    filtradas.push({
      mark_code: Math.trunc(code),
      nombre: String(row[COL_NOMBRE] ?? "").trim(),
      clases: claseRaw == null ? null : Math.trunc(claseRaw),
      solicitudes: row[COL_NRO_SOL],
      estado,
      anio_estado: anioRaw == null ? Number.NaN : anioRaw,
    });
  }

  filtradas.sort((a, b) => {
    const ay = Number.isFinite(a.anio_estado) ? a.anio_estado : -Infinity;
    const by = Number.isFinite(b.anio_estado) ? b.anio_estado : -Infinity;
    return by - ay;
  });

  const grupos = new Map<number, Fila[]>();
  for (const fila of filtradas) {
    const list = grupos.get(fila.mark_code);
    if (list) list.push(fila);
    else grupos.set(fila.mark_code, [fila]);
  }

  const statusSet = new Set<string>();
  for (const fila of filtradas) statusSet.add(fila.estado);
  const statusList = [...statusSet].sort();
  const statusIdx = new Map(statusList.map((s, i) => [s, i]));

  const nombres: string[] = [];
  const sidx: number[] = [];
  const anios: number[] = [];
  const codes: number[] = [];
  const clases: number[][] = [];
  const sols: string[][] = [];

  for (const [code, g] of grupos) {
    const first = g[0];
    if (!first) continue;
    const claseSet = [
      ...new Set(
        g
          .map((r) => r.clases)
          .filter((c): c is number => c != null),
      ),
    ].sort((a, b) => a - b);
    const nroSet = [
      ...new Set(
        g
          .filter((r) => r.solicitudes != null && r.solicitudes !== "")
          .map((r) => solicitudBase(r.solicitudes, r.clases)),
      ),
    ].sort();
    nombres.push(first.nombre);
    sidx.push(statusIdx.get(first.estado) ?? 0);
    anios.push(Number.isFinite(first.anio_estado) ? Math.trunc(first.anio_estado) : 0);
    codes.push(code);
    clases.push(claseSet);
    sols.push(nroSet);
  }

  const payload = {
    e: statusList,
    n: nombres,
    s: sidx,
    a: anios,
    mark_code: codes,
    c: clases,
    q: sols,
  };

  const json = JSON.stringify(payload);
  await writeFile(outPath, json, "utf8");
  const size = (await stat(outPath)).size;
  console.log(`Wrote ${outPath} (${nombres.length} marcas, ${size} bytes)`);
}

void main();
