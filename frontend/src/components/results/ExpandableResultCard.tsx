"use client";

import { Button } from "@/components/ui/button";
import { copy } from "@/lib/copy";
import {
  clasePuntoEstado,
  etiquetaEstadoCard,
} from "@/lib/estado-marca";
import type { ResultCardDisplay } from "@/lib/result-card-meta";
import { solicitudMasReciente } from "@/lib/result-card-meta";
import { cn } from "@/lib/utils";

export interface ExpandableResultCardProps {
  marca: ResultCardDisplay;
  onVerDetalle: () => void;
}

const COL_MARCA = "sm:w-[260px] sm:min-w-[260px] sm:max-w-[260px]";

export function ExpandableResultCard({
  marca,
  onVerDetalle,
}: ExpandableResultCardProps) {
  const estado = marca.estado?.trim();
  const etiquetaEstado = etiquetaEstadoCard(estado);
  const puntoEstado = clasePuntoEstado(estado);
  const anio = marca.anio_estado;
  const solicitud = solicitudMasReciente(marca.solicitudes);

  return (
    <article className="overflow-hidden rounded-lg border border-inapi-border bg-white px-5 py-4 transition-[border-color,box-shadow,background-color] duration-150 hover:border-inapi-blue hover:bg-[#f7fafc] hover:shadow-sm">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:gap-0">
        <div className={cn("flex min-w-0 shrink-0 flex-col gap-1.5", COL_MARCA)}>
          <p className="text-2xl font-bold leading-tight tracking-wide text-[#111]">
            {marca.nombre}
          </p>
          <p className="flex items-center gap-2 text-base font-semibold leading-snug text-inapi-text">
            {puntoEstado ? (
              <span
                className={cn("size-2.5 shrink-0 rounded-full", puntoEstado)}
                aria-hidden
              />
            ) : null}
            {etiquetaEstado}
          </p>
          {anio && anio > 0 ? (
            <p className="text-sm text-inapi-muted">{anio}</p>
          ) : null}
          {marca.razonSocial ? (
            <p className="text-sm font-medium leading-snug text-inapi-text">
              {marca.razonSocial}
            </p>
          ) : null}
          {solicitud ? (
            <p className="text-sm text-inapi-muted">
              {copy.detail.solicitud}: {solicitud}
            </p>
          ) : null}
          {marca.clasesRegistradas.length > 0 ? (
            <p className="text-sm text-inapi-muted">
              {copy.results.clasesRegistradas(marca.clasesRegistradas)}
            </p>
          ) : null}
        </div>

        <div
          className="hidden w-px shrink-0 self-stretch bg-inapi-border sm:mx-4 sm:block"
          aria-hidden
        />

        <ul className="min-w-0 flex-1 list-disc space-y-1 pl-5 text-sm leading-relaxed text-inapi-muted">
          {marca.resumenItems.map((item) => (
            <li key={item}>{item}</li>
          ))}
          {marca.clasesIdenticas.length > 0 ? (
            <li className="font-bold text-[#111]">
              {copy.results.bulletClaseIdentica(marca.clasesIdenticas)}
            </li>
          ) : null}
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
