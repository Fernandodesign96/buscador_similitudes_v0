import type { Resultado } from "@/lib/types";
import { SIMILITUD_MIN_RESULTADOS } from "@/lib/similarity";

export type NivelParecido = "muy" | "algo" | "poco";

export interface ResultCardDisplay extends Resultado {
  razonSocial: string;
  nivelParecido: NivelParecido;
  resumenColapsado: string;
}

function nivelFromScores(r: Resultado): NivelParecido {
  const peak = Math.max(r.desglose.ortografica, r.desglose.fonetica);
  if (peak >= SIMILITUD_MIN_RESULTADOS) return "muy";
  if (peak >= 50) return "algo";
  return "poco";
}

function partesSimilitud(r: Resultado): string[] {
  const partes: string[] = [];
  if (r.desglose.ortografica >= 50) partes.push("al escribir");
  if (r.desglose.fonetica >= 50) partes.push("al pronunciar");
  return partes;
}

function resumenClases(clasesBuscadas: number[], r: Resultado): string {
  if (clasesBuscadas.length === 0 || !r.clase_relacionada) {
    return "clase distinta";
  }
  const coinciden = r.clases.filter((c) => clasesBuscadas.includes(c));
  if (coinciden.length === 0) return "clase distinta";
  if (coinciden.length === 1) return `a la clase ${coinciden[0]}`;
  if (coinciden.length === 2) {
    return `a la clase ${coinciden[0]} y ${coinciden[1]}`;
  }
  return `a las clases ${coinciden.join(", ")}`;
}

export function buildResumenColapsado(
  r: Resultado,
  clasesBuscadas: number[],
): string {
  const nivel = nivelFromScores(r);
  const partes = partesSimilitud(r);

  if (nivel === "poco") return "Poco parecida";

  if (nivel === "algo") {
    if (partes.length === 0) return "Algo parecida · clase distinta";
    return `Algo parecida: ${partes.join(" y ")}`;
  }

  const claseTxt = resumenClases(clasesBuscadas, r);
  if (partes.length === 0) {
    return claseTxt === "clase distinta"
      ? "Muy parecida · clase distinta"
      : `Muy parecida: ${claseTxt}`;
  }
  const base = partes.join(", ");
  return claseTxt === "clase distinta"
    ? `Muy parecida: ${base}`
    : `Muy parecida: ${base} y ${claseTxt}`;
}

export function toResultCardDisplay(
  r: Resultado,
  clasesBuscadas: number[],
): ResultCardDisplay {
  return {
    ...r,
    razonSocial: r.titular?.trim() || "Nombre o razón social no disponible",
    nivelParecido: nivelFromScores(r),
    resumenColapsado: buildResumenColapsado(r, clasesBuscadas),
  };
}
