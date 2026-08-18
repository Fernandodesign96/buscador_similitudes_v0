import { copy } from "@/lib/copy";
import { NCL_CLASSES } from "@/lib/ncl-classes";
import { barWidth } from "@/lib/similarity";
import type { Resultado } from "@/lib/types";

interface ResultCardProps {
  resultado: Resultado;
  clasesBuscadas?: number[];
}

function SignalBar({ label, value }: { label: string; value: number }) {
  const width = barWidth(value);
  return (
    <div>
      <p className="mb-2 text-left text-base font-semibold text-[#111]">{label}</p>
      <div
        className="h-1.5 overflow-hidden rounded-sm bg-[#f2f2f2]"
        role="img"
        aria-label={label}
      >
        <div
          className="h-full bg-inapi-blue"
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  );
}

function ordenarClases(clases: number[], buscadas: number[]) {
  const setBuscadas = new Set(buscadas);
  const coinciden = clases.filter((n) => setBuscadas.has(n));
  const otras = clases.filter((n) => !setBuscadas.has(n));
  return { coinciden, otras, ordenadas: [...coinciden, ...otras] };
}

export function ResultCard({
  resultado,
  clasesBuscadas = [],
}: ResultCardProps) {
  const estado = resultado.estado?.trim() || copy.results.estadoChip;
  const { coinciden, ordenadas } = ordenarClases(
    resultado.clases,
    clasesBuscadas,
  );
  const coincidenSet = new Set(coinciden);

  return (
    <article className="mb-4 rounded-sm border border-[#E6E6E6] bg-white p-5 sm:p-6">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <h3 className="min-w-0 text-2xl font-semibold leading-tight text-[#111]">
          {resultado.nombre}
        </h3>
        <div className="flex max-w-full flex-wrap items-center justify-end gap-2">
          <span className="inline-block rounded-sm border border-[#E6E6E6] bg-[#F8F9FA] px-2.5 py-1 text-sm font-medium text-[#373737]">
            {estado}
          </span>
          {resultado.clase_relacionada && (
            <span className="inline-block rounded-sm bg-[#E3F2FD] px-2.5 py-1 text-sm font-medium text-inapi-blue">
              {copy.results.claseRelacionada}
            </span>
          )}
        </div>
      </div>

      <div className="mb-4">
        <h4 className="text-base font-semibold text-[#111]">
          {copy.results.coberturaTitulo}
        </h4>
        <p className="mt-1 text-sm leading-relaxed">
          {ordenadas.map((n, i) => {
            const title = NCL_CLASSES[n] ?? `Clase ${n}`;
            const coincide = coincidenSet.has(n);
            return (
              <span key={n}>
                {i > 0 ? ". " : null}
                <span
                  className={
                    coincide
                      ? "font-bold text-inapi-blue"
                      : "text-inapi-muted"
                  }
                >
                  Clase {n}: {title}
                </span>
              </span>
            );
          })}
        </p>
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
