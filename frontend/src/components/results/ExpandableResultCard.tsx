"use client";

import { Button } from "@/components/ui/button";
import { copy } from "@/lib/copy";
import type { ResultCardDisplay } from "@/lib/result-card-meta";
import { cn } from "@/lib/utils";

export interface ExpandableResultCardProps {
  marca: ResultCardDisplay;
  onVerDetalle: () => void;
}

const COL_MARCA = "sm:w-[220px] sm:min-w-[220px] sm:max-w-[220px]";

export function ExpandableResultCard({
  marca,
  onVerDetalle,
}: ExpandableResultCardProps) {
  const estado = marca.estado?.trim() || copy.results.estadoChip;

  return (
    <article className="overflow-hidden rounded-lg border border-inapi-border bg-white px-5 py-4">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:gap-0">
        <div className={cn("flex min-w-0 shrink-0 flex-col gap-3", COL_MARCA)}>
          <p className="text-lg font-bold tracking-wide text-[#111]">
            {marca.nombre}
          </p>
          <p className="text-sm text-inapi-muted">{estado}</p>
          <p className="text-base font-semibold leading-snug text-[#373737]">
            {marca.razonSocial}
          </p>
        </div>

        <div
          className="hidden w-px shrink-0 self-stretch bg-inapi-border sm:mx-4 sm:block"
          aria-hidden
        />

        <ul className="min-w-0 flex-1 list-disc space-y-1 pl-5 text-sm leading-relaxed text-inapi-muted">
          {marca.resumenItems.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>

        <div className="flex shrink-0 flex-col items-stretch sm:ml-4 sm:w-[11.75rem]">
          <Button
            type="button"
            onClick={onVerDetalle}
            className="h-11 rounded-sm bg-inapi-blue-dark px-3 text-sm font-bold hover:bg-inapi-blue-dark/90"
          >
            {copy.results.verDetalle}
          </Button>
        </div>
      </div>
    </article>
  );
}
