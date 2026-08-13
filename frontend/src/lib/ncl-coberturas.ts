export type TipoCobertura = "Producto" | "Servicio";

export interface NclCobertura {
  id: number;
  clase: number;
  cobertura: string;
  tipo: TipoCobertura;
}
