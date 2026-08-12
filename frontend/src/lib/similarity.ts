export type SimilarityLevel = "high" | "medium" | "low";

/** Umbral interno del motor (no se muestra al usuario). Alineado con api.py */
export const SIMILITUD_MIN_RESULTADOS = 75;

export function similarityLevel(value: number): SimilarityLevel {
  if (value >= SIMILITUD_MIN_RESULTADOS) return "high";
  if (value >= 50) return "medium";
  return "low";
}

/** Ancho de barra 0–100. El valor numérico no se renderiza en la UI. */
export function barWidth(value: number): number {
  if (!Number.isFinite(value)) return 0;
  return Math.min(100, Math.max(0, value));
}
