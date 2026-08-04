/**
 * Textos de la interfaz — Lenguaje Claro (INAPI).
 * Fuentes: docs/lenguaje-claro/*.pdf
 * Criterios: checklist A–H (37 ítems aplicables).
 * Última revisión copy: 31-07-2026 (reunión Bernarda + Camila).
 */
export const copy = {
  meta: {
    title: "Buscador de marcas — INAPI",
    description:
      "Compara el nombre de tu marca con marcas previamente solicitadas o registradas ante INAPI. Identifica posibles similitudes denominativas antes de presentar tu solicitud ante INAPI.",
  },
  page: {
    title: "Buscador de marcas",
  },
  search: {
    label: "Nombre de tu marca",
    placeholder: "Ejemplo: Mi Marca",
    classesLabel: "Clasificación Internacional de Niza (NCL)",
    classesOptional: "opcional",
    classesAll: "Todas las clases",
    classesCount: (n: number) =>
      n === 1 ? "1 clase seleccionada" : `${n} clases seleccionadas`,
    submit: "Buscar marcas parecidas",
    loading: "Buscando marcas parecidas…",
    clear: "Borrar nombre y resultados",
  },
  /**
   * Disclaimer legal acordado (30-07-2026).
   * Se muestra siempre al final del contenido principal (visible sin necesidad de buscar).
   * Párrafos separados para legibilidad; el sentido jurídico se mantiene.
   */
  disclaimerLegal: {
    title: "Aviso legal",
    paragraphs: [
      "Este buscador fonético permite identificar potenciales coincidencias o similitudes denominativas con marcas previamente solicitadas o registradas ante INAPI. Sus resultados tienen un carácter meramente informativo y orientador para los usuarios, no incluye el análisis de los elementos figurativos, gráficos o de imagen. Los resultados pueden contener algunos errores o imprecisiones. En consecuencia, su uso es de exclusiva responsabilidad de quien lo utiliza y, en ningún caso, sustituye, anticipa ni prejuzga el examen sustantivo que corresponde realizar a INAPI conforme a la normativa vigente, ni asegura el resultado de dicho examen o la eventual concesión o rechazo de una solicitud de marca.",
    ],
  },
  results: {
    coincidenciasIntro: (total: number) =>
      total === 1
        ? "Encontramos 1 coincidencia que podría ser similar a la tuya."
        : `Encontramos ${total} coincidencias que podrían ser similares a la tuya.`,
    coincidenciasRegistro:
      "Aún puedes solicitar el registro si consideras que tu marca es lo suficientemente diferente.",
    coincidenciasVerificaTitulo: "Verifica si son similares en cuanto a:",
    coincidenciasAspectos: [
      "Ortografía",
      "Sonido o pronunciación",
      "Productos o servicios (Clases de Niza)",
    ] as const,
    empty:
      "No encontramos marcas registradas con un nombre parecido al que escribiste.",
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
    title: "¿Cómo entender los resultados?",
    porcentajeTitulo: "¿Qué significa el porcentaje?",
    porcentajeTexto:
      "El buscador compara el nombre que escribiste con marcas previamente solicitadas o registradas ante INAPI. Te muestra un porcentaje de parecido (considera cómo se escribe y cómo suena en español): cuanto más alto, más similar es tu marca respecto a la encontrada. Ese porcentaje orienta, pero no indica si INAPI aceptará o rechazará tu solicitud.",
    criteriosTitulo: "¿Cómo se calcula el parecido?",
    escritoTitulo: "Parecido al escribir",
    escritoTexto:
      "Mide si las palabras se ven similares. Por ejemplo: «Casa Blanca» y «Blanca Casa».",
    sonidoTitulo: "Parecido al pronunciar",
    sonidoTexto:
      "Mide si suenan parecido al decirlas en Chile. Por ejemplo: «Cauquenes» y «Kaukenes».",
    combinacionTexto:
      "Ambos criterios combinados generan el porcentaje que puedes ver en cada marca encontrada, utilizando un color distinto para diferenciar qué tanto se parecen entre sí.",
    nivelesTitulo: "¿Qué significa cada porcentaje?",
    nivelAlto: {
      rango: "75 % a 100 %",
      accion: "Existe mucha similitud, por lo que se recomienda comparar qué características se repiten en ambas marcas —como palabras y/o clases de niza—, antes de presentar tu solicitud.",
    },
    nivelMedio: {
      rango: "50 % a 74 %",
      accion:
        "Existe similitud parcial, es decir, son menos las características que se repiten entre ambas marcas, aún así se recomienda revisar la solicitud de tu marca.",
    },
    nivelBajo: {
      rango: "0 % a 49 %",
      accion:
        "La similitud es baja o muy baja, por lo que los conflictos encontrados entre las características de tu marca con la encontrada son poco probables o casi nulos.",
    },
    nclTitulo: "¿Qué es la Clasificación Internacional de Niza (NCL)?",
    nclTexto:
      "La marca se debe inscribir en al menos una clase (pueden ser varias), lo que dependerá del producto o servicio que esta represente. Existen 45 clases en total. Si tu marca ya se encuentra registrada por un tercero en la clase elegida, lo ideal es hacer una modificación en el nombre o diseño para evitar que sea rechazada.",
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
      actual: "Buscador de marcas",
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
      actualizacion: "Última actualización: 31-07-2026",
    },
  },
} as const;
