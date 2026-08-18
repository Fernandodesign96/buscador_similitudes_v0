import { copy } from "@/lib/copy";

const NIVELES = [
  copy.help.nivelAlto,
  copy.help.nivelMedio,
  copy.help.nivelBajo,
] as const;

export function HelpAccordion() {
  return (
    <details className="group mb-8 w-full overflow-hidden rounded-sm border border-[#E6E6E6] bg-white text-left">
      <summary className="cursor-pointer list-none bg-[#F8F9FA] px-4 py-3.5 text-sm font-medium text-[#111] transition-colors hover:bg-[#F2F2F2] [&::-webkit-details-marker]:hidden">
        <span className="flex items-center justify-between gap-3">
          {copy.help.title}
          <span
            className="shrink-0 text-xs text-inapi-muted transition-transform group-open:rotate-180"
            aria-hidden
          >
            ▼
          </span>
        </span>
      </summary>
      <div className="w-full space-y-6 border-t border-[#E6E6E6] bg-white px-4 py-6 text-left sm:px-6">
        <section>
          <h2 className="mb-3 text-base font-semibold text-[#111]">
            {copy.help.criteriosTitulo}
          </h2>
          <ul className="space-y-4 text-sm leading-relaxed text-inapi-muted">
            <li>
              <strong className="block font-semibold text-[#111]">
                {copy.help.escritoTitulo}
              </strong>
              {copy.help.escritoTexto}
            </li>
            <li>
              <strong className="block font-semibold text-[#111]">
                {copy.help.sonidoTitulo}
              </strong>
              {copy.help.sonidoTexto}
            </li>
          </ul>
          <p className="mt-3 text-sm leading-relaxed text-inapi-muted">
            {copy.help.combinacionTexto}
          </p>
        </section>

        <section>
          <h2 className="mb-3 text-base font-semibold text-[#111]">
            {copy.help.nivelesTitulo}
          </h2>
          <ul className="space-y-3">
            {NIVELES.map((n) => (
              <li key={n.rango} className="text-sm">
                <span className="font-semibold text-[#111]">{n.rango}</span>
                <span className="text-inapi-muted"> — {n.accion}</span>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </details>
  );
}
