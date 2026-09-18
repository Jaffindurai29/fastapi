import { i18n } from "@/lib/i18n";
import { uiTranslations } from "fumadocs-ui/i18n";
import type { BaseLayoutProps } from "fumadocs-ui/layouts/shared";

export const translations = i18n
  .translations()
  .extend(uiTranslations())
  .add({
    en: {
      displayName: "English",
    },
    tanglish: {
      displayName: "Tanglish",
    },
  });

export function baseOptions(locale: string): BaseLayoutProps {
  return {
    i18n: true,
    themeSwitch: { enabled: false },
    nav: {
      title: "FastAPI Docs",
      url: `/${locale}`,
    },
    links: [
      {
        text: "Docs",
        url: `/${locale}/docs`,
      },
    ],
  };
}
