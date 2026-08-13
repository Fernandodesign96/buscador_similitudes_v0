"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { CircleHelp } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverTitle,
  PopoverTrigger,
} from "@/components/ui/popover";
import { LegalDisclaimerGate } from "@/components/legal/LegalDisclaimerGate";
import { MarkDetail } from "@/components/results/MarkDetail";
import { ExpandableResultCard } from "@/components/results/ExpandableResultCard";
import { ResultsEmptyState } from "@/components/results/ResultsEmptyState";
import { ResultsGuidance } from "@/components/results/ResultsGuidance";
import { ResultsPagination } from "@/components/results/ResultsPagination";
import { CoverageSearch } from "@/components/search/CoverageSearch";
import { ApiError, buscarMarcas } from "@/lib/api";
import { copy } from "@/lib/copy";
import type { NclCobertura } from "@/lib/ncl-coberturas";
import { toResultCardDisplay } from "@/lib/result-card-meta";
import type { BusquedaResponse, Resultado } from "@/lib/types";
import { cn } from "@/lib/utils";
import { SIMILITUD_MIN_RESULTADOS } from "@/lib/similarity";
import {
  searchControlClass,
  searchFieldLabelClass,
  searchPanelClass,
  searchSubmitClass,
} from "@/lib/search-layout";

