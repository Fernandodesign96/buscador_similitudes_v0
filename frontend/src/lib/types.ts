export interface DesgloseSimilitud {
  ortografica: number;
  fonetica: number;
}

export interface Resultado {
  nombre: string;
  clases: number[];
  similitud: number;
  desglose: DesgloseSimilitud;
  clase_relacionada: boolean;
}

export type ModoClases = "atenuar" | "filtrar";

export interface BusquedaResponse {
  consulta: string;
  clases: number[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  resultados: Resultado[];
}

export interface BusquedaParams {
  q: string;
  clases?: number[];
  top?: number;
  modo_clases?: ModoClases;
  page?: number;
  per_page?: number;
  similitud_min?: number;
}
