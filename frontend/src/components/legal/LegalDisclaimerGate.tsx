"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { copy } from "@/lib/copy";
import { cn } from "@/lib/utils";

interface LegalDisclaimerGateProps {
  onAccept: () => void;
}

export function LegalDisclaimerGate({ onAccept }: LegalDisclaimerGateProps) {
  const [checked, setChecked] = useState(false);
  const c = copy.landing;

  return (
    <main className="mx-auto w-full max-w-[1140px] px-6 py-8 text-left">
      <header className="mb-8">
        <h1 className="font-[family-name:var(--font-roboto-slab)] text-[31px] font-medium text-[#111]">
          {copy.page.title}
        </h1>
        <p className="mt-3 max-w-2xl text-base leading-relaxed text-inapi-muted">
          {copy.page.subtitleLanding}
        </p>
      </header>

      <section className="mb-8" aria-labelledby="que-es">
        <h2 id="que-es" className="text-lg font-semibold text-[#111]">
          {c.queEsTitulo}
        </h2>
        <p className="mt-3 max-w-3xl text-sm leading-relaxed text-inapi-muted">
          {c.queEsP1}
        </p>
      </section>

      <section className="mb-8" aria-labelledby="que-no">
        <h2 id="que-no" className="text-lg font-semibold text-[#111]">
          {c.queNoTitulo}
        </h2>
        <p className="mt-3 max-w-3xl text-sm leading-relaxed text-inapi-muted">
          {c.queEsP2}
        </p>
      </section>

      <section className="mb-8" aria-labelledby="ten-en-cuenta">
        <h2 id="ten-en-cuenta" className="text-lg font-semibold text-[#111]">
          {c.tenEnCuentaTitulo}
        </h2>
        <ul className="mt-3 max-w-3xl list-disc space-y-2 pl-5 text-sm leading-relaxed text-inapi-muted">
          {c.tenEnCuentaItems.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section
        className="mb-8 rounded-sm border border-[#E8ECEF] bg-white p-5 sm:p-6"
        aria-labelledby="aviso"
      >
        <h2 id="aviso" className="text-lg font-semibold text-[#111]">
          {c.legalTitle}
        </h2>
        <p className="mt-3 max-w-3xl text-sm leading-relaxed text-inapi-muted">
          {c.legalAcordado}
        </p>

        <label className="mt-6 flex cursor-pointer items-start gap-3 text-sm font-medium text-[#111]">
          <Checkbox
            checked={checked}
            onCheckedChange={(value) => setChecked(value === true)}
            className="mt-0.5 size-5 shrink-0 border-2 border-[#1565C0] bg-white data-checked:border-inapi-blue data-checked:bg-inapi-blue"
          />
          <span className="leading-relaxed">{c.acceptLabel}</span>
        </label>

        <div className="mt-6">
          <Button
            type="button"
            disabled={!checked}
            onClick={onAccept}
            className={cn(
              "h-11 rounded-sm px-8 text-sm font-bold",
              checked
                ? "bg-inapi-blue text-white hover:bg-inapi-blue-dark"
                : "bg-[#E0E0E0] text-[#757575]",
            )}
          >
            {c.continue}
          </Button>
        </div>
      </section>

      <p className="mt-8 text-xs text-inapi-muted">
        {copy.chrome.footer.actualizacion}
      </p>
    </main>
  );
}
