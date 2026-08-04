import Link from "next/link";
import { copy } from "@/lib/copy";

export function BreadcrumbNav() {
  return (
    <nav aria-label="Ubicación en el sitio" className="border-b border-[#E6E6E6] bg-white">
      <ol className="mx-auto flex max-w-[1140px] flex-wrap items-center gap-2 px-6 py-3.5 text-left text-sm text-inapi-muted">
        <li>
          <Link href="#" className="text-inapi-blue hover:underline">
            {copy.chrome.breadcrumb.inicio}
          </Link>
        </li>
        <li aria-hidden className="text-[#999]">
          ›
        </li>
        <li>
          <Link href="#" className="text-inapi-blue hover:underline">
            {copy.chrome.breadcrumb.marcas}
          </Link>
        </li>
        <li aria-hidden className="text-[#999]">
          ›
        </li>
        <li className="font-bold text-[#111]" aria-current="page">
          {copy.chrome.breadcrumb.actual}
        </li>
      </ol>
    </nav>
  );
}
