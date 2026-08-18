import type { BusquedaResponse, Resultado } from "@/lib/types";

/** Compacto: e=estados, n=nombre, s=idx estado, a=año, mark_code|m, c=clases, q=solicitudes. */
interface MarcasMetaFile {
  e: string[];
  n: string[];
  s: number[];
  a: number[];
  m?: number[];
  mark_code?: number[];
  c: number[][];
  q: string[][];
}

export interface MarcaExcelMeta {
  estado: string;
  anioEstado: number | null;
  mark_code: number;
  clases: number[];
  solicitudes: string[];
}

interface MetaCatalog {
  byCode: Map<number, MarcaExcelMeta>;
  byName: Map<string, MarcaExcelMeta[]>;
}

let loadPromise: Promise<MetaCatalog> | null = null;

function emptyCatalog(): MetaCatalog {
  return { byCode: new Map(), byName: new Map() };
}

function normNombre(nombre: string): string {
  return nombre.trim().toLocaleUpperCase("es-CL");
}

function clasesKey(clases: number[]): string {
  return [...clases].sort((a, b) => a - b).join(",");
}

function overlapCount(a: number[], b: number[]): number {
  if (a.length === 0 || b.length === 0) return 0;
  const setB = new Set(b);
  let n = 0;
  for (const c of a) {
    if (setB.has(c)) n += 1;
  }
  return n;
}

function parseFile(file: MarcasMetaFile): MetaCatalog {
  const byCode = new Map<number, MarcaExcelMeta>();
  const byName = new Map<string, MarcaExcelMeta[]>();
  const { e, n, s, a, c, q } = file;
  const codes = file.mark_code ?? file.m ?? [];
  for (let i = 0; i < n.length; i += 1) {
    const anio = a[i];
    const mark_code = codes[i];
    const row: MarcaExcelMeta = {
      estado: e[s[i]] ?? "",
      anioEstado: anio && anio > 0 ? anio : null,
      mark_code,
      clases: c[i] ?? [],
      solicitudes: q[i] ?? [],
    };
    if (mark_code != null) byCode.set(mark_code, row);
    const key = normNombre(n[i] ?? "");
    if (!key) continue;
    const list = byName.get(key);
    if (list) list.push(row);
    else byName.set(key, [row]);
  }
  return { byCode, byName };
}

export function loadMarcasMeta(): Promise<MetaCatalog> {
  if (!loadPromise) {
    loadPromise = fetch("/marcas-meta.json")
      .then((res) => {
        if (!res.ok) {
          throw new Error(`marcas-meta ${res.status}`);
        }
        return res.json() as Promise<MarcasMetaFile>;
      })
      .then(parseFile)
      .catch(() => {
        loadPromise = null;
        return emptyCatalog();
      });
  }
  return loadPromise;
}

export function pickMeta(
  r: Resultado,
  candidates: MarcaExcelMeta[],
): MarcaExcelMeta | undefined {
  if (candidates.length === 0) return undefined;
  if (candidates.length === 1) return candidates[0];

  const want = clasesKey(r.clases);
  const exact = candidates.filter((c) => clasesKey(c.clases) === want);
  if (exact.length >= 1) return exact[0];

  let best: MarcaExcelMeta | undefined;
  let bestOverlap = 0;
  for (const cand of candidates) {
    const n = overlapCount(r.clases, cand.clases);
    if (n > bestOverlap) {
      bestOverlap = n;
      best = cand;
    }
  }
  return bestOverlap > 0 ? best : candidates[0];
}

function applyMeta(r: Resultado, hit: MarcaExcelMeta): Resultado {
  return {
    ...r,
    estado: hit.estado || r.estado,
    anio_estado: hit.anioEstado ?? r.anio_estado,
    mark_code: hit.mark_code,
    solicitudes: hit.solicitudes.length > 0 ? hit.solicitudes : r.solicitudes,
  };
}

export function enrichResultado(r: Resultado, catalog: MetaCatalog): Resultado {
  if (r.mark_code != null) {
    const byCode = catalog.byCode.get(r.mark_code);
    if (byCode) return applyMeta(r, byCode);
  }
  const hit = pickMeta(r, catalog.byName.get(normNombre(r.nombre)) ?? []);
  if (!hit) return r;
  return applyMeta(r, hit);
}

export async function enrichBusqueda(
  data: BusquedaResponse,
): Promise<BusquedaResponse> {
  const catalog = await loadMarcasMeta();
  if (catalog.byCode.size === 0 && catalog.byName.size === 0) return data;
  return {
    ...data,
    resultados: data.resultados.map((r) => enrichResultado(r, catalog)),
  };
}
