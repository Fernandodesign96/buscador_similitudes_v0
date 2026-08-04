import { copy } from "@/lib/copy";

const NIVELES = [
  { color: "#D32F2F", ...copy.help.nivelAlto },
  { color: "#FF9800", ...copy.help.nivelMedio },
  { color: "#43A047", ...copy.help.nivelBajo },
] as const;

export function HelpAccordion() {
  return (
    <details className="group mb-6 w-full overflow-hidden rounded-lg border border-inapi-blue text-left">
      <summary className="cursor-pointer list-none bg-inapi-blue px-4 py-4 text-sm font-bold text-white [&::-webkit-details-marker]:hidden">
        <span className="flex items-center justify-between">
          {copy.help.title}
          <span className="group-open:hidden" aria-hidden>
            ▼
          </span>
          <span className="hidden group-open:inline" aria-hidden>
            ▲
          </span>
        </span>
      </summary>
      <div className="w-full space-y-6 border-t border-inapi-blue/20 bg-white px-6 py-6 text-left">
        <section>
          <h2 className="mb-2 text-base font-bold text-[#111]">
            {copy.help.porcentajeTitulo}
          </h2>
          <p className="text-sm leading-relaxed text-inapi-muted">
            {copy.help.porcentajeTexto}
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-base font-bold text-[#111]">
            {copy.help.nclTitulo}
          </h2>
          <p className="text-sm leading-relaxed text-inapi-muted">
            {copy.help.nclTexto}
          </p>
        </section>

        <section>
          <h2 className="mb-3 text-base font-bold text-[#111]">
            {copy.help.criteriosTitulo}
          </h2>
          <ul className="space-y-4 text-sm leading-relaxed text-inapi-muted">
            <li>
              <strong className="block font-bold text-inapi-blue">
                {copy.help.escritoTitulo}
              </strong>
              {copy.help.escritoTexto}
            </li>
            <li>
              <strong className="block font-bold text-inapi-blue">
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
          <h2 className="mb-3 text-base font-bold text-[#111]">
            {copy.help.nivelesTitulo}
          </h2>
          <ul className="space-y-3">
            {NIVELES.map((n) => (
              <li key={n.rango} className="flex flex-wrap items-start gap-2 text-sm">
                <span
                  className="mt-1 inline-block h-3 w-3 shrink-0 rounded-full"
                  style={{ backgroundColor: n.color }}
                  aria-hidden
                />
                <span className="font-bold text-[#111]">{n.rango}</span>
                <span className="text-inapi-muted">— {n.accion}</span>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </details>
  );
}