function usePerPage() {
  const [perPage, setPerPage] = useState(20);

  useEffect(() => {
    const mq = window.matchMedia("(max-width: 640px)");
    const update = () => setPerPage(mq.matches ? 10 : 20);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);

  return perPage;
}

export function BuscadorApp() {
  const perPage = usePerPage();
  const [legalAccepted, setLegalAccepted] = useState(false);
  const [consulta, setConsulta] = useState("");
  const [coberturas, setCoberturas] = useState<NclCobertura[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<BusquedaResponse | null>(null);
  const [searched, setSearched] = useState(false);
  const [howOpen, setHowOpen] = useState(false);
  const [expandedIds, setExpandedIds] = useState<string[]>([]);
  const [detailResult, setDetailResult] = useState<Resultado | null>(null);
  const [coverageResultsSlot, setCoverageResultsSlot] =
    useState<HTMLDivElement | null>(null);

  const onCoverageResultsSlot = useCallback((node: HTMLDivElement | null) => {
    setCoverageResultsSlot(node);
  }, []);

  const marcaIngresada = consulta.trim().length > 0;

  const clasesEfectivas = useMemo(
    () =>
      [...new Set(coberturas.map((c) => c.clase))].sort((a, b) => a - b),
    [coberturas],
  );

  const puedeContinuar = marcaIngresada && coberturas.length > 0;

  const ejecutarBusqueda = useCallback(
    async (q: string, pageNum: number) => {
      const trimmed = q.trim();
      if (!trimmed) return;

      setLoading(true);
      setError(null);
      setSearched(true);
      setExpandedIds([]);
      setDetailResult(null);

      try {
        const response = await buscarMarcas({
          q: trimmed,
          clases: clasesEfectivas,
          top: 200,
          modo_clases: "filtrar",
          similitud_min: SIMILITUD_MIN_RESULTADOS,
          page: pageNum,
          per_page: perPage,
        });
        setData(response);
        if (response.resultados.length > 0) {
          setExpandedIds([`${response.resultados[0].nombre}-0`]);
        }
      } catch (err) {
        const message =
          err instanceof ApiError
            ? err.message
            : "Revisa tu conexión a internet.";
        setError(message);
        setData(null);
      } finally {
        setLoading(false);
      }
    },
    [clasesEfectivas, perPage],
  );

  const handleContinuar = () => {
    if (!puedeContinuar) return;
    void ejecutarBusqueda(consulta, 1);
  };

  const handlePageChange = (newPage: number) => {
    void ejecutarBusqueda(consulta, newPage);
  };

  const handleClearSearch = () => {
    setConsulta("");
    setCoberturas([]);
    setData(null);
    setError(null);
    setSearched(false);
    setExpandedIds([]);
    setDetailResult(null);
  };

  const handleConsultaChange = (value: string) => {
    setConsulta(value);
    if (!value.trim()) {
      setCoberturas([]);
      setData(null);
      setError(null);
      setSearched(false);
      setExpandedIds([]);
      setDetailResult(null);
    }
  };

  const toggleExpanded = (id: string) => {
    setExpandedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  };

  if (!legalAccepted) {
    return <LegalDisclaimerGate onAccept={() => setLegalAccepted(true)} />;
  }

  if (detailResult) {
    return (
      <MarkDetail
        resultado={detailResult}
        onBack={() => setDetailResult(null)}
      />
    );
  }

  return (
    <main className="mx-auto w-full max-w-[1140px] px-6 py-8 text-left">
      <header className="mb-8">
        <h1 className="font-[family-name:var(--font-roboto-slab)] text-[31px] font-medium text-[#111]">
          {copy.page.title}
        </h1>
        <p className="mt-3 max-w-2xl text-base leading-relaxed text-inapi-muted">
          {copy.page.subtitleSearch}
        </p>
      </header>

      <section className={searchPanelClass}>
        <div className="grid gap-8 lg:grid-cols-2 lg:items-start">
          <div className="min-w-0">
            <div className={searchFieldLabelClass}>
              <span className="flex items-center gap-1.5">
                <label htmlFor="searchInput" className="cursor-default">
                  {copy.search.label}
                </label>
                <Popover open={howOpen} onOpenChange={setHowOpen}>
                  <PopoverTrigger
                    type="button"
                    aria-label={copy.search.howItWorksAria}
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
                      {copy.search.howItWorksTitle}
                    </PopoverTitle>
                    <PopoverDescription className="text-sm leading-relaxed text-inapi-muted">
                      {copy.search.howItWorks}
                    </PopoverDescription>
                    <p className="text-sm leading-relaxed text-inapi-muted">
                      {copy.search.howItWorksExample}
                    </p>
                    <p className="text-sm leading-relaxed text-inapi-muted">
                      {copy.search.howItWorksNumeros}
                    </p>
                  </PopoverContent>
                </Popover>
              </span>
            </div>
            <Input
              id="searchInput"
              type="text"
              value={consulta}
              onChange={(e) => handleConsultaChange(e.target.value)}
              placeholder={copy.search.placeholder}
              className={cn(searchControlClass, "text-left")}
              autoComplete="off"
            />
          </div>

          <div
            className={cn(
              "min-w-0 transition-opacity",
              !marcaIngresada && "opacity-60",
            )}
          >
            <CoverageSearch
              selected={coberturas}
              onChange={setCoberturas}
              disabled={!marcaIngresada}
              compact
              resultsSlot={coverageResultsSlot}
            />
          </div>
        </div>

        <div
          ref={onCoverageResultsSlot}
          className="mt-6 w-full"
          aria-live="polite"
        />

        <div className="mt-8 flex flex-wrap gap-3">
          <Button
            type="button"
            disabled={!puedeContinuar || loading}
            onClick={handleContinuar}
            className={searchSubmitClass}
          >
            {loading ? copy.search.loading : copy.search.submit}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={handleClearSearch}
            className="h-11 min-h-11 rounded-sm border-[#E6E6E6] px-6 text-sm font-bold text-[#111]"
          >
            {copy.search.clear}
          </Button>
        </div>

        {!puedeContinuar && (
          <p className="mt-3 text-sm text-inapi-muted">
            {copy.coverage.needClass}
          </p>
        )}
      </section>

      {searched && (
        <section className="mt-8" aria-live="polite" aria-busy={loading}>
          {loading && (
            <div className="space-y-4">
              <Skeleton className="h-4 w-64" />
              <Skeleton className="h-40 w-full" />
            </div>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{copy.results.error(error)}</AlertDescription>
            </Alert>
          )}

          {!loading && !error && data && (
            <>
              {data.resultados.length === 0 ? (
                <ResultsEmptyState
                  message={
                    clasesEfectivas.length > 0
                      ? copy.results.emptyFiltered
                      : copy.results.empty
                  }
                  consulta={data.consulta}
                />
              ) : (
                <>
                  <ResultsGuidance
                    total={data.total}
                    consulta={data.consulta}
                  />
                  <p className="mb-4 text-sm text-inapi-muted">
                    {copy.results.mostrando(
                      data.resultados.length,
                      data.total,
                    )}
                  </p>
                  <ul className="list-none space-y-3">
                    {data.resultados.map((r, index) => {
                      const cardId = `${r.nombre}-${index}`;
                      const display = toResultCardDisplay(
                        r,
                        clasesEfectivas,
                      );
                      return (
                        <li key={cardId}>
                          <ExpandableResultCard
                            marca={display}
                            cardId={cardId}
                            clasesBuscadas={clasesEfectivas}
                            expanded={expandedIds.includes(cardId)}
                            onToggle={() => toggleExpanded(cardId)}
                            onVerDetalle={() => setDetailResult(r)}
                          />
                        </li>
                      );
                    })}
                  </ul>
                </>
              )}

              <ResultsPagination
                page={data.page}
                totalPages={data.total_pages}
                onPageChange={handlePageChange}
              />
            </>
          )}
        </section>
      )}

      <p className="mt-8 text-xs text-inapi-muted">
        {copy.chrome.footer.actualizacion}
      </p>
    </main>
  );
}
