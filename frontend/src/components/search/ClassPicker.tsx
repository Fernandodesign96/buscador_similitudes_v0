"use client";

import { useState } from "react";
import { CircleHelp } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverTitle,
  PopoverTrigger,
} from "@/components/ui/popover";
import { copy } from "@/lib/copy";
import { NCL_CLASSES, NCL_CLASS_IDS } from "@/lib/ncl-classes";
import {
  searchControlClass,
  searchFieldLabelClass,
} from "@/lib/search-layout";
import { cn } from "@/lib/utils";

interface ClassPickerProps {
  selected: number[];
  onChange: (classes: number[]) => void;
  buscarTodas: boolean;
  onBuscarTodasChange: (value: boolean) => void;
}

export function ClassPicker({
  selected,
  onChange,
  buscarTodas,
  onBuscarTodasChange,
}: ClassPickerProps) {
  const [open, setOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);

  const toggle = (id: number) => {
    onBuscarTodasChange(false);
    if (selected.includes(id)) {
      onChange(selected.filter((c) => c !== id));
    } else {
      onChange([...selected, id].sort((a, b) => a - b));
    }
  };

  const remove = (id: number) => {
    onChange(selected.filter((c) => c !== id));
  };

  const clearAll = () => {
    onChange([]);
    onBuscarTodasChange(false);
  };

  const label = buscarTodas
    ? copy.search.classesAllSearch
    : selected.length > 0
      ? copy.search.classesCount(selected.length)
      : copy.search.classesAll;

  return (
    <div className="w-full">
      <div className={searchFieldLabelClass}>
        <span className="flex items-center gap-1.5">
          <label id="ncl-label" className="cursor-default">
            {copy.search.classesLabel}
          </label>
          <Popover open={helpOpen} onOpenChange={setHelpOpen}>
            <PopoverTrigger
              type="button"
              aria-label={copy.search.nclTooltipAria}
              className="flex size-5 shrink-0 items-center justify-center rounded-full text-[#999] transition-colors hover:text-inapi-blue focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inapi-blue/40"
            >
              <CircleHelp className="size-4" aria-hidden />
            </PopoverTrigger>
            <PopoverContent
              className="w-[min(20rem,calc(100vw-2rem))] gap-2 p-4"
              side="top"
              align="start"
            >
              <PopoverTitle className="text-sm font-bold text-[#111]">
                {copy.search.nclTooltipTitle}
              </PopoverTitle>
              <PopoverDescription className="text-sm leading-relaxed text-inapi-muted">
                {copy.search.nclTooltipText}
              </PopoverDescription>
              <p className="text-sm leading-relaxed text-inapi-muted">
                {copy.search.classesHint}
              </p>
            </PopoverContent>
          </Popover>
        </span>
      </div>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger
          type="button"
          aria-labelledby="ncl-label"
          className={cn(
            searchControlClass,
            "flex items-center justify-between text-left",
          )}
        >
          <span className="truncate">{label}</span>
          <span className="ml-2 shrink-0 text-xs" aria-hidden>
            ▼
          </span>
        </PopoverTrigger>
        <PopoverContent
          className="max-h-[360px] w-[var(--radix-popover-trigger-width)] overflow-y-auto p-0"
          align="start"
        >
          <div className="space-y-2 border-b border-[#E6E6E6] bg-[#F8F9FA] px-3 py-3">
            <label className="flex cursor-pointer items-center gap-3 text-sm">
              <Checkbox
                checked={buscarTodas}
                onCheckedChange={(value) => {
                  const next = value === true;
                  onBuscarTodasChange(next);
                  if (next) onChange([]);
                }}
              />
              <span>{copy.search.classesSearchAll}</span>
            </label>
            <button
              type="button"
              onClick={clearAll}
              className="text-sm font-medium text-inapi-blue hover:underline"
            >
              {copy.search.classesClearAll}
            </button>
          </div>
          <ul className="list-none">
            {NCL_CLASS_IDS.map((id) => (
              <li key={id}>
                <label className="flex cursor-pointer items-center gap-3 border-b border-[#f0f0f0] px-3 py-3 text-sm last:border-b-0 hover:bg-[#f9f9f9]">
                  <Checkbox
                    checked={selected.includes(id)}
                    onCheckedChange={() => toggle(id)}
                  />
                  <span>
                    <span className="font-bold">Clase {id}</span>
                    <span className="ml-2">{NCL_CLASSES[id]}</span>
                  </span>
                </label>
              </li>
            ))}
          </ul>
        </PopoverContent>
      </Popover>

      {selected.length > 0 && (
        <ul className="mt-3 flex list-none flex-wrap gap-2">
          {selected.map((id) => (
            <li key={id}>
              <span className="inline-flex items-center gap-1.5 rounded-sm border border-[#E6E6E6] bg-[#F8F9FA] px-3 py-1.5 text-xs text-inapi-text">
                Clase {id} · {NCL_CLASSES[id]}
                <button
                  type="button"
                  onClick={() => remove(id)}
                  className="ml-1 font-bold leading-none"
                  aria-label={`Quitar clase ${id}`}
                >
                  ×
                </button>
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
