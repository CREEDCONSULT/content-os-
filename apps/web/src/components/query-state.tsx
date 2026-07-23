import { AlertTriangle, DatabaseZap } from "lucide-react";

export function LoadingGrid() {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4" aria-label="Loading content">
      {Array.from({ length: 4 }, (_, index) => (
        <div key={index} className="surface h-36 p-5">
          <div className="skeleton h-3 w-24 rounded" />
          <div className="skeleton mt-6 h-9 w-20 rounded" />
          <div className="skeleton mt-5 h-2 w-full rounded" />
        </div>
      ))}
    </div>
  );
}

export function ErrorState({
  error,
  retry,
}: {
  error: Error;
  retry?: () => void;
}) {
  return (
    <div className="surface flex min-h-48 flex-col items-center justify-center p-8 text-center">
      <AlertTriangle className="size-8 text-danger" aria-hidden />
      <h2 className="mt-4 text-lg font-semibold">The command center could not load this data.</h2>
      <p className="mt-2 max-w-lg text-sm text-muted">{error.message}</p>
      {retry && (
        <button className="button-secondary mt-5" type="button" onClick={retry}>
          Retry
        </button>
      )}
    </div>
  );
}

export function EmptyState({
  title,
  body,
}: {
  title: string;
  body: string;
}) {
  return (
    <div className="surface flex min-h-48 flex-col items-center justify-center p-8 text-center">
      <DatabaseZap className="size-8 text-gold" aria-hidden />
      <h2 className="mt-4 text-lg font-semibold">{title}</h2>
      <p className="mt-2 max-w-lg text-sm text-muted">{body}</p>
    </div>
  );
}
