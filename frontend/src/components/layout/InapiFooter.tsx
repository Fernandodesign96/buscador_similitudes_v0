import Image from "next/image";
import Link from "next/link";
import { copy } from "@/lib/copy";

export function InapiFooter() {
  const c = copy.chrome.footer;
  return (
    <footer className="mt-auto bg-inapi-navy text-left text-white">
      <div className="mx-auto flex max-w-[1140px] flex-wrap gap-12 px-6 py-12">
        <div className="min-w-[260px] flex-[1_1_300px]">
          <Image
            src="/uploads/inapi_logo.jpg"
            alt="Logotipo del Instituto Nacional de Propiedad Industrial (INAPI)"
            width={84}
            height={84}
            className="rounded-sm"
          />
          <p className="mt-4 text-[15px] leading-snug font-bold">{c.institucion}</p>
          <p className="mt-1.5 max-w-xs text-sm leading-relaxed text-white/78">
            {c.descripcion}
          </p>
        </div>
        <div className="min-w-[180px] flex-[0_1_230px]">
          <h2 className="mb-4 text-base font-bold">{c.dondeEstamos}</h2>
          <ul className="list-none space-y-3 text-sm leading-snug text-white/85">
            <li>{c.direccion}</li>
            <li>{c.telefono}</li>
            <li>{c.correo}</li>
            <li>{c.rut}</li>
          </ul>
        </div>
        <div className="min-w-[160px] flex-[0_1_180px]">
          <h2 className="mb-4 text-base font-bold">{c.conversemos}</h2>
          <ul className="list-none space-y-2.5 text-sm">
            {Object.entries(c.enlacesSociales).map(([key, label]) => (
              <li key={key}>
                <Link href="#" className="text-white/85 hover:text-white">
                  {label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
        <div className="min-w-[160px] flex-[0_1_200px]">
          <h2 className="mb-4 text-base font-bold">{c.accesos}</h2>
          <ul className="list-none space-y-2.5 text-sm">
            {Object.entries(c.enlacesAccesos).map(([key, label]) => (
              <li key={key}>
                <Link href="#" className="text-white/85 hover:text-white">
                  {label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div className="bg-[#061526] px-6 py-4">
        <div className="mx-auto flex max-w-[1140px] flex-wrap items-center justify-between gap-5 text-[13px] text-white/70">
          <span>© 2026 INAPI · Gobierno de Chile. {c.licencia}</span>
          <nav className="flex flex-wrap gap-5" aria-label="Enlaces legales">
            {Object.entries(c.enlacesLegales).map(([key, label]) => (
              <Link key={key} href="#" className="hover:text-white">
                {label}
              </Link>
            ))}
          </nav>
        </div>
        <p className="mx-auto mt-2 max-w-[1140px] text-xs text-white/55">
          {c.actualizacion}
        </p>
      </div>
    </footer>
  );
}
