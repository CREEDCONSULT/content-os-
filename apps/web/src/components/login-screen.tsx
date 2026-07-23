"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, KeyRound, ShieldCheck } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useState } from "react";

import { BrandMark } from "@/components/brand-mark";
import { api } from "@/lib/api";

export function LoginScreen() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const [username, setUsername] = useState("mezie");
  const [password, setPassword] = useState("");
  const login = useMutation({
    mutationFn: () => api.login(username, password),
    onSuccess: ({ user }) => {
      queryClient.setQueryData(["auth", "me"], user);
      const next = searchParams.get("next");
      router.replace(next?.startsWith("/") ? next : "/dashboard");
    },
  });

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (username.trim() && password) login.mutate();
  };

  return (
    <main className="grid min-h-screen lg:grid-cols-[1.08fr_0.92fr]">
      <section className="relative hidden overflow-hidden border-r border-line p-12 lg:flex lg:flex-col lg:justify-between">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_25%,rgba(214,173,92,0.12),transparent_26rem)]" />
        <BrandMark className="relative z-10" />
        <div className="relative z-10 max-w-2xl">
          <p className="eyebrow">Personal brand operating system</p>
          <h1 className="mt-4 font-display text-6xl font-semibold leading-[1.06] tracking-[-0.04em]">
            Turn possibility into
            <span className="block italic text-gold">operating evidence.</span>
          </h1>
          <p className="mt-7 max-w-xl text-base leading-7 text-muted">
            One governed workspace for brand truth, idea intelligence, production, approvals,
            distribution, learning, and memory.
          </p>
        </div>
        <div className="relative z-10 grid grid-cols-3 gap-3">
          {["Source-grounded", "Approval-aware", "Demo-honest"].map((item) => (
            <div key={item} className="rounded-xl border border-line bg-panel/55 p-4 text-xs text-muted">
              <ShieldCheck className="mb-3 size-4 text-gold" />
              {item}
            </div>
          ))}
        </div>
      </section>

      <section className="flex items-center justify-center px-5 py-12 sm:px-12">
        <div className="w-full max-w-md">
          <BrandMark className="mb-12 lg:hidden" />
          <p className="eyebrow">Secure workspace</p>
          <h2 className="mt-3 font-display text-4xl font-semibold tracking-[-0.035em]">
            Welcome back.
          </h2>
          <p className="mt-3 text-sm leading-6 text-muted">
            Sign in to your local BrandOS. Credentials remain server-side and the session uses an
            HttpOnly cookie.
          </p>

          <form className="surface mt-8 space-y-5 p-6 sm:p-7" onSubmit={onSubmit}>
            <label className="block">
              <span className="mb-2 block text-xs font-semibold text-muted">Username</span>
              <input
                className="input"
                autoComplete="username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                required
              />
            </label>
            <label className="block">
              <span className="mb-2 block text-xs font-semibold text-muted">Password</span>
              <input
                className="input"
                type="password"
                autoComplete="current-password"
                placeholder="Enter local workspace password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </label>

            {login.isError && (
              <p className="rounded-lg border border-danger/25 bg-danger/8 p-3 text-xs text-danger">
                {login.error.message}
              </p>
            )}

            <button
              className="button-primary w-full"
              type="submit"
              disabled={login.isPending || !username.trim() || !password}
            >
              {login.isPending ? (
                <>
                  <KeyRound className="size-4 animate-pulse" />
                  Verifying…
                </>
              ) : (
                <>
                  Enter BrandOS
                  <ArrowRight className="size-4" />
                </>
              )}
            </button>
          </form>

          <p className="mt-5 text-center text-[0.68rem] leading-5 text-faint">
            Local development starts with username <strong className="text-muted">mezie</strong>.
            Change all bootstrap credentials before any production deployment.
          </p>
        </div>
      </section>
    </main>
  );
}
