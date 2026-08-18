import { copy } from "@/lib/copy";

const ESTADO_REGISTRADA = "Registrada";

/** Estados no vigentes: no se muestran como «En trámite». */
const MARCAS_NO_VIGENTES = [
  "rechazada",
  "rechazo",
  "caduca",
  "anulada",
  "cancelada",
  "abandonada",
  "abandonar",
  "desistida",
  "por no presentada",
  "no presentada",
  "cesada",
];

export type SemaforoEstado = "registrada" | "tramite" | "extinta";

function normalizar(estado: string): string {
  return estado
    .trim()
    .toLocaleLowerCase("es-CL")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

function esNoVigente(estado: string): boolean {
  const n = normalizar(estado);
  return MARCAS_NO_VIGENTES.some((k) => n.includes(normalizar(k)));
}

export function semaforoEstado(estado?: string): SemaforoEstado {
  const t = estado?.trim() ?? "";
  if (!t) return "tramite";
  if (t === ESTADO_REGISTRADA) return "registrada";
  if (esNoVigente(t)) return "extinta";
  return "tramite";
}

export function etiquetaEstadoCard(estado?: string): string {
  const s = semaforoEstado(estado);
  if (s === "registrada") return copy.results.registrada;
  if (s === "tramite") return copy.results.enTramite;
  return estado?.trim() || copy.results.estadoChip;
}

export function clasePuntoEstado(estado?: string): string | null {
  const s = semaforoEstado(estado);
  if (s === "registrada") {
    return "bg-[#22c55e] shadow-[0_0_6px_#22c55e]";
  }
  if (s === "tramite") {
    return "bg-[#f97316] shadow-[0_0_6px_#f97316]";
  }
  return null;
}
