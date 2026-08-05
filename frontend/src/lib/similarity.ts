export type SimilarityLevel = "high" | "medium" | "low";

/** Umbral mínimo (%) para mostrar marcas en resultados — alineado con api.py */
export const SIMILITUD_MIN_RESULTADOS = 75;

export function similarityLevel(value: number): SimilarityLevel {
  if (value >= SIMILITUD_MIN_RESULTADOS) return "high";
  if (value >= 50) return "medium";
  return "low";
}

export function similarityColor(value: number): string {
  const level = similarityLevel(value);
  if (level === "high") return "#D32F2F";
  if (level === "medium") return "#FF9800";
  return "#43A047";
}

export function badgeColors(similarity: number): { bg: string; text: string } {
  if (similarity >= SIMILITUD_MIN_RESULTADOS) {
    return { bg: "#FFE5E5", text: "#D32F2F" };
  }
  return { bg: "#FFF3E0", text: "#FF9800" };
}
