import { CheckCircle2 } from "lucide-react";
import { copy } from "@/lib/copy";

interface ResultsEmptyStateProps {
  message: string;
  consulta: string;
}

/** Aviso UI Kit Gobierno — sin coincidencias de parecido alto */
export function ResultsEmptyState({ message, consulta }: ResultsEmptyStateProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="overflow-hidden rounded-lg border border-[#C8E6C9] border-l-4 border-l-[#2E7D32] bg-[#E8F5E9]"
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
          <p className="mt-3 text-sm leading-relaxed text-[#1B5E20]">
            {message}
          </p>
          <p className="mt-2 text-sm text-inapi-muted">
            {copy.results.emptyHint(consulta)}
          </p>
        </div>
      </div>
    </div>
  );
}
