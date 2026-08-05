"use client";

import { useState } from "react";
import { Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { copy } from "@/lib/copy";
import { cn } from "@/lib/utils";

interface LegalDisclaimerGateProps {
  onAccept: () => void;
}

export function LegalDisclaimerGate({ onAccept }: LegalDisclaimerGateProps) {
  const [checked, setChecked] = useState(false);

  return (
    <section
      className="mx-auto w-full max-w-[1140px] px-6 py-8 text-left"
      aria-labelledby="buscador-intro-title"
    >
      <div className="mb-8">
        <h2
          id="buscador-intro-title"
          className="text-base font-bold text-[#111]"
        >
          {copy.disclaimerLegal.introTitle}
        </h2>
        <p className="mt-3 text-sm leading-relaxed text-inapi-muted">
          {copy.disclaimerLegal.introText}
        </p>
      </div>

      {/* UI Kit Gobierno: aviso informativo con borde lateral e icono */}
      <div className="overflow-hidden rounded-lg border border-[#B3E5FC] border-l-4 border-l-inapi-blue bg-[#E3F2FD]">
        <div className="flex gap-3 p-5 sm:p-6">
          <Info
            className="mt-0.5 size-5 shrink-0 text-inapi-blue"
            aria-hidden
          />
          <div className="min-w-0">
            <h2
              id="disclaimer-legal-title"
              className="text-base font-bold text-[#111]"
            >
              {copy.disclaimerLegal.title}
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-inapi-muted">
              {copy.disclaimerLegal.text}
            </p>
          </div>
        </div>
      </div>

      <div className="mt-6 flex flex-col gap-6">
        <label className="flex cursor-pointer items-start gap-3 text-sm text-[#111]">
          <Checkbox
            checked={checked}
            onCheckedChange={(value) => setChecked(value === true)}
            className="mt-0.5"
          />
          <span className="leading-relaxed">
            {copy.disclaimerLegal.acceptLabel}
          </span>
        </label>

        <div>
          <Button
            type="button"
            disabled={!checked}
            onClick={onAccept}
            className={cn(
              "h-11 rounded-none px-8 font-bold",
              checked
                ? "bg-inapi-navy hover:bg-inapi-navy/90"
                : "bg-[#ccc] text-[#666]",
            )}
          >
            {copy.disclaimerLegal.continue}
          </Button>
        </div>
      </div>
    </section>
  );
}
