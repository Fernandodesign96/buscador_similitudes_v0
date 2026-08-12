"use client";

import { useCallback, useEffect, useState } from "react";
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
import { ResultCard } from "@/components/results/ResultCard";
import { ResultsEmptyState } from "@/components/results/ResultsEmptyState";
import { ResultsGuidance } from "@/components/results/ResultsGuidance";
import { ResultsPagination } from "@/components/results/ResultsPagination";
import { ClassPicker } from "@/components/search/ClassPicker";
import { ApiError, buscarMarcas } from "@/lib/api";
import { copy } from "@/lib/copy";
import type { BusquedaResponse } from "@/lib/types";
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
  const [clases, setClases] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<BusquedaResponse | null>(null);
  const [searched, setSearched] = useState(false);
  const [howOpen, setHowOpen] = useState(false);

  const ejecutarBusqueda = useCallback(
    async (q: string, pageNum: number) => {
      const trimmed = q.trim();
      if (!trimmed) return;

      setLoading(true);
      setError(null);
      setSearched(true);

      try {
        const response = await buscarMarcas({
          q: trimmed,
          clases: clases.length > 0 ? clases : undefined,
          top: 200,
          modo_clases: "filtrar",
          similitud_min: SIMILITUD_MIN_RESULTADOS,
          page: pageNum,
          per_page: perPage,
        });
        setData(response);
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
    [clases, perPage],
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    void ejecutarBusqueda(consulta, 1);
  };

  const handlePageChange = (newPage: number) => {
    void ejecutarBusqueda(consulta, newPage);
  };

  const handleClearSearch = () => {
    setConsulta("");
    setClases([]);
    setData(null);
    setError(null);
    setSearched(false);
  };

  if (!legalAccepted) {
    return <LegalDisclaimerGate onAccept={() => setLegalAccepted(true)} />;
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
        <form onSubmit={handleSubmit} className="w-full">
          <div className="grid w-full gap-4 lg:grid-cols-[minmax(0,1fr)_280px] lg:items-start">
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
                    </PopoverContent>
                  </Popover>
                </span>
              </div>
              <Input
                id="searchInput"
                type="text"
                value={consulta}
                onChange={(e) => setConsulta(e.target.value)}
                placeholder={copy.search.placeholder}
                className={cn(searchControlClass, "text-left")}
                autoComplete="off"
              />
            </div>

            <ClassPicker selected={clases} onChange={setClases} />
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <Button
              type="submit"
              disabled={!consulta.trim() || loading}
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
        </form>
      </section>

      {searched && (
        <>
          <section aria-live="polite" aria-busy={loading}>
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
                      clases.length > 0
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
                    <ul className="list-none">
                      {data.resultados.map((r, index) => (
                        <li key={`${r.nombre}-${r.clases.join("-")}-${index}`}>
                          <ResultCard
                            resultado={r}
                            clasesBuscadas={clases}
                          />
                        </li>
                      ))}
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
        </>
      )}

      <p className="mt-8 text-xs text-inapi-muted">
        {copy.chrome.footer.actualizacion}
      </p>
    </main>
  );
}
