export interface DesgloseSimilitud {
  ortografica: number;
  fonetica: number;
}

/**
 * Campos opcionales: el API actual solo envía nombre, clases, similitud,
 * desglose y clase_relacionada. El resto se muestra como «no disponible»
 * hasta que Camila los agregue (ver frontend/PROPUESTA-DETALLE-MARCA.md).
 */
export interface Resultado {
  nombre: string;
  clases: number[];
  similitud: number;
  desglose: DesgloseSimilitud;
  clase_relacionada: boolean;
  mark_code?: number;
  estado?: string;
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
