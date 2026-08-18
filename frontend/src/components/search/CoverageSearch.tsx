"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { createPortal, flushSync } from "react-dom";
import { CircleHelp, Loader2, X } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import {
  Popover,
  PopoverContent,
  PopoverTitle,
  PopoverTrigger,
} from "@/components/ui/popover";
import { copy } from "@/lib/copy";
import { loadNclCatalog } from "@/lib/ncl-catalog";
import type { NclCobertura, TipoCobertura } from "@/lib/ncl-coberturas";
import { searchCoberturas } from "@/lib/ncl-fuse";
import { NCL_CLASSES } from "@/lib/ncl-classes";
import {
  searchControlClass,
  searchControlLockedClass,
  searchFieldLabelClass,
  searchSubmitClass,
  searchSubmitLockedClass,
} from "@/lib/search-layout";
import { cn } from "@/lib/utils";

const PREVIEW_LIMIT = 5;

interface CoverageSearchProps {
  selected: NclCobertura[];
  onChange: (items: NclCobertura[]) => void;
  disabled?: boolean;
  compact?: boolean;
  /** Contenedor donde renderizar resultados (columna izquierda). */
  resultsSlot?: HTMLElement | null;
  onCatalogLoadingChange?: (loading: boolean) => void;
  onSearchingChange?: (searching: boolean) => void;
}

function groupByClass(items: NclCobertura[]) {
  const map = new Map<number, NclCobertura[]>();
  const order: number[] = [];
  for (const item of items) {
    if (!map.has(item.clase)) {
      map.set(item.clase, []);
      order.push(item.clase);
    }
    map.get(item.clase)?.push(item);
  }
  return order.map((clase) => ({ clase, items: map.get(clase) ?? [] }));
}

function ClassGroup({
  clase,
  items,
  selectedIds,
  onToggle,
}: {
  clase: number;
  items: NclCobertura[];
  selectedIds: Set<number>;
  onToggle: (item: NclCobertura) => void;
}) {
  const [open, setOpen] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const visible = expanded ? items : items.slice(0, PREVIEW_LIMIT);
  const hiddenCount = items.length - PREVIEW_LIMIT;

  return (
    <details
      open={open}
      onToggle={(event) => setOpen(event.currentTarget.open)}
      className="group border-b border-inapi-border last:border-b-0"
    >
      <summary className="cursor-pointer list-none bg-[#F0F7FD] px-4 py-3 [&::-webkit-details-marker]:hidden">
        <span className="flex items-center justify-between gap-3">
          <span className="flex min-w-0 flex-wrap items-center gap-2">
            <span className="inline-flex h-8 w-[5.5rem] shrink-0 items-center justify-center rounded-sm bg-inapi-blue text-sm font-bold text-white tabular-nums">
              {copy.coverage.classBar(clase)}
            </span>
            <span className="text-sm font-semibold text-[#111]">
              {NCL_CLASSES[clase]}
            </span>
            <span className="text-xs font-normal text-inapi-muted">
              {copy.coverage.classGroupCount(items.length)}
            </span>
          </span>
          <span
            className="shrink-0 text-xs text-inapi-muted transition-transform group-open:rotate-180"
            aria-hidden
          >
            ▼
          </span>
        </span>
      </summary>
      <div className="bg-white px-4 py-3">
        <ul className="list-none">
          {visible.map((item) => (
            <li key={item.id}>
              <label className="flex cursor-pointer items-start gap-3 py-2 text-sm hover:bg-[#f9f9f9]">
                <Checkbox
                  className="mt-0.5"
                  checked={selectedIds.has(item.id)}
                  onCheckedChange={() => onToggle(item)}
                />
                <span>
                  <span className="text-[#111]">{item.cobertura}</span>
                  <span className="ml-2 text-xs text-inapi-muted">
                    {item.tipo}
                  </span>
                </span>
              </label>
            </li>
          ))}
        </ul>
        {hiddenCount > 0 && (
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="mt-2 text-sm font-medium text-inapi-blue hover:underline"
          >
            {expanded
              ? copy.coverage.showLess
              : copy.coverage.showAll(items.length)}
          </button>
        )}
      </div>
    </details>
  );
}

