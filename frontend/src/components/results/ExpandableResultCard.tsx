"use client";

import { Button } from "@/components/ui/button";
import { copy } from "@/lib/copy";
import { NCL_CLASSES } from "@/lib/ncl-classes";
import type { NivelParecido, ResultCardDisplay } from "@/lib/result-card-meta";
import { cn } from "@/lib/utils";

export interface ExpandableResultCardProps {
  marca: ResultCardDisplay;
  cardId: string;
  clasesBuscadas: number[];
  expanded: boolean;
  onToggle: () => void;
  onVerDetalle: () => void;
}

const NIVEL_BORDER: Record<NivelParecido, string> = {
  muy: "border-[#D32F2F]",
  algo: "border-[#FF9800]",
  poco: "border-[#43A047]",
};

const NIVEL_GUIA: Record<NivelParecido, string> = {
  muy: copy.results.guiaDetalle.muy,
  algo: copy.results.guiaDetalle.algo,
  poco: copy.results.guiaDetalle.poco,
};

const COL_MARCA = "sm:w-[220px] sm:min-w-[220px] sm:max-w-[220px]";

const CHIP_BASE =
  "inline-flex min-w-[7.75rem] items-center justify-center rounded-sm border px-2.5 py-1 text-center text-sm font-medium";

function chipEstadoClass(_estado: string): string {
  return cn(
    CHIP_BASE,
    "border-[#E0E0E0] bg-[#F0F4F8] text-[#455A64]",
  );
}

function ClasesList({
  clases,
  buscadas,
}: {
  clases: number[];
  buscadas: number[];
}) {
  const setBuscadas = new Set(buscadas);
  const coinciden = clases.filter((n) => setBuscadas.has(n));
  const otras = clases.filter((n) => !setBuscadas.has(n));

  const item = (n: number, destacada: boolean) => (
    <li
      key={n}
      className={cn(
        "text-sm leading-relaxed",
        destacada ? "font-semibold text-inapi-blue" : "text-inapi-muted",
      )}
    >
      Clase {n}: {NCL_CLASSES[n] ?? `Clase ${n}`}
    </li>
  );

  return (
    <div>
      <h4 className="mb-2 text-sm font-semibold text-[#111]">
        {copy.results.coberturaTitulo}
      </h4>
      {coinciden.length > 0 && (
        <ul className="mb-3 list-disc space-y-1 pl-5">
          {coinciden.map((n) => item(n, true))}
        </ul>
      )}
      {otras.length > 0 && (
        <ul className="list-disc space-y-1 pl-5">
          {otras.map((n) => item(n, false))}
        </ul>
      )}
    </div>
  );
}

export function ExpandableResultCard({
  marca,
  cardId,
  clasesBuscadas,
  expanded,
  onToggle,
  onVerDetalle,
}: ExpandableResultCardProps) {
  const estado = marca.estado?.trim() || copy.results.estadoChip;
  const panelId = `result-card-panel-${cardId}`;

  return (
    <article
      className={cn(
        "overflow-hidden rounded-lg border-2 bg-white",
        NIVEL_BORDER[marca.nivelParecido],
      )}
    >
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={expanded}
        aria-controls={panelId}
        className="relative w-full px-5 py-4 text-left transition-colors hover:bg-[#FAFAFA] sm:pr-36"
      >
        <span
          className={cn(
            "absolute top-1/2 right-5 hidden -translate-y-1/2 sm:inline-flex",
            chipEstadoClass(estado),
          )}
        >
          {estado}
        </span>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-stretch sm:gap-0">
          <div className={cn("min-w-0 shrink-0", COL_MARCA)}>
            <p className="text-lg font-bold tracking-wide text-[#111]">
              {marca.nombre}
            </p>
            <p className="mt-1 text-base font-semibold leading-snug text-[#373737]">
              {marca.razonSocial}
            </p>
          </div>

          <div
            className="hidden w-px shrink-0 self-stretch bg-[#E6E6E6] sm:mx-4 sm:block"
            aria-hidden
          />

          <p className="min-w-0 flex-1 self-center text-sm leading-relaxed text-inapi-muted">
            {marca.resumenColapsado}
          </p>

          <span className={cn("sm:hidden", chipEstadoClass(estado))}>
            {estado}
          </span>
        </div>
      </button>

      {expanded && (
        <div id={panelId} className="border-t border-[#E6E6E6] px-5 py-5">
          <ClasesList clases={marca.clases} buscadas={clasesBuscadas} />

          <p className="mt-5 text-sm leading-relaxed text-inapi-muted">
            {NIVEL_GUIA[marca.nivelParecido]}
          </p>

          <div className="mt-5">
            <Button
              type="button"
              onClick={onVerDetalle}
              className="h-11 rounded-sm bg-inapi-blue-dark px-6 text-sm font-bold hover:bg-inapi-blue-dark/90"
            >
              {copy.results.verDetalle}
            </Button>
          </div>
        </div>
      )}
    </article>
  );
}
