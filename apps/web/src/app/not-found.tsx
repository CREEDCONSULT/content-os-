import Link from "next/link";

import { BrandMark } from "@/components/brand-mark";

export default function NotFound() {
  return (
    <main className="grid min-h-screen place-items-center px-6">
      <div className="surface max-w-lg p-8 text-center">
        <BrandMark className="justify-center" />
        <p className="eyebrow mt-8">404 · Outside the system</p>
        <h1 className="mt-3 font-display text-4xl font-semibold">This route has no operating record.</h1>
        <p className="mt-4 text-sm leading-6 text-muted">
          Return to the command center and continue from a governed workspace.
        </p>
        <Link className="button-primary mt-7" href="/dashboard">
          Open command center
        </Link>
      </div>
    </main>
  );
}
