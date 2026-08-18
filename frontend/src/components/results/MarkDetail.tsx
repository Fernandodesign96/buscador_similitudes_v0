"use client";

import { copy } from "@/lib/copy";
import { clasePuntoEstado } from "@/lib/estado-marca";
import { NCL_CLASSES } from "@/lib/ncl-classes";
import {
  solicitudesMasRecientesPrimero,
  textosParecido,
} from "@/lib/result-card-meta";
import type { Resultado } from "@/lib/types";
import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

interface MarkDetailProps {
  resultado: Resultado;
  clasesBuscadas?: number[];
  onBack: () => void;
}

function Field({
  label,
  tip,
  children,
}: {
  label: string;
  tip?: string;
  children: ReactNode;
}) {
  return (
    <div>
      <dt className="text-[11px] font-semibold tracking-wide text-inapi-muted uppercase">
        {label}
        {tip ? <span className="sr-only">. {tip}</span> : null}
      </dt>
      <dd className="mt-1.5 text-base font-semibold leading-snug text-[#111]">
        {children}
      </dd>
    </div>
  );
}

export function MarkDetail({
  resultado,
  clasesBuscadas = [],
  onBack,
}: MarkDetailProps) {
  const estado = resultado.estado?.trim();
  const puntoEstado = clasePuntoEstado(estado);
  const solicitudes = solicitudesMasRecientesPrimero(
    resultado.solicitudes?.filter(Boolean) ?? [],
  );
  const tipo = resultado.tipo?.trim();
  const registro = resultado.nro_registro?.trim();
  const titular = resultado.titular?.trim();
  const fechas = resultado.fechas;
  const anioEstado = resultado.anio_estado;
  const markCode = resultado.mark_code;
  const parecido = textosParecido(resultado, clasesBuscadas);
  const clasesIdenticas = new Set(clasesBuscadas);
  const clasesOrdenadas = [...resultado.clases].sort((a, b) => {
    const ia = clasesIdenticas.has(a) ? 0 : 1;
    const ib = clasesIdenticas.has(b) ? 0 : 1;
    if (ia !== ib) return ia - ib;
    return a - b;
  });

  return (
    <main className="mx-auto w-full max-w-[1140px] px-6 py-8 text-left">
      <nav aria-label="Migas de pan" className="mb-8 text-sm text-inapi-muted">
        <ol className="flex flex-wrap items-center gap-2">
          <li>
            <button
              type="button"
              onClick={onBack}
              className="font-medium text-inapi-blue hover:underline"
            >
              {copy.detail.backCrumb}
            </button>
          </li>
          <li aria-hidden>›</li>
          <li className="font-semibold text-[#111]" aria-current="page">
            {resultado.nombre}
          </li>
        </ol>
      </nav>

      <header className="mb-8">
        <h1 className="font-[family-name:var(--font-roboto-slab)] text-5xl font-bold leading-tight text-[#111]">
          {resultado.nombre}
        </h1>
      </header>

      <section className="rounded-sm border border-inapi-border bg-white p-6">
        <h2 className="mb-6 font-[family-name:var(--font-roboto-slab)] text-lg font-semibold text-[#111]">
          {copy.detail.idsTitulo}
        </h2>
        <dl className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <Field label={copy.results.ortografica}>{parecido.escribir}</Field>
          <Field label={copy.results.fonetica}>{parecido.pronunciar}</Field>
          {parecido.clase ? (
            <Field label={copy.results.claseRelacionada}>{parecido.clase}</Field>
          ) : null}
          <Field label={copy.detail.estado}>
            <span className="inline-flex items-center gap-2">
              {puntoEstado ? (
                <span
                  className={cn("size-2.5 shrink-0 rounded-full", puntoEstado)}
                  aria-hidden
                />
              ) : null}
              {estado || copy.results.estadoChip}
            </span>
          </Field>
          {markCode != null ? (
            <Field label={copy.detail.markCode} tip={copy.detail.markCodeTip}>
              {markCode}
            </Field>
          ) : null}
          {solicitudes.length > 0 ? (
            <div className="sm:col-span-2 lg:col-span-3">
              <Field
                label={copy.detail.solicitud}
                tip={copy.detail.solicitudTip}
              >
                <ul className="flex flex-wrap gap-2">
                  {solicitudes.map((nro, i) => (
                    <li
                      key={nro}
                      className={
                        i === 0
                          ? "rounded-sm bg-inapi-navy px-2.5 py-1 text-sm font-semibold text-white"
                          : "rounded-sm bg-inapi-surface-muted px-2.5 py-1 text-sm font-medium text-inapi-text"
                      }
                    >
                      {nro}
                    </li>
                  ))}
                </ul>
              </Field>
            </div>
          ) : null}
          {registro ? (
            <Field label={copy.detail.registro} tip={copy.detail.registroTip}>
              {registro}
            </Field>
          ) : null}
          {anioEstado && anioEstado > 0 ? (
            <Field label={copy.detail.anioEstado} tip={copy.detail.anioEstadoTip}>
              {anioEstado}
            </Field>
          ) : null}
          {tipo ? (
            <Field label={copy.detail.tipo} tip={copy.detail.tipoTip}>
              {tipo}
            </Field>
          ) : null}
        </dl>
      </section>

      {fechas?.presentacion ||
      fechas?.publicacion ||
      fechas?.registro ||
      fechas?.vigencia ? (
        <section className="mt-5 rounded-sm border border-inapi-border bg-white p-6">
          <h2 className="mb-6 font-[family-name:var(--font-roboto-slab)] text-lg font-semibold text-[#111]">
            {copy.detail.datesTitulo}
          </h2>
          <dl className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {fechas.presentacion ? (
              <Field label={copy.detail.presentacion}>{fechas.presentacion}</Field>
            ) : null}
            {fechas.publicacion ? (
              <Field label={copy.detail.publicacion}>{fechas.publicacion}</Field>
            ) : null}
            {fechas.registro ? (
              <Field label={copy.detail.fechaRegistro}>{fechas.registro}</Field>
            ) : null}
            {fechas.vigencia ? (
              <Field label={copy.detail.vigencia}>{fechas.vigencia}</Field>
            ) : null}
          </dl>
        </section>
      ) : null}

      <section className="mt-5 rounded-sm border border-inapi-border bg-white p-6">
        <h2 className="mb-6 font-[family-name:var(--font-roboto-slab)] text-lg font-semibold text-[#111]">
          {copy.detail.coverageTitulo}
        </h2>
        <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {clasesOrdenadas.map((n) => {
            const identica = clasesIdenticas.has(n);
            return (
              <li
                key={n}
                className={cn(
                  "flex gap-3 px-4 py-3",
                  identica
                    ? "border-2 border-inapi-blue bg-white"
                    : "border border-inapi-border bg-inapi-surface-muted",
                )}
              >
                <span
                  className={cn(
                    "shrink-0 text-sm font-bold",
                    identica ? "text-inapi-blue-dark" : "text-inapi-blue",
                  )}
                >
                  {n}
                </span>
                <div className="min-w-0">
                  <h3 className="text-sm font-semibold text-[#111]">
                    {copy.detail.clase(n)}
                  </h3>
                  <p className="mt-1 text-sm leading-snug text-inapi-muted">
                    {NCL_CLASSES[n] ?? copy.detail.unavailable}
                  </p>
                  {identica ? (
                    <p className="mt-2 text-sm font-semibold text-inapi-blue">
                      {copy.detail.claseIdentica}
                    </p>
                  ) : null}
                </div>
              </li>
            );
          })}
        </ul>
      </section>

      {titular ? (
        <section className="mt-5 rounded-sm border border-inapi-border bg-white p-6">
          <h2 className="mb-4 font-[family-name:var(--font-roboto-slab)] text-lg font-semibold text-[#111]">
            {copy.detail.ownerTitulo}
          </h2>
          <p className="text-lg font-semibold text-[#111]">{titular}</p>
          {resultado.titular_nota ? (
            <p className="mt-2 text-sm text-inapi-muted">{resultado.titular_nota}</p>
          ) : null}
        </section>
      ) : null}

      <div className="mt-8 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={onBack}
          className="inline-flex h-11 items-center justify-center rounded-sm border border-inapi-border bg-white px-5 text-sm font-medium text-[#111] hover:bg-inapi-surface-muted"
        >
          {copy.detail.back}
        </button>
      </div>

      <p className="mt-8 text-xs text-inapi-muted">
        {copy.chrome.footer.actualizacion}
      </p>
    </main>
  );
}
