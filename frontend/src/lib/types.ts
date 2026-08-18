export interface DesgloseSimilitud {
  ortografica: number;
  fonetica: number;
}

/**
 * El API envía nombre, clases, similitud, desglose y clase_relacionada.
 * Si llega `mark_code` (como en el parquet), el frontend cruza el Excel por
 * esa llave. Si no, usa nombre + clases. Estado y año salen del Excel.
 */
export interface Resultado {
  nombre: string;
  clases: number[];
  similitud: number;
  desglose: DesgloseSimilitud;
  clase_relacionada: boolean;
  mark_code?: number;
  estado?: string;
  anio_estado?: number;
  solicitudes?: string[];
  nro_registro?: string;
  tipo?: string;
  titular?: string;
  titular_nota?: string;
  fechas?: {
    presentacion?: string;
    publicacion?: string;
    registro?: string;
    vigencia?: string;
  };
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
