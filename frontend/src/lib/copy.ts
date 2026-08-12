/**
 * Textos de la interfaz — Lenguaje Claro (INAPI).
 * Criterios: checklist A–H (calidad web / RLC).
 * Última revisión copy: 12-08-2026.
 */
export const copy = {
  meta: {
    title: "Revisa si tu marca se parece a otra — INAPI",
    description:
      "Compara el nombre de tu marca con marcas ya pedidas o registradas en INAPI. Revisa el parecido al escribir y al pronunciar antes de solicitar el registro.",
  },
  page: {
    title: "Revisa si tu marca se parece a otra",
    subtitleLanding:
      "Usa esta herramienta antes de pedir el registro de tu marca.",
    subtitleSearch:
      "Escribe el nombre y, si quieres, elige los productos o servicios. Luego revisa las marcas parecidas.",
  },
  landing: {
    queEsTitulo: "¿Qué hace esta herramienta?",
    queEsP1:
      "Compara el nombre que escribes con marcas ya pedidas o registradas en INAPI. Te muestra el parecido según cómo se escribe y cómo suena en español.",
    queEsP2:
      "Cuanto más se parecen al escribirse o al pronunciarse, más conviene revisar esa marca antes de solicitar.",
    antesTitulo: "Antes de empezar",
    checklist: [
      "Esta revisión mira solo el nombre escrito (no el dibujo ni el logo).",
      "El resultado es una orientación: no decide si INAPI aceptará o rechazará tu solicitud.",
      "Si tu caso es complejo, puedes pedir ayuda a un ejecutivo de INAPI de manera presencial o telefónica.",
    ] as const,
    legalSummary: "Leer el aviso legal completo",
    legalAcordado:
      "Este buscador permite identificar posibles coincidencias o similitudes de nombre con marcas previamente solicitadas o registradas ante INAPI. Sus resultados tienen un carácter meramente informativo y orientador para los usuarios, no incluye el análisis de los elementos figurativos, gráficos o de imagen. Los resultados pueden contener algunos errores o imprecisiones. En consecuencia, su uso es de exclusiva responsabilidad de quien lo utiliza y, en ningún caso, sustituye, anticipa ni prejuzga el examen sustantivo que corresponde realizar a INAPI conforme a la normativa vigente, ni asegura el resultado de dicho examen o la eventual concesión o rechazo de una solicitud de marca.",
    acceptLabel: "Leí el aviso y quiero continuar",
    continue: "Comenzar revisión",
  },
  search: {
    label: "Nombre de tu marca",
    placeholder: "Ejemplo: Mi Marca",
    hint: "Ejemplo: Mi Marca",
    classesLabel: "Productos o servicios",
    nclTooltipTitle: "¿Qué son los productos o servicios?",
    nclTooltipText:
      "La Clasificación Internacional de Niza (NCL) agrupa productos y servicios en 45 clases. Elige una o más clases para acotar la búsqueda. Si no eliges ninguna, buscamos en todas.",
    nclTooltipAria: "Información sobre productos o servicios (Clasificación de Niza)",
    classesAll: "Elige una clase para añadirla",
    classesCount: (n: number) =>
      n === 1 ? "1 clase seleccionada" : `${n} clases seleccionadas`,
    classesHint:
      "Cada clase que elijas se suma abajo. Puedes quitarla con la X. Si no eliges ninguna, buscamos en todas.",
    howItWorksTitle: "¿Cómo encuentra marcas este buscador?",
    howItWorks:
      "El buscador encuentra marcas parecidas por cómo se escriben y cómo suenan al pronunciarlas en español.",
    howItWorksExample:
      "Ejemplo: Casa Blanca y Blanca Casa. O Cauquenes y Kaukenes.",
    howItWorksAria: "¿Cómo encuentra marcas este buscador?",
    submit: "Buscar marcas parecidas",
    loading: "Buscando marcas parecidas…",
    clear: "Limpiar",
    clearAria: "Limpiar nombre, clases y resultados",
  },
  results: {
    summaryTitle: "Observaciones de similitud",
    coincidenciasIntro: (total: number, consulta: string) =>
      total === 1
        ? `Hay 1 marca parecida a «${consulta}». Te recomendamos revisarla.`
        : `Hay ${total} marcas parecidas a «${consulta}». Te recomendamos revisar esas similitudes.`,
    coincidenciasRegistro:
      "Si otra persona ya tiene una marca igual o muy parecida en la misma clase de productos o servicios, puedes cambiar el nombre antes de solicitar.",
    coincidenciasNoDecide:
      "Esto no decide si INAPI acepta o rechaza tu solicitud. Sirve para que compares y decidas si conviene ajustar el nombre o la cobertura.",
    coincidenciasVerificaTitulo: "Revisa si se parecen en:",
    coincidenciasAspectos: [
      "Cómo se escriben",
      "Cómo suenan al pronunciarlos",
      "Qué productos o servicios cubren",
    ] as const,
    emptyTitle: "No encontramos marcas con un parecido alto",
    empty:
      "No hay marcas registradas con un parecido alto al nombre que escribiste.",
    emptyHint: (q: string) =>
      `Marca buscada: «${q}». Puedes continuar con tu solicitud si lo deseas.`,
    emptyFiltered:
      "No hay marcas con un parecido alto en las clases que elegiste. Prueba otras clases o busca sin filtrar.",
    error: (msg: string) =>
      `No pudimos completar la búsqueda. ${msg} Intenta de nuevo en unos minutos.`,
    claseRelacionada: "Misma clase de productos o servicios",
    ortografica: "Parecido al escribir",
    fonetica: "Parecido al pronunciar",
    coberturaTitulo: "Clases encontradas para esta marca",
    estadoChip: "Estado de la marca",
    verDetalle: "Ver detalle de la marca",
    mostrando: (shown: number, total: number) =>
      `Mostrando ${shown} de ${total} marcas parecidas`,
  },
  help: {
    title: "¿Cómo leer estos resultados?",
    criteriosTitulo: "Cómo se calcula el parecido",
    escritoTitulo: "Al escribir",
    escritoTexto:
      "Mide si las palabras se ven parecidas. Ejemplo: Casa Blanca y Blanca Casa.",
    sonidoTitulo: "Al pronunciar",
    sonidoTexto:
      "Mide si suenan parecido en español de Chile. Ejemplo: Cauquenes y Kaukenes.",
    combinacionTexto:
      "Revisa ambas señales en cada marca. Un parecido alto al escribir o al pronunciar no significa un rechazo automático.",
    nivelesTitulo: "Qué hacer con lo que ves",
    nivelAlto: {
      rango: "Parecido alto",
      accion:
        "Conviene comparar bien el nombre y las clases antes de solicitar.",
    },
    nivelMedio: {
      rango: "Parecido parcial",
      accion: "Hay coincidencias. Revisa si cubren los mismos productos o servicios.",
    },
    nivelBajo: {
      rango: "Parecido bajo",
      accion: "Es menos probable un conflicto solo por el nombre.",
    },
  },
  detail: {
    eyebrow: "Detalle de la marca",
    back: "Volver a marcas parecidas",
    backCrumb: "Marcas parecidas",
    kindFallback: "Marca de palabra",
    visualTitulo: "Cómo se ve",
    idsTitulo: "Identificación",
    datesTitulo: "Fechas importantes",
    coverageTitulo: "Productos o servicios que cubre",
    ownerTitulo: "Dueño o dueña",
    statusTitulo: "Estado del trámite",
    solicitud: "N.° de solicitud",
    solicitudTip:
      "Número que INAPI asigna cuando alguien pide registrar una marca.",
    registro: "N.° de registro",
    registroTip: "Número que identifica la marca cuando ya está inscrita.",
    estado: "Estado",
    tipo: "Tipo de marca",
    tipoTip:
      "Marca de palabra (solo texto), mixta (texto y dibujo), figurativa (solo dibujo) u otros tipos.",
    presentacion: "Fecha de presentación",
    publicacion: "Fecha de publicación",
    fechaRegistro: "Fecha de registro",
    vigencia: "Vigencia",
    unavailable: "Dato no disponible en este MVP",
    unavailableHint:
      "Este dato llegará cuando se conecte la ficha completa de la marca. Mientras tanto puedes revisar el nombre y las clases.",
    scoreHint: "Orientación de parecido, no un rechazo automático.",
    irSolicitar: "Ir a solicitar tu marca",
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
      actual: "Revisa si tu marca se parece a otra",
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
      actualizacion: "Última actualización: 12-08-2026",
    },
  },
} as const;
