"use client";

import { useCallback, useEffect, useState } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { HelpAccordion } from "@/components/help/HelpAccordion";
import { ResultCard } from "@/components/results/ResultCard";
import { ResultsPagination } from "@/components/results/ResultsPagination";
import { ClassPicker } from "@/components/search/ClassPicker";
import { ApiError, buscarMarcas } from "@/lib/api";
import { copy } from "@/lib/copy";
import type { BusquedaResponse, VistaProducto } from "@/lib/types";
import { cn } from "@/lib/utils";
import {
  searchControlClass,
  searchFieldLabelClass,
  searchPanelClass,
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
  const [vista, setVista] = useState<VistaProducto>("opcion-a");
  const [consulta, setConsulta] = useState("");
  const [clases, setClases] = useState<number[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<BusquedaResponse | null>(null);
  const [searched, setSearched] = useState(false);

  const ejecutarBusqueda = useCallback(
    async (q: string, pageNum: number) => {
      const trimmed = q.trim();
      if (!trimmed) return;

      setLoading(true);
      setError(null);
      setSearched(true);

      try {
        const esOpcionA = vista === "opcion-a";
        const response = await buscarMarcas({
          q: trimmed,
          clases: clases.length > 0 ? clases : undefined,
          top: esOpcionA ? 1 : 200,
          modo_clases: esOpcionA ? "atenuar" : "filtrar",
          page: esOpcionA ? 1 : pageNum,
          per_page: esOpcionA ? 1 : perPage,
        });
        setData(response);
        setPage(response.page);
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
    [vista, clases, perPage],
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    void ejecutarBusqueda(consulta, 1);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    void ejecutarBusqueda(consulta, newPage);
  };

  const handleVistaChange = (nueva: VistaProducto) => {
    setVista(nueva);
    setData(null);
    setError(null);
    setSearched(false);
    setPage(1);
  };

  return (
    <>
      <div className="border-b border-[#E6E6E6] bg-white px-6 py-8 text-left">
        <div className="mx-auto max-w-[1140px]">
          <h1 className="font-[family-name:var(--font-roboto-slab)] text-[31px] font-medium text-[#111]">
            {copy.page.title}
          </h1>
          <p className="mt-3 max-w-2xl text-base leading-relaxed text-inapi-muted">
            {copy.page.lead}
          </p>

          <div
            className="mt-6 flex flex-wrap gap-3"
            role="group"
            aria-label="Modo de visualización de resultados"
          >
            <Button
              type="button"
              variant={vista === "opcion-a" ? "default" : "outline"}
              className={cn(
                "text-left",
                vista === "opcion-a" &&
                  "bg-inapi-blue-dark hover:bg-inapi-blue-dark/90",
              )}
              onClick={() => handleVistaChange("opcion-a")}
            >
              {copy.page.opcionA}
            </Button>
            <Button
              type="button"
              variant={vista === "opcion-b" ? "default" : "outline"}
              className={cn(
                "text-left",
                vista === "opcion-b" &&
                  "bg-inapi-blue-dark hover:bg-inapi-blue-dark/90",
              )}
              onClick={() => handleVistaChange("opcion-b")}
            >
              {copy.page.opcionB}
            </Button>
          </div>
          <p className="mt-2 text-sm text-inapi-muted">
            {vista === "opcion-a"
              ? copy.page.opcionADesc
              : copy.page.opcionBDesc}
          </p>
        </div>
      </div>

      <main className="mx-auto w-full max-w-[1140px] px-6 py-8 text-left">
        <HelpAccordion />

        <section className={cn(searchPanelClass, "mb-6")}>
          <form onSubmit={handleSubmit} className="w-full">
            <div className="grid w-full gap-4 lg:grid-cols-[minmax(0,1fr)_280px_auto] lg:items-start">
              <div className="min-w-0">
                <label htmlFor="searchInput" className={searchFieldLabelClass}>
                  {copy.search.label}
                </label>
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

              <div className="flex w-full flex-col lg:w-auto">
                <div
                  className="mb-2 hidden min-h-11 lg:block"
                  aria-hidden="true"
                />
                <Button
                  type="submit"
                  disabled={!consulta.trim() || loading}
                  className="h-11 min-h-11 w-full rounded-none bg-inapi-blue-dark px-6 font-bold hover:bg-inapi-blue-dark/90 lg:min-w-[180px]"
                >
                  {loading ? copy.search.loading : copy.search.submit}
                </Button>
              </div>
            </div>
          </form>
        </section>

        <p className="mb-8 text-sm leading-relaxed text-inapi-muted">
          {copy.disclaimerShort}
        </p>

        {vista === "opcion-b" && (
          <p className="mb-6 text-sm text-inapi-muted">{copy.results.opcionBNota}</p>
        )}

        {searched && (
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
                <p className="mb-6 text-sm text-inapi-muted">
                  {vista === "opcion-a"
                    ? copy.results.opcionASummary(data.consulta)
                    : copy.results.opcionBSummary(data.consulta, data.total)}
                </p>

                {data.resultados.length === 0 ? (
                  <p className="py-12 text-center text-sm text-inapi-muted">
                    {vista === "opcion-b" && clases.length > 0
                      ? copy.results.emptyFiltered
                      : copy.results.empty}
                  </p>
                ) : (
                  <ul className="list-none">
                    {data.resultados.map((r) => (
                      <li key={`${r.nombre}-${r.similitud}`}>
                        <ResultCard resultado={r} />
                      </li>
                    ))}
                  </ul>
                )}

                {vista === "opcion-b" && (
                  <ResultsPagination
                    page={data.page}
                    totalPages={data.total_pages}
                    onPageChange={handlePageChange}
                  />
                )}

                <p className="mt-8 rounded bg-[#f2f2f2] p-6 text-sm leading-relaxed text-inapi-muted">
                  {copy.disclaimerFull}
                </p>
              </>
            )}
          </section>
        )}

      </main>
    </>
  );
}
