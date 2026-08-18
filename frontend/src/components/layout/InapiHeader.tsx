import Image from "next/image";
import Link from "next/link";
import { copy } from "@/lib/copy";

const NAV = [
  { key: "nosotros", label: copy.chrome.header.nav.nosotros },
  { key: "conoceMas", label: copy.chrome.header.nav.conoceMas },
  { key: "marcas", label: copy.chrome.header.nav.marcas, active: true },
  { key: "patentes", label: copy.chrome.header.nav.patentes },
  { key: "pct", label: "PCT", title: copy.chrome.header.nav.pct },
  { key: "madrid", label: copy.chrome.header.nav.madrid },
  { key: "sello", label: copy.chrome.header.nav.sello },
  { key: "aprende", label: copy.chrome.header.nav.aprende },
  { key: "conecta", label: copy.chrome.header.nav.conecta },
] as const;

export function InapiHeader() {
  return (
    <header className="sticky top-0 z-40 bg-inapi-navy text-white">
      <div className="mx-auto flex h-[72px] max-w-[1140px] items-center gap-9 px-6">
        <Link href="#" className="inline-flex items-center gap-3">
          <Image
            src="/uploads/inapi_logo.jpg"
            alt="Logotipo del Instituto Nacional de Propiedad Industrial (INAPI)"
            width={52}
            height={52}
            className="rounded-sm"
            priority
          />
          <span className="text-[13px] leading-tight font-medium text-white/85">
            Instituto Nacional
            <br />
            de Propiedad Industrial
          </span>
        </Link>
        <nav
          className="ml-auto hidden items-center gap-6 text-[13px] lg:flex"
          aria-label="Menú principal"
        >
          {NAV.map((item) => (
            <Link
              key={item.key}
              href="#"
              title={"title" in item ? item.title : undefined}
              className={`border-b-[3px] border-transparent pb-1 hover:border-inapi-amber ${
                "active" in item && item.active ? "border-inapi-amber" : ""
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
      <nav
        className="border-t border-b border-[#E6E6E6] bg-[#F2F2F2]"
        aria-label="Accesos del sitio"
      >
        <div className="mx-auto flex max-w-[1140px] items-center justify-end gap-6 px-6 py-3">
          <div className="flex max-w-[300px] flex-1 items-center border border-[#808080] bg-white">
            <input
              type="search"
              placeholder={copy.chrome.header.buscarSitio}
              className="flex-1 px-3.5 py-2.5 text-left text-sm text-[#111] outline-none"
              readOnly
              aria-label={copy.chrome.header.buscarSitioAria}
            />
          </div>
        </div>
      </nav>
    </header>
  );
}
