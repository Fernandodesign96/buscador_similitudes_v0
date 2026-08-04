import { copy } from "@/lib/copy";

interface ResultsGuidanceProps {
  total: number;
}

export function ResultsGuidance({ total }: ResultsGuidanceProps) {
  return (
    <div className="mb-6 rounded-lg border border-inapi-blue/25 bg-[#f0f7fd] p-5 text-left text-sm leading-relaxed text-inapi-muted">
      <p>
        {copy.results.coincidenciasIntro(total)}{" "}
        {copy.results.coincidenciasRegistro}
      </p>
      <p className="mt-4 font-bold text-[#111]">
        {copy.results.coincidenciasVerificaTitulo}
      </p>
      <ul className="mt-2 list-inside list-disc space-y-1">
        {copy.results.coincidenciasAspectos.map((aspecto) => (
          <li key={aspecto}>{aspecto}</li>
        ))}
      </ul>
    </div>
  );
}
