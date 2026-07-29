import type { Resultado } from "@/lib/types";
import { copy } from "@/lib/copy";
import { badgeColors, similarityColor } from "@/lib/similarity";

interface ResultCardProps {
  resultado: Resultado;
}

function SignalBar({ label, value }: { label: string; value: number }) {
  const color = similarityColor(value);
  return (
    <div>
      <p className="mb-2 text-left text-xs font-bold text-inapi-muted">
        {label}
      </p>
      <div className="h-1.5 overflow-hidden rounded-sm bg-[#f2f2f2]">
        <div
          className="h-full transition-all"
          style={{ width: `${value}%`, backgroundColor: color }}
        />
      </div>
      <p className="mt-1 text-center text-xs font-bold" style={{ color }}>
        {value}%
      </p>
    </div>
  );
}

export function ResultCard({ resultado }: ResultCardProps) {
  const pctColor = similarityColor(resultado.similitud);
  const badge = badgeColors(resultado.similitud);

  return (
    <article
      className="mb-4 rounded border border-[#ccc] border-l-4 bg-white p-6"
      style={{ borderLeftColor: pctColor }}
    >
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-[#111]">{resultado.nombre}</h3>
          <p className="mt-2 text-xs text-inapi-muted">
            {copy.results.clases}: {resultado.clases.join(", ")}
            {resultado.clase_relacionada && (
              <span
                className="ml-2 inline-block rounded-xl px-2 py-0.5 text-[11px] font-bold"
                style={{ backgroundColor: badge.bg, color: badge.text }}
              >
                {copy.results.claseRelacionada}
              </span>
            )}
          </p>
        </div>
        <div className="text-right">
          <p className="text-[28px] font-bold leading-none" style={{ color: pctColor }}>
            <span className="sr-only">{copy.results.similitudLabel}: </span>
            {resultado.similitud}%
          </p>
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <SignalBar
          label={copy.results.ortografica}
          value={resultado.desglose.ortografica}
        />
        <SignalBar
          label={copy.results.fonetica}
          value={resultado.desglose.fonetica}
        />
      </div>
    </article>
  );
}
