/**
 * Textos de la interfaz — Lenguaje Claro (INAPI).
 * Fuentes: docs/lenguaje-claro/*.pdf
 * Criterios: checklist A–H (39 ítems).
 */
export const copy = {
  meta: {
    title: "Buscador de anterioridades — INAPI",
    description:
      "Compara el nombre de tu marca con marcas ya inscritas en Chile antes de presentar tu solicitud.",
  },
  page: {
    title: "Buscador de anterioridades",
    /** A1, A2: mensaje principal en la parte superior */
    lead:
      "Escribe el nombre de tu marca y revisa si existe otra marca inscrita con un nombre parecido. Así puedes anticipar posibles conflictos antes de presentar tu solicitud.",
    opcionA: "Opción A — Marca más parecida",
    opcionB: "Opción B — Todas las parecidas",
    opcionADesc:
      "Muestra solo la marca inscrita que más se parece al nombre que escribiste.",
    opcionBDesc:
      "Muestra todas las marcas inscritas parecidas. Puedes filtrar por Clasificación Internacional de Niza (NCL).",
  },
  search: {
    label: "Nombre de tu marca",
    placeholder: "Ejemplo: Mi Marca",
    classesLabel: "Clasificación de Niza (NCL)",
    classesOptional: "opcional",
    classesAll: "Todas las clases",
    classesCount: (n: number) =>
      n === 1 ? "1 clase seleccionada" : `${n} clases seleccionadas`,
    submit: "Buscar marcas parecidas",
    loading: "Buscando marcas parecidas…",
  },
  /** A5: solo lo necesario para la tarea; tono informativo, no legal */
  disclaimerShort:
    "El porcentaje es orientativo. No reemplaza el examen que realiza INAPI al revisar tu solicitud.",
  disclaimerFull:
    "El porcentaje indica qué tan parecido es el nombre respecto a marcas ya inscritas, por escritura y por sonido. Te orienta antes de presentar tu solicitud. INAPI revisa cada caso en el examen de fondo y puede llegar a otra conclusión.",
  results: {
    opcionASummary: (q: string) =>
      `La marca inscrita más parecida a «${q}» es:`,
    opcionBSummary: (q: string, total: number) =>
      total === 1
        ? `Encontramos 1 marca parecida a «${q}»:`
        : `Encontramos ${total} marcas parecidas a «${q}»:`,
    empty:
      "No encontramos marcas inscritas con un nombre parecido al que escribiste.",
    emptyFiltered:
      "No hay marcas parecidas en las clases que elegiste. Prueba otras clases o busca sin filtrar.",
    error: (msg: string) =>
      `No pudimos completar la búsqueda. ${msg} Intenta de nuevo en unos minutos.`,
    claseRelacionada: "Misma clase NCL",
    ortografica: "Parecido al escribir",
    fonetica: "Parecido al pronunciar",
    clases: "Clases NCL",
    opcionBNota:
      "Mostramos hasta 200 marcas, de la más parecida a la menos parecida.",
    similitudLabel: "Similitud",
  },
  help: {
    /** C6: resumen al inicio del bloque extenso */
    title: "Cómo leer los resultados",
    resumen:
      "El porcentaje mide parecido de nombres, no si tu marca será aceptada. Abajo explicamos qué significa y cómo se calcula.",
    porcentajeTitulo: "Qué significa el porcentaje",
    porcentajeTexto:
      "Compara el nombre que escribiste con una marca ya inscrita. Considera cómo se escribe y cómo suena en español de Chile. Un porcentaje alto indica más parecido; no indica que tu solicitud será rechazada.",
    criteriosTitulo: "Cómo calculamos el parecido",
    escritoTitulo: "Parecido al escribir",
    escritoTexto:
      "Mide si las palabras se ven similares. Por ejemplo: «Casa Blanca» y «Blanca Casa».",
    sonidoTitulo: "Parecido al pronunciar",
    sonidoTexto:
      "Mide si suenan parecido al decirlas en Chile. Por ejemplo: «Cauquenes» y «Kaukenes».",
    combinacionTexto:
      "Combinamos ambos criterios: 58 % por escritura y 42 % por pronunciación.",
    nivelesTitulo: "Qué hacer según el porcentaje",
    nivelAlto: {
      rango: "75 % a 100 %",
      accion: "Revisa con atención antes de presentar tu solicitud.",
    },
    nivelMedio: {
      rango: "50 % a 74 %",
      accion: "Hay parecido parcial. Revisa el tipo de productos o servicios de cada marca.",
    },
    nivelBajo: {
      rango: "0 % a 49 %",
      accion: "El parecido es bajo. El conflicto es poco probable, según el nombre.",
    },
    nclTitulo: "Qué es la Clasificación de Niza (NCL)",
    nclTexto:
      "Las marcas se inscriben por tipo de producto o servicio. Cada tipo tiene un número de clase (1 a 45). Si indicas las clases de tu marca, resaltamos las coincidencias que comparten al menos una clase contigo.",
  },
  pagination: {
    anterior: "Página anterior",
    siguiente: "Página siguiente",
    ariaLabel: "Paginación de resultados",
  },
  chrome: {
    header: {
      acceso: "Ingresar a Mi INAPI",
      buscarSitio: "Buscar en inapi.cl",
      buscarSitioAria: "Buscar en el sitio de INAPI",
      nav: {
        nosotros: "Nosotros",
        conoceMas: "Conoce más",
        marcas: "Marcas",
        patentes: "Patentes",
        pct: "Tratado de Cooperación en materia de Patentes (PCT)",
        madrid: "Sistema de Madrid",
        sello: "Sello de origen",
        aprende: "Aprende",
        conecta: "Conecta",
      },
    },
    breadcrumb: {
      inicio: "Inicio",
      marcas: "Marcas",
      actual: "Buscador de anterioridades",
    },
    footer: {
      institucion: "Instituto Nacional de Propiedad Industrial (INAPI)",
      descripcion:
        "Servicio público del Estado de Chile, dependiente del Ministerio de Economía, Fomento y Turismo.",
      dondeEstamos: "Dónde estamos",
      direccion: "Carabineros de Chile Nº 195, Santiago",
      telefono: "Teléfono: +56 2 2887 0400",
      correo: "Correo: inapi@inapi.cl",
      rut: "RUT: 65.999.669-3",
      conversemos: "Conversemos",
      enlacesSociales: {
        contacto: "Formulario de contacto",
        facebook: "Página de Facebook de INAPI",
        x: "Cuenta de INAPI en X",
        instagram: "Cuenta de Instagram de INAPI",
        linkedin: "Página de LinkedIn de INAPI",
      },
      accesos: "Accesos útiles",
      enlacesAccesos: {
        registrar: "Registrar una marca",
        chequeo: "Chequeo de marcas",
        faq: "Preguntas frecuentes sobre marcas",
        glosario: "Glosario de propiedad industrial",
        mapa: "Mapa del sitio de INAPI",
        visualizadores: "Descargar visualizadores de documentos",
      },
      licencia:
        "Contenido bajo licencia Creative Commons Atribución 4.0 Internacional (CC BY 4.0).",
      enlacesLegales: {
        mapa: "Mapa del sitio",
        accesibilidad: "Declaración de accesibilidad",
        arco: "Política de privacidad y derechos ARCO",
      },
      actualizacion: "Última actualización: 29-07-2026",
    },
  },
} as const;
