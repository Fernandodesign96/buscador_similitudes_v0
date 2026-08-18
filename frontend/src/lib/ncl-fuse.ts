import Fuse, { type Expression, type FuseResult } from "fuse.js";
import type { NclCobertura } from "./ncl-coberturas";

const STOPWORDS = new Set([
  "de",
  "la",
  "el",
  "los",
  "las",
  "un",
  "una",
  "unos",
  "unas",
  "y",
  "o",
  "para",
  "con",
  "en",
  "a",
  "del",
  "al",
  "por",
  "and",
  "or",
  "the",
]);

export function buildCoberturaFuse(items: NclCobertura[]) {
  return new Fuse(items, {
    keys: [
      { name: "cobertura", weight: 0.85 },
      { name: "clase", weight: 0.15 },
    ],
    threshold: 0.36,
    ignoreLocation: true,
    minMatchCharLength: 2,
    includeScore: true,
    shouldSort: true,
    useExtendedSearch: true,
  });
}

function tokensDe(parte: string): string[] {
  return parte
    .split(/\s+(?:AND|Y)\s+|\s+/i)
    .map((t) => t.replace(/[^\p{L}\p{N}]+/gu, ""))
    .filter((t) => t.length >= 2 && !STOPWORDS.has(t.toLowerCase()));
}

function expresionAnd(parte: string): string | Expression {
  const tokens = tokensDe(parte);
  if (tokens.length === 0) return parte.trim();
  if (tokens.length === 1) return { cobertura: tokens[0] };
  return { $and: tokens.map((t) => ({ cobertura: t })) };
}

function fusionar(
  a: FuseResult<NclCobertura>[],
  b: FuseResult<NclCobertura>[],
  limit: number,
): NclCobertura[] {
  const byId = new Map<number, FuseResult<NclCobertura>>();
  for (const hit of [...a, ...b]) {
    const prev = byId.get(hit.item.id);
    if (!prev || (hit.score ?? 1) < (prev.score ?? 1)) {
      byId.set(hit.item.id, hit);
    }
  }
  return [...byId.values()]
    .sort((x, y) => (x.score ?? 1) - (y.score ?? 1))
    .slice(0, limit)
    .map((h) => h.item);
}

/** Búsqueda difusa con AND/OR (también «y» / «o» entre palabras). */
export function searchCoberturas(
  fuse: Fuse<NclCobertura>,
  raw: string,
  limit = 40,
): NclCobertura[] {
  const q = raw.trim();
  if (q.length < 2) return [];

  const orParts = q
    .split(/\s+(?:OR|O)\s+/i)
    .map((s) => s.trim())
    .filter(Boolean);

  if (orParts.length > 1) {
    const expr: Expression = { $or: orParts.map(expresionAnd) };
    return fuse.search(expr, { limit }).map((r) => r.item);
  }

  const andHits = fuse.search(expresionAnd(q), { limit: limit * 2 });
  const phraseHits = fuse.search(q, { limit });
  return fusionar(andHits, phraseHits, limit);
}
