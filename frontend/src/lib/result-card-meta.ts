import { copy } from "@/lib/copy";
import type { Resultado } from "@/lib/types";
import { SIMILITUD_MIN_RESULTADOS } from "@/lib/similarity";

export type NivelParecido = "muy" | "algo" | "poco";

export interface ResultCardDisplay extends Resultado {
  razonSocial: string;
  nivelParecido: NivelParecido;
  resumenItems: string[];
}

function nivelFromScores(r: Resultado): NivelParecido {
  const peak = Math.max(r.desglose.ortografica, r.desglose.fonetica);
  if (peak >= SIMILITUD_MIN_RESULTADOS) return "muy";
  if (peak >= 50) return "algo";
  return "poco";
}

type BandaSimilitud = "sobre95" | "sobre90" | "sobre85" | "sobre80" | "bajo80";

function bandaFromPct(value: number): BandaSimilitud {
  const n = Number.isFinite(value) ? value : 0;
  if (n >= 95) return "sobre95";
  if (n >= 90) return "sobre90";
  if (n >= 85) return "sobre85";
  if (n >= 80) return "sobre80";
  return "bajo80";
}

function clasesIdenticas(clasesBuscadas: number[], r: Resultado): number[] {
  if (clasesBuscadas.length === 0) return [];
  return r.clases.filter((c) => clasesBuscadas.includes(c));
}

export function buildResumenItems(
  r: Resultado,
  clasesBuscadas: number[],
): string[] {
  const items = [
    copy.results.bandaEscribir[bandaFromPct(r.desglose.ortografica)],
    copy.results.bandaPronunciar[bandaFromPct(r.desglose.fonetica)],
  ];
  const identicas = clasesIdenticas(clasesBuscadas, r);
  if (identicas.length > 0) {
    items.push(copy.results.bulletClaseIdentica(identicas));
  }
  return items;
}

export function toResultCardDisplay(
  r: Resultado,
  clasesBuscadas: number[],
): ResultCardDisplay {
  return {
    ...r,
    razonSocial: r.titular?.trim() || "Nombre o razón social",
    nivelParecido: nivelFromScores(r),
    resumenItems: buildResumenItems(r, clasesBuscadas),
  };
}
