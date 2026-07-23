"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BadgeCheck,
  Award,
  Bot,
  BookOpenText,
  Boxes,
  CalendarDays,
  ChevronRight,
  CircleGauge,
  Clapperboard,
  FilePenLine,
  FolderArchive,
  Lightbulb,
  LogOut,
  Menu,
  Settings2,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";

import { BrandMark } from "@/components/brand-mark";
import { api, ApiError } from "@/lib/api";
import { cn } from "@/lib/cn";

const navigation = [
  { href: "/dashboard", label: "Command center", icon: CircleGauge },
  { href: "/brand", label: "Brand intelligence", icon: BookOpenText },
  { href: "/ideas", label: "Idea intelligence", icon: Lightbulb },
  { href: "/pipeline", label: "Content lifecycle", icon: Boxes },
  { href: "/studio", label: "Script studio", icon: FilePenLine },
  { href: "/calendar", label: "Content calendar", icon: CalendarDays },
  { href: "/production", label: "Production & shoot", icon: Clapperboard },
  { href: "/assets", label: "Asset library", icon: FolderArchive },
  { href: "/proof", label: "Proof of work", icon: Award },
  { href: "/agent", label: "Agent console", icon: Bot },
  { href: "/approvals", label: "Approval queue", icon: ShieldCheck },
];

const systemNavigation = [{ href: "/settings", label: "System & adapters", icon: Settings2 }];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [mobileOpen, setMobileOpen] = useState(false);
  const userQuery = useQuery({
    queryKey: ["auth", "me"],
    queryFn: api.me,
    retry: false,
  });

  if (userQuery.isError) {
    const error = userQuery.error;
    if (error instanceof ApiError && error.status === 401) {
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
      return <FullScreenLoader label="Opening secure workspace…" />;
    }
    return (
      <div className="grid min-h-screen place-items-center px-6">
        <div className="surface max-w-md p-8 text-center">
          <BrandMark className="justify-center" />
          <h1 className="mt-6 text-xl font-semibold">BrandOS API is unavailable</h1>
          <p className="mt-2 text-sm leading-6 text-muted">
            {error.message} Start the FastAPI service, then retry this secure session check.
          </p>
          <button
            className="button-primary mt-6"
            type="button"
            onClick={() => void userQuery.refetch()}
          >
            Retry connection
          </button>
        </div>
      </div>
    );
  }

  if (userQuery.isPending) return <FullScreenLoader label="Securing your command center…" />;

  const logout = async () => {
    await api.logout();
    queryClient.clear();
    router.replace("/login");
  };

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[17rem_minmax(0,1fr)]">
      {mobileOpen && (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-black/65 backdrop-blur-sm lg:hidden"
          aria-label="Close navigation"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-[17rem] flex-col border-r border-line bg-[#080b10]/98 p-4 shadow-2xl transition-transform lg:sticky lg:top-0 lg:h-screen lg:translate-x-0 lg:shadow-none",
          mobileOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex items-center justify-between px-2 py-3">
          <BrandMark />
          <button
            type="button"
            className="button-ghost min-h-9 px-2 lg:hidden"
            onClick={() => setMobileOpen(false)}
            aria-label="Close navigation"
          >
            <X className="size-5" />
          </button>
        </div>

        <nav className="mt-8 flex-1" aria-label="Primary navigation">
          <p className="px-3 text-[0.62rem] font-bold uppercase tracking-[0.16em] text-faint">
            Operating system
          </p>
          <div className="mt-2 space-y-1">
            {navigation.map((item) => (
              <NavigationLink
                key={item.href}
                {...item}
                active={pathname === item.href || pathname.startsWith(`${item.href}/`)}
                onNavigate={() => setMobileOpen(false)}
              />
            ))}
          </div>

          <p className="mt-8 px-3 text-[0.62rem] font-bold uppercase tracking-[0.16em] text-faint">
            Infrastructure
          </p>
          <div className="mt-2 space-y-1">
            {systemNavigation.map((item) => (
              <NavigationLink
                key={item.href}
                {...item}
                active={pathname === item.href}
                onNavigate={() => setMobileOpen(false)}
              />
            ))}
          </div>
        </nav>

        <div className="rounded-xl border border-line bg-panel/70 p-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-green">
            <BadgeCheck className="size-4" />
            Workspace authenticated
          </div>
          <p className="mt-2 truncate text-xs text-muted">{userQuery.data.display_name}</p>
          <button className="button-ghost mt-2 w-full justify-start px-0" type="button" onClick={logout}>
            <LogOut className="size-4" />
            Sign out
          </button>
        </div>
      </aside>

      <div className="min-w-0">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-line bg-canvas/85 px-4 backdrop-blur-xl sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <button
              type="button"
              className="button-ghost min-h-9 px-2 lg:hidden"
              onClick={() => setMobileOpen(true)}
              aria-label="Open navigation"
            >
              <Menu className="size-5" />
            </button>
            <div>
              <p className="text-xs font-semibold text-muted">
                {navigation.concat(systemNavigation).find((item) => pathname.startsWith(item.href))
                  ?.label ?? "Mezie BrandOS"}
              </p>
              <p className="hidden text-[0.65rem] text-faint sm:block">
                See the possibility. Build the system. Become the evidence.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="hidden items-center gap-1.5 rounded-full border border-purple/25 bg-purple/7 px-3 py-1.5 text-[0.68rem] font-semibold text-purple sm:flex">
              <Sparkles className="size-3.5" />
              AI: controlled mock
            </span>
            <Link href="/ideas" className="button-primary min-h-9 text-xs">
              <Lightbulb className="size-3.5" />
              Capture idea
            </Link>
          </div>
        </header>
        <main className="mx-auto w-full max-w-[1600px] p-4 sm:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}

function NavigationLink({
  href,
  label,
  icon: Icon,
  active,
  onNavigate,
}: {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  active: boolean;
  onNavigate: () => void;
}) {
  return (
    <Link
      href={href}
      onClick={onNavigate}
      className={cn(
        "focus-ring group flex items-center gap-3 rounded-xl border px-3 py-2.5 text-sm transition",
        active
          ? "border-gold/25 bg-gold/8 text-gold-bright"
          : "border-transparent text-muted hover:border-line hover:bg-panel hover:text-ink",
      )}
    >
      <Icon className={cn("size-4", active ? "text-gold" : "text-faint group-hover:text-muted")} />
      <span className="flex-1">{label}</span>
      {active && <ChevronRight className="size-3.5 text-gold" />}
    </Link>
  );
}

function FullScreenLoader({ label }: { label: string }) {
  return (
    <div className="grid min-h-screen place-items-center">
      <div className="text-center">
        <BrandMark className="justify-center" />
        <div className="mx-auto mt-6 h-1 w-40 overflow-hidden rounded-full bg-line">
          <div className="h-full w-1/2 animate-pulse rounded-full bg-gold" />
        </div>
        <p className="mt-3 text-xs text-muted">{label}</p>
      </div>
    </div>
  );
}
