import type { BusquedaParams, BusquedaResponse } from "./types";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function buscarMarcas(
  params: BusquedaParams,
): Promise<BusquedaResponse> {
  const search = new URLSearchParams();
  search.set("q", params.q);

  if (params.top !== undefined) {
    search.set("top", String(params.top));
  }
  if (params.clases && params.clases.length > 0) {
    search.set("clases", params.clases.join(","));
  }
  if (params.modo_clases) {
    search.set("modo_clases", params.modo_clases);
  }
  if (params.page !== undefined) {
    search.set("page", String(params.page));
  }
  if (params.per_page !== undefined) {
    search.set("per_page", String(params.per_page));
  }
  if (params.similitud_min !== undefined) {
    search.set("similitud_min", String(params.similitud_min));
  }

  const response = await fetch(`/api/buscar?${search.toString()}`);

  if (!response.ok) {
    let message = `Error HTTP ${response.status}`;
    try {
      const body = (await response.json()) as { error?: string };
      if (body.error) message = body.error;
    } catch {
      // respuesta no JSON
    }
    throw new ApiError(message, response.status);
  }

  return response.json() as Promise<BusquedaResponse>;
}
