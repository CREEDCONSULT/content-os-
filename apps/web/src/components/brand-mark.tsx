import { cn } from "@/lib/cn";

export function BrandMark({
  compact = false,
  className,
}: {
  compact?: boolean;
  className?: string;
}) {
  return (
    <div className={cn("flex items-center gap-3", className)} data-testid="brand-mark">
      <div className="relative grid size-9 place-items-center rounded-xl border border-gold/45 bg-gold/8">
        <span className="font-display text-lg font-bold italic text-gold-bright">M</span>
        <span className="absolute -right-0.5 -top-0.5 size-1.5 rounded-full bg-gold-bright shadow-[0_0_12px_#f0cf80]" />
      </div>
      {!compact && (
        <div>
          <div className="text-[0.96rem] font-bold tracking-[0.02em] text-ink">
            MEZIE <span className="font-medium text-gold">BrandOS</span>
          </div>
          <div className="mt-0.5 text-[0.58rem] font-semibold uppercase tracking-[0.2em] text-faint">
            Builder Intelligence
          </div>
        </div>
      )}
    </div>
  );
}
