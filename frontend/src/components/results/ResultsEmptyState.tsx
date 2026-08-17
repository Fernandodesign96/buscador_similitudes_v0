import { CheckCircle2 } from "lucide-react";
import { copy } from "@/lib/copy";

interface ResultsEmptyStateProps {
  consulta: string;
}

/** Aviso UI Kit Gobierno — sin coincidencias de parecido alto */
export function ResultsEmptyState({ consulta }: ResultsEmptyStateProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="overflow-hidden rounded-lg border border-inapi-border bg-white"
    >
      <div className="flex gap-3 p-5 sm:p-6">
        <CheckCircle2
          className="mt-0.5 size-5 shrink-0 text-[#2E7D32]"
          aria-hidden
        />
        <div className="min-w-0">
          <p className="text-base font-bold text-[#111]">
            {copy.results.emptyTitle}
          </p>
          <p className="mt-3 text-sm leading-relaxed text-inapi-muted">
            {copy.results.emptyHint(consulta)}
          </p>
          <p className="mt-3 text-sm font-bold leading-relaxed text-[#111]">
            {copy.results.emptyDisclaimer}
          </p>
        </div>
      </div>
    </div>
  );
}
