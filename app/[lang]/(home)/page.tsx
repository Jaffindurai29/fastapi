import Link from "next/link";

const copy = {
  en: {
    kicker: "Learn FastAPI",
    title: "FastAPI docs, from zero to your first API",
    subtitle:
      "A friendly, step-by-step guide to building APIs with FastAPI — path params, request bodies, validation, and the automatic interactive docs.",
    cta: "Start reading",
    secondary: "Also available in Tanglish",
    secondaryHref: "/tanglish/docs",
  },
  tanglish: {
    kicker: "FastAPI Kathukalam",
    title: "FastAPI docs, zero-la irundhu first API varaikkum",
    subtitle:
      "FastAPI vachu API build panra maadhiri, easy-a, step-by-step-a solra guide — path params, request body, validation, automatic docs ellam irukku.",
    cta: "Padikka start pannunga",
    secondary: "English-layum irukku",
    secondaryHref: "/en/docs",
  },
} as const;

export default async function HomePage({
  params,
}: PageProps<"/[lang]">) {
  const { lang } = await params;
  const t = lang === "tanglish" ? copy.tanglish : copy.en;

  return (
    <main className="flex flex-1 flex-col items-center justify-center px-6 py-24 text-center">
      <p className="text-sm font-medium uppercase tracking-widest text-fd-muted-foreground">
        {t.kicker}
      </p>
      <h1 className="mt-4 max-w-2xl text-4xl font-semibold tracking-tight sm:text-5xl">
        {t.title}
      </h1>
      <p className="mt-6 max-w-xl text-lg text-fd-muted-foreground">
        {t.subtitle}
      </p>
      <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row">
        <Link
          href={`/${lang}/docs`}
          className="rounded-full bg-fd-primary px-6 py-3 text-sm font-semibold text-fd-primary-foreground transition-opacity hover:opacity-90"
        >
          {t.cta}
        </Link>
        <Link
          href={t.secondaryHref}
          className="rounded-full border border-fd-border px-6 py-3 text-sm font-semibold transition-colors hover:bg-fd-accent"
        >
          {t.secondary}
        </Link>
      </div>
    </main>
  );
}
