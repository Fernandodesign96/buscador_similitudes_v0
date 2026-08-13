"use client";

import { copy } from "@/lib/copy";
import { NCL_CLASSES } from "@/lib/ncl-classes";
import { barWidth } from "@/lib/similarity";
import type { Resultado } from "@/lib/types";

interface MarkDetailProps {
  resultado: Resultado;
  onBack: () => void;
}

function Unavailable({ label, tip }: { label: string; tip?: string }) {
  return (
    <div>
      <dt className="text-xs font-medium text-inapi-muted">
        {label}
        {tip ? <span className="sr-only">. {tip}</span> : null}
      </dt>
      <dd className="mt-1 text-sm text-[#111]">
        {copy.detail.unavailable}
        <span className="mt-1 block text-xs font-normal text-inapi-muted">
          {copy.detail.unavailableHint}
        </span>
      </dd>
    </div>
  );
}

function SignalBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <p className="mb-2 text-xs font-medium text-[#111]">{label}</p>
      <div className="h-1.5 overflow-hidden rounded-sm bg-[#f2f2f2]" role="img" aria-label={label}>
        <div className="h-full bg-inapi-blue" style={{ width: `${barWidth(value)}%` }} />
      </div>
    </div>
  );
}

export function MarkDetail({ resultado, onBack }: MarkDetailProps) {
  const estado = resultado.estado?.trim();
  const solicitudes = resultado.solicitudes?.filter(Boolean) ?? [];
  const tipo = resultado.tipo?.trim();
  const registro = resultado.nro_registro?.trim();
  const titular = resultado.titular?.trim();
  const fechas = resultado.fechas;

  return (
    <main className="mx-auto w-full max-w-[1140px] px-6 py-8 text-left">
      <nav aria-label="Migas de pan" className="mb-6 text-sm text-inapi-muted">
        <ol className="flex flex-wrap items-center gap-2">
          <li>
            <button
              type="button"
              onClick={onBack}
              className="text-inapi-blue hover:underline"
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

      <div className="grid gap-8 lg:grid-cols-[220px_minmax(0,1fr)]">
        <aside aria-label={copy.detail.statusTitulo}>
          <div className="rounded-sm border border-[#E6E6E6] bg-[#F8F9FA] px-4 py-3 text-sm font-semibold text-[#111]">
            {estado || copy.results.estadoChip}
          </div>
          <p className="mt-3 text-xs leading-relaxed text-inapi-muted">
            {copy.detail.unavailableHint}
          </p>
        </aside>

        <div>
          <header className="mb-8 flex flex-wrap items-start justify-between gap-6">
            <div>
              <p className="text-xs font-medium tracking-wide text-inapi-muted uppercase">
                {copy.detail.eyebrow}
              </p>
              <h1 className="mt-2 font-[family-name:var(--font-roboto-slab)] text-[31px] font-medium text-[#111]">
                {resultado.nombre}
              </h1>
              <p className="mt-2 text-sm text-inapi-muted">
                {tipo || copy.detail.kindFallback}
              </p>
            </div>
            <div className="w-full max-w-xs space-y-3">
              <SignalBar
                label={copy.results.ortografica}
                value={resultado.desglose.ortografica}
              />
              <SignalBar
                label={copy.results.fonetica}
                value={resultado.desglose.fonetica}
              />
              <p className="text-xs text-inapi-muted">{copy.detail.scoreHint}</p>
            </div>
          </header>

          <div className="grid gap-4 md:grid-cols-2">
            <section className="rounded-sm border border-[#E6E6E6] bg-white p-5">
              <h2 className="mb-4 text-base font-semibold text-[#111]">
                {copy.detail.idsTitulo}
              </h2>
              <dl className="space-y-4">
                {solicitudes.length > 0 ? (
                  <div>
                    <dt className="text-xs font-medium text-inapi-muted">
                      {copy.detail.solicitud}
                    </dt>
                    <dd className="mt-1 text-sm text-[#111]">
                      {solicitudes.join(", ")}
                    </dd>
                  </div>
                ) : (
                  <Unavailable
                    label={copy.detail.solicitud}
                    tip={copy.detail.solicitudTip}
                  />
                )}
                {registro ? (
                  <div>
                    <dt className="text-xs font-medium text-inapi-muted">
                      {copy.detail.registro}
                    </dt>
                    <dd className="mt-1 text-sm text-[#111]">{registro}</dd>
                  </div>
                ) : (
                  <Unavailable
                    label={copy.detail.registro}
                    tip={copy.detail.registroTip}
                  />
                )}
                <div>
                  <dt className="text-xs font-medium text-inapi-muted">
                    {copy.detail.estado}
                  </dt>
                  <dd className="mt-1 text-sm text-[#111]">
                    {estado || copy.results.estadoChip}
                  </dd>
                </div>
                {tipo ? (
                  <div>
                    <dt className="text-xs font-medium text-inapi-muted">
                      {copy.detail.tipo}
                    </dt>
                    <dd className="mt-1 text-sm text-[#111]">{tipo}</dd>
                  </div>
                ) : (
                  <Unavailable label={copy.detail.tipo} tip={copy.detail.tipoTip} />
                )}
              </dl>
            </section>

            <section className="rounded-sm border border-[#E6E6E6] bg-white p-5">
              <h2 className="mb-4 text-base font-semibold text-[#111]">
                {copy.detail.visualTitulo}
              </h2>
              <div className="flex min-h-28 items-center justify-center rounded-sm bg-[#F8F9FA] px-4 py-8 text-center font-[family-name:var(--font-roboto-slab)] text-2xl font-medium text-[#111]">
                {resultado.nombre}
              </div>
            </section>
          </div>

          <section className="mt-4 rounded-sm border border-[#E6E6E6] bg-white p-5">
            <h2 className="mb-4 text-base font-semibold text-[#111]">
              {copy.detail.datesTitulo}
            </h2>
            <dl className="grid gap-4 sm:grid-cols-2">
              {fechas?.presentacion ? (
                <div>
                  <dt className="text-xs font-medium text-inapi-muted">
                    {copy.detail.presentacion}
                  </dt>
                  <dd className="mt-1 text-sm text-[#111]">{fechas.presentacion}</dd>
                </div>
              ) : (
                <Unavailable label={copy.detail.presentacion} />
              )}
              {fechas?.publicacion ? (
                <div>
                  <dt className="text-xs font-medium text-inapi-muted">
                    {copy.detail.publicacion}
                  </dt>
                  <dd className="mt-1 text-sm text-[#111]">{fechas.publicacion}</dd>
                </div>
              ) : (
                <Unavailable label={copy.detail.publicacion} />
              )}
              {fechas?.registro ? (
                <div>
                  <dt className="text-xs font-medium text-inapi-muted">
                    {copy.detail.fechaRegistro}
                  </dt>
                  <dd className="mt-1 text-sm text-[#111]">{fechas.registro}</dd>
                </div>
              ) : (
                <Unavailable label={copy.detail.fechaRegistro} />
              )}
              {fechas?.vigencia ? (
                <div>
                  <dt className="text-xs font-medium text-inapi-muted">
                    {copy.detail.vigencia}
                  </dt>
                  <dd className="mt-1 text-sm text-[#111]">{fechas.vigencia}</dd>
                </div>
              ) : (
                <Unavailable label={copy.detail.vigencia} />
              )}
            </dl>
          </section>

          <section className="mt-4 rounded-sm border border-[#E6E6E6] bg-white p-5">
            <h2 className="mb-4 text-base font-semibold text-[#111]">
              {copy.detail.coverageTitulo}
            </h2>
            <ul className="space-y-4">
              {resultado.clases.map((n) => (
                <li key={n}>
                  <h3 className="text-sm font-semibold text-[#111]">
                    Clase {n} — {NCL_CLASSES[n] ?? `Clase ${n}`}
                  </h3>
                  <p className="mt-1 text-sm text-inapi-muted">
                    {NCL_CLASSES[n]
                      ? `Cubre productos o servicios de esta clase: ${NCL_CLASSES[n]}.`
                      : copy.detail.unavailable}
                  </p>
                </li>
              ))}
            </ul>
          </section>

          <section className="mt-4 rounded-sm border border-[#E6E6E6] bg-white p-5">
            <h2 className="mb-4 text-base font-semibold text-[#111]">
              {copy.detail.ownerTitulo}
            </h2>
            {titular ? (
              <>
                <p className="text-sm font-semibold text-[#111]">{titular}</p>
                {resultado.titular_nota ? (
                  <p className="mt-2 text-sm text-inapi-muted">
                    {resultado.titular_nota}
                  </p>
                ) : null}
              </>
            ) : (
              <p className="text-sm text-inapi-muted">
                {copy.detail.unavailable}. {copy.detail.unavailableHint}
              </p>
            )}
          </section>

          <div className="mt-8 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={onBack}
              className="h-11 rounded-sm border border-[#E6E6E6] bg-white px-5 text-sm font-bold text-[#111] hover:bg-[#F8F9FA]"
            >
              {copy.detail.back}
            </button>
          </div>
        </div>
      </div>

      <p className="mt-8 text-xs text-inapi-muted">
        {copy.chrome.footer.actualizacion}
      </p>
    </main>
  );
}
