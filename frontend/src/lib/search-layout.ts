/** Alturas y superficies del formulario — UI Kit Gobierno (jerarquía visual). */

/** Etiquetas de campo: peso medio, texto oscuro (no compiten con el CTA). */
export const searchFieldLabelClass =
  "mb-2 flex min-h-11 items-end text-sm font-medium leading-snug text-[#111]";

/** Controles de formulario: borde neutro, sin caja contenedora adicional. */
export const searchControlClass =
  "h-11 w-full rounded-sm border border-[#E6E6E6] bg-white px-3 text-sm text-[#111] shadow-none transition-none focus-visible:border-inapi-blue focus-visible:ring-2 focus-visible:ring-inapi-blue/20 disabled:pointer-events-none disabled:cursor-not-allowed disabled:!border-[#E0E0E0] disabled:!bg-[#E0E0E0] disabled:!text-[#757575] disabled:!opacity-100";

/** Mismo gris que Continuar inactivo, aunque el input no use :disabled. */
export const searchControlLockedClass =
  "!border-[#E0E0E0] !bg-[#E0E0E0] !text-[#757575] !opacity-100 pointer-events-none cursor-not-allowed";

/** Zona de búsqueda: sin “card” extra; el CTA es el único bloque de color fuerte. */
export const searchPanelClass = "w-full pb-8";

/** Botón primario de búsqueda (único acento azul saturado en la zona). */
export const searchSubmitClass =
  "h-11 min-h-11 w-full rounded-sm bg-inapi-blue px-6 text-sm font-bold text-white hover:bg-inapi-blue-dark disabled:bg-[#E0E0E0] disabled:text-[#757575] disabled:opacity-100 lg:min-w-[180px]";

/** Mismo gris que Continuar inactivo, sin atributo disabled (no cancela el clic). */
export const searchSubmitLockedClass =
  "!bg-[#E0E0E0] !text-[#757575] hover:!bg-[#E0E0E0] pointer-events-none cursor-not-allowed";
