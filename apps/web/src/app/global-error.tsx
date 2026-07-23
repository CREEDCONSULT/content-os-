"use client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body>
        <main className="grid min-h-screen place-items-center bg-canvas px-6 text-ink">
          <div className="surface max-w-lg p-8 text-center">
            <p className="eyebrow">Workspace fault</p>
            <h1 className="mt-3 font-display text-4xl font-semibold">BrandOS hit an unexpected boundary.</h1>
            <p className="mt-4 text-sm leading-6 text-muted">{error.message}</p>
            <button className="button-primary mt-7" type="button" onClick={reset}>
              Retry workspace
            </button>
          </div>
        </main>
      </body>
    </html>
  );
}
