"use client";

import { useEffect, useState } from "react";
import { ChevronUp } from "lucide-react";
import { copy } from "@/lib/copy";

const UMBRAL_PX = 400;

export function ScrollToTopButton() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > UMBRAL_PX);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  if (!visible) return null;

  return (
    <button
      type="button"
      onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      className="fixed right-6 bottom-6 z-50 inline-flex size-12 items-center justify-center rounded-full bg-inapi-blue text-white shadow-md hover:bg-inapi-blue-dark"
      aria-label={copy.results.volverArriba}
    >
      <ChevronUp className="size-6" aria-hidden />
    </button>
  );
}
