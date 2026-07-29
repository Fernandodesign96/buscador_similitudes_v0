import { BuscadorApp } from "@/components/BuscadorApp";
import { BreadcrumbNav } from "@/components/layout/BreadcrumbNav";
import { InapiFooter } from "@/components/layout/InapiFooter";
import { InapiHeader } from "@/components/layout/InapiHeader";

export default function Home() {
  return (
    <>
      <InapiHeader />
      <BreadcrumbNav />
      <BuscadorApp />
      <InapiFooter />
    </>
  );
}
