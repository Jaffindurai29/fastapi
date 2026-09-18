"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { i18n } from "@/lib/i18n";

export default function RootRedirect() {
  const router = useRouter();

  useEffect(() => {
    router.replace(`/${i18n.defaultLanguage}`);
  }, [router]);

  return null;
}
