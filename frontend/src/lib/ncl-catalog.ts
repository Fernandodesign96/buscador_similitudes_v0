import Fuse from "fuse.js";
import type { NclCobertura } from "./ncl-coberturas";
import { buildCoberturaFuse } from "./ncl-fuse";

let catalogPromise: Promise<NclCobertura[]> | null = null;
let fuseInstance: Fuse<NclCobertura> | null = null;

export async function loadNclCatalog(): Promise<{
  items: NclCobertura[];
  fuse: Fuse<NclCobertura>;
}> {
  if (!catalogPromise) {
    catalogPromise = fetch("/data/ncl-coberturas.json").then(async (res) => {
      if (!res.ok) {
        throw new Error("No se pudo cargar el catálogo de productos y servicios.");
      }
      return (await res.json()) as NclCobertura[];
    });
  }
  const items = await catalogPromise;
  if (!fuseInstance) {
    fuseInstance = buildCoberturaFuse(items);
  }
  return { items, fuse: fuseInstance };
}
