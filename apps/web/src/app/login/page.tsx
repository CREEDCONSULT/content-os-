import { Suspense } from "react";

import { BrandMark } from "@/components/brand-mark";
import { LoginScreen } from "@/components/login-screen";

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <main className="grid min-h-screen place-items-center">
          <div className="text-center">
            <BrandMark className="justify-center" />
            <div className="skeleton mx-auto mt-6 h-1 w-40 rounded-full" />
          </div>
        </main>
      }
    >
      <LoginScreen />
    </Suspense>
  );
}
