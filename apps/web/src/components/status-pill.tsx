import { cn } from "@/lib/cn";

const tones = {
  gold: "border-gold/30 bg-gold/8 text-gold-bright",
  green: "border-green/30 bg-green/8 text-green",
  blue: "border-blue/30 bg-blue/8 text-blue",
  purple: "border-purple/30 bg-purple/8 text-purple",
  danger: "border-danger/30 bg-danger/8 text-danger",
  neutral: "border-line-bright bg-panel-soft text-muted",
};

export function StatusPill({
  children,
  tone = "neutral",
  dot = false,
}: {
  children: React.ReactNode;
  tone?: keyof typeof tones;
  dot?: boolean;
}) {
  return (
    <span
      className={cn(
        "inline-flex w-fit items-center gap-1.5 rounded-full border px-2 py-1 text-[0.64rem] font-bold uppercase tracking-[0.09em]",
        tones[tone],
      )}
    >
      {dot && <span className="size-1.5 rounded-full bg-current" />}
      {children}
    </span>
  );
}
