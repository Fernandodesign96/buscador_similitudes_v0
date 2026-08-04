"use client";

import { useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Popover,
  PopoverContent,
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
}

export function ClassPicker({ selected, onChange }: ClassPickerProps) {
  const [open, setOpen] = useState(false);

  const toggle = (id: number) => {
    if (selected.includes(id)) {
      onChange(selected.filter((c) => c !== id));
    } else {
      onChange([...selected, id].sort((a, b) => a - b));
    }
  };

  const remove = (id: number) => {
    onChange(selected.filter((c) => c !== id));
  };

  const label =
    selected.length > 0
      ? copy.search.classesCount(selected.length)
      : copy.search.classesAll;

  return (
    <div className="w-full">
      <label id="ncl-label" className={searchFieldLabelClass}>
        {copy.search.classesLabel}{" "}
        <span className="font-normal">({copy.search.classesOptional})</span>
      </label>
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
          className="max-h-[300px] w-[var(--radix-popover-trigger-width)] overflow-y-auto p-0"
          align="start"
        >
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
              <span className="inline-flex items-center gap-1.5 rounded-2xl border border-[#B3E5FC] bg-[#E3F2FD] px-3 py-1.5 text-xs text-inapi-blue">
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