export function CoverageSearch({
  selected,
  onChange,
  disabled = false,
  compact = false,
  resultsSlot,
  onCatalogLoadingChange,
  onSearchingChange,
}: CoverageSearchProps) {
  const [helpOpen, setHelpOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");
  const [loadingCatalog, setLoadingCatalog] = useState(true);
  const [searching, setSearching] = useState(false);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [results, setResults] = useState<NclCobertura[] | null>(null);
  const [searched, setSearched] = useState(false);
  const [showProducto, setShowProducto] = useState(true);
  const [showServicio, setShowServicio] = useState(true);

  useEffect(() => {
    let cancelled = false;
    void loadNclCatalog()
      .then(() => {
        if (!cancelled) setLoadingCatalog(false);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setCatalogError(
            err instanceof Error
              ? err.message
              : "No se pudo cargar el catálogo de productos y servicios.",
          );
          setLoadingCatalog(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    onCatalogLoadingChange?.(loadingCatalog);
  }, [loadingCatalog, onCatalogLoadingChange]);

  useEffect(() => {
    onSearchingChange?.(searching);
  }, [searching, onSearchingChange]);

  const selectedIds = new Set(selected.map((s) => s.id));

  const toggle = (item: NclCobertura) => {
    if (selectedIds.has(item.id)) {
      onChange(selected.filter((s) => s.id !== item.id));
    } else {
      onChange([...selected, item]);
    }
  };

  const filtered = useMemo(() => {
    if (!results) return [];
    const allowed = new Set<TipoCobertura>();
    if (showProducto) allowed.add("Producto");
    if (showServicio) allowed.add("Servicio");
    return results.filter((item) => allowed.has(item.tipo));
  }, [results, showProducto, showServicio]);

  const groups = useMemo(() => groupByClass(filtered), [filtered]);

  const inFlight = useRef(false);

  const runCoverageSearch = async () => {
    const q = query.trim();
    if (q.length < 2 || loadingCatalog || catalogError || inFlight.current) {
      return;
    }
    inFlight.current = true;
    const inicio = Date.now();

    flushSync(() => {
      setSearching(true);
      setSearched(true);
      onSearchingChange?.(true);
    });

    try {
      await new Promise<void>((resolve) => {
        requestAnimationFrame(() => {
          requestAnimationFrame(() => resolve());
        });
      });
      const { fuse } = await loadNclCatalog();
      const encontrados = searchCoberturas(fuse, q);
      const resta = 500 - (Date.now() - inicio);
      if (resta > 0) {
        await new Promise((resolve) => setTimeout(resolve, resta));
      }
      setResults(encontrados);
    } finally {
      inFlight.current = false;
      setSearching(false);
      onSearchingChange?.(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    void runCoverageSearch();
  };

  const botonOcupado = loadingCatalog || searching;

  const inputDisabled =
    disabled || loadingCatalog || searching || Boolean(catalogError);

  const resultsPanel =
    results && results.length > 0 ? (
      <div className="overflow-hidden rounded-sm border border-inapi-border bg-white">
        <div className="flex flex-wrap items-center gap-4 border-b border-inapi-border px-4 py-3 text-sm">
          <span className="text-inapi-muted">{copy.coverage.showClassesFor}</span>
          <label className="flex cursor-pointer items-center gap-2">
            <Checkbox
              checked={showProducto}
              onCheckedChange={(value) => setShowProducto(value === true)}
            />
            {copy.coverage.filterProducto}
          </label>
          <label className="flex cursor-pointer items-center gap-2">
            <Checkbox
              checked={showServicio}
              onCheckedChange={(value) => setShowServicio(value === true)}
            />
            {copy.coverage.filterServicio}
          </label>
        </div>
        {groups.length === 0 ? (
          <p className="px-4 py-4 text-sm text-inapi-muted">
            {copy.coverage.empty}
          </p>
        ) : (
          groups.map((group) => (
            <ClassGroup
              key={group.clase}
              clase={group.clase}
              items={group.items}
              selectedIds={selectedIds}
              onToggle={toggle}
            />
          ))
        )}
      </div>
    ) : null;

  const selectedPanel =
    selected.length > 0 ? (
      <div className="mt-4">
        <p className="mb-2 text-sm font-semibold text-[#111]">
          {copy.coverage.selectedTitle(selected.length)}
        </p>
        <ul className="flex list-none flex-wrap gap-2">
          {selected.map((item) => (
            <li key={item.id}>
              <span className="inline-flex max-w-full items-center gap-1.5 rounded-sm border border-inapi-border bg-inapi-surface-muted px-3 py-1.5 text-xs text-inapi-text">
                <span className="truncate">
                  Clase {item.clase} · {item.cobertura}
                </span>
                <button
                  type="button"
                  onClick={() => toggle(item)}
                  className="ml-1 font-bold leading-none"
                  aria-label={`Quitar ${item.cobertura}`}
                >
                  ×
                </button>
              </span>
            </li>
          ))}
        </ul>
      </div>
    ) : null;

  const emptyMessage =
    searched && !searching && results && results.length === 0 ? (
      <p className="text-sm text-inapi-muted">{copy.coverage.empty}</p>
    ) : null;

  const resultsContent =
    resultsPanel || selectedPanel || emptyMessage ? (
      <div>
        {(emptyMessage || resultsPanel) && (
          <div
            className={cn(
              resultsSlot &&
                "max-h-[min(32rem,calc(100vh-14rem))] overflow-y-auto",
            )}
          >
            {emptyMessage}
            {resultsPanel && (
              <div className={resultsSlot ? "" : "mt-4"}>{resultsPanel}</div>
            )}
          </div>
        )}
        {selectedPanel}
      </div>
    ) : null;

  const resultsNode =
    resultsContent &&
    (resultsSlot ? createPortal(resultsContent, resultsSlot) : resultsContent);

  return (
    <section className={cn("text-left", compact ? "mb-0" : "mb-8")}>
      <form onSubmit={handleSearch}>
        <div className={searchFieldLabelClass}>
          <span className="flex items-center gap-1.5">
            <label
              htmlFor="coverageInput"
              className={cn("cursor-default", disabled && "text-inapi-muted")}
            >
              {copy.coverage.label}
            </label>
            <Popover open={helpOpen} onOpenChange={setHelpOpen}>
              <PopoverTrigger
                type="button"
                disabled={disabled}
                aria-label={copy.coverage.tooltipAria}
                className="flex size-5 shrink-0 items-center justify-center rounded-full text-[#999] transition-colors hover:text-inapi-blue focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inapi-blue/40 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <CircleHelp className="size-4" aria-hidden />
              </PopoverTrigger>
              <PopoverContent
                className="w-[min(24rem,calc(100vw-2rem))] gap-2 p-4"
                side="top"
                align="start"
              >
                <PopoverTitle className="text-sm font-bold text-[#111]">
                  {copy.coverage.tooltipTitle}
                </PopoverTitle>
                <div className="space-y-3 text-sm leading-relaxed text-inapi-muted">
                  <p>{copy.coverage.tooltipIntro}</p>
                  <p>{copy.coverage.tooltipNcl}</p>
                  <p className="font-semibold text-[#111]">
                    {copy.coverage.tooltipComoEscribirTitulo}
                  </p>
                  <ul className="list-disc space-y-2 pl-5">
                    <li>{copy.coverage.tooltipTildes}</li>
                    <li>{copy.coverage.tooltipEspecifico}</li>
                  </ul>
                </div>
              </PopoverContent>
            </Popover>
          </span>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start">
          <div className="relative min-w-0 flex-1">
            <Input
              id="coverageInput"
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={copy.coverage.placeholder}
              className={cn(
                searchControlClass,
                "text-left",
                query.length > 0 && !inputDisabled && "pr-10",
                inputDisabled && searchControlLockedClass,
              )}
              autoComplete="off"
              disabled={inputDisabled}
              readOnly={inputDisabled}
              aria-disabled={inputDisabled}
            />
            {query.length > 0 && !inputDisabled && (
              <button
                type="button"
                onClick={() => {
                  setQuery("");
                  setResults(null);
                  setSearched(false);
                  inputRef.current?.focus();
                }}
                className="absolute top-1/2 right-2 flex size-7 -translate-y-1/2 items-center justify-center rounded-full text-inapi-muted transition-colors hover:bg-inapi-surface-muted hover:text-[#111]"
                aria-label={copy.coverage.clearAria}
              >
                <X className="size-4" aria-hidden />
              </button>
            )}
          </div>
          <button
            type="submit"
            aria-busy={botonOcupado}
            disabled={
              Boolean(catalogError) ||
              (!botonOcupado && (disabled || query.trim().length < 2))
            }
            className={cn(
              searchSubmitClass,
              "inline-flex items-center justify-center gap-2 sm:w-auto",
              botonOcupado && searchSubmitLockedClass,
            )}
          >
            {botonOcupado ? (
              <Loader2 className="size-4 shrink-0 animate-spin" aria-hidden />
            ) : null}
            {loadingCatalog
              ? copy.coverage.loadingCatalog
              : searching
                ? copy.coverage.searching
                : copy.coverage.submit}
          </button>
        </div>
      </form>

      {!disabled && (
        <p className="mt-2 text-sm leading-relaxed text-inapi-muted">
          {copy.coverage.searchHint}
        </p>
      )}

      {disabled && (
        <p className="mt-2 text-sm text-inapi-muted">{copy.coverage.disabledHint}</p>
      )}

      {catalogError && (
        <p className="mt-3 text-sm text-[#C62828]">{catalogError}</p>
      )}

      {!resultsSlot &&
        searched &&
        !searching &&
        results &&
        results.length === 0 && (
          <p className="mt-4 text-sm text-inapi-muted">{copy.coverage.empty}</p>
        )}

      {resultsNode}
    </section>
  );
}
