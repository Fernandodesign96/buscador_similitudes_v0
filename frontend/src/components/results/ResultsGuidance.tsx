import { copy } from "@/lib/copy";

interface ResultsGuidanceProps {
  total: number;
  consulta: string;
}

export function ResultsGuidance({ total, consulta }: ResultsGuidanceProps) {
  return (
    <details className="group mb-6 overflow-hidden rounded-sm border border-inapi-blue/25 bg-[#f0f7fd] text-left">
      <summary className="cursor-pointer list-none px-5 py-4 text-base font-semibold text-[#111] [&::-webkit-details-marker]:hidden">
        <span className="flex items-center justify-between gap-3">
          {copy.results.summaryTitle}
          <span
            className="shrink-0 text-xs font-normal text-inapi-muted transition-transform group-open:rotate-180"
            aria-hidden
          >
            ▼
          </span>
        </span>
      </summary>
      <div className="border-t border-inapi-blue/20 px-5 py-4">
        <p className="text-sm leading-relaxed text-inapi-muted">
          {copy.results.coincidenciasIntro(total, consulta)}
        </p>
        <p className="mt-3 text-sm leading-relaxed text-inapi-muted">
          {copy.results.coincidenciasRegistro}
        </p>
        <p className="mt-3 text-sm leading-relaxed text-inapi-muted">
          {copy.results.coincidenciasNoDecide}
        </p>
        <p className="mt-4 text-base font-semibold text-[#111]">
          {copy.results.coincidenciasVerificaTitulo}
        </p>
        <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-inapi-muted">
          {copy.results.coincidenciasAspectos.map((aspecto) => (
            <li key={aspecto}>{aspecto}</li>
          ))}
        </ul>
      </div>
    </details>
  );
}
