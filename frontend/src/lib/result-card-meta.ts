import { copy } from "@/lib/copy";
import type { Resultado } from "@/lib/types";
import { SIMILITUD_MIN_RESULTADOS } from "@/lib/similarity";

export type NivelParecido = "muy" | "algo" | "poco";

export interface ResultCardDisplay extends Resultado {
  razonSocial?: string;
  nivelParecido: NivelParecido;
  resumenItems: string[];
}

function nivelFromScores(r: Resultado): NivelParecido {
  const peak = Math.max(r.desglose.ortografica, r.desglose.fonetica);
  if (peak >= SIMILITUD_MIN_RESULTADOS) return "muy";
  if (peak >= 50) return "algo";
  return "poco";
}

type BandaSimilitud =
  | "exacto"
  | "sobre95"
  | "sobre90"
  | "sobre85"
  | "sobre80"
  | "bajo80";

function bandaFromPct(value: number): BandaSimilitud {
  const n = Number.isFinite(value) ? value : 0;
  if (n >= 100) return "exacto";
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

export function textosParecido(
  r: Resultado,
  clasesBuscadas: number[],
): { escribir: string; pronunciar: string; clase: string | null } {
  const identicas = clasesIdenticas(clasesBuscadas, r);
  return {
    escribir: copy.results.bandaEscribir[bandaFromPct(r.desglose.ortografica)],
    pronunciar: copy.results.bandaPronunciar[bandaFromPct(r.desglose.fonetica)],
    clase:
      identicas.length > 0
        ? copy.results.bulletClaseIdentica(identicas)
        : null,
  };
}

export function buildResumenItems(
  r: Resultado,
  clasesBuscadas: number[],
): string[] {
  const t = textosParecido(r, clasesBuscadas);
  const items: string[] = [t.escribir, t.pronunciar];
  if (t.clase) items.push(t.clase);
  return items;
}

export function solicitudMasReciente(
  solicitudes: string[] | undefined,
): string | undefined {
  if (!solicitudes || solicitudes.length === 0) return undefined;
  let mejor = solicitudes[0];
  let mejorN = Number.parseInt(mejor, 10);
  for (const s of solicitudes) {
    const n = Number.parseInt(s, 10);
    if (!Number.isFinite(n)) continue;
    if (!Number.isFinite(mejorN) || n > mejorN) {
      mejor = s;
      mejorN = n;
    }
  }
  return mejor;
}

export function solicitudesMasRecientesPrimero(
  solicitudes: string[],
): string[] {
  return [...solicitudes].sort((a, b) => {
    const na = Number.parseInt(a, 10);
    const nb = Number.parseInt(b, 10);
    if (Number.isFinite(na) && Number.isFinite(nb)) return nb - na;
    return b.localeCompare(a);
  });
}

export function toResultCardDisplay(
  r: Resultado,
  clasesBuscadas: number[],
): ResultCardDisplay {
  const titular = r.titular?.trim();
  return {
    ...r,
    razonSocial: titular || undefined,
    nivelParecido: nivelFromScores(r),
    resumenItems: buildResumenItems(r, clasesBuscadas),
  };
}
