import { Activity, Circle } from "lucide-react";

interface Props {
  recording: boolean;
  status: string;
}

export function Header({ recording, status }: Props) {
  return (
    <header className="flex items-center gap-3">
      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/15 ring-1 ring-primary/30">
        <Activity className="h-5 w-5 text-primary" />
      </div>
      <div className="leading-tight">
        <h1 className="text-base font-bold tracking-tight">
          Voce<span className="text-primary">Lab</span>
        </h1>
        <p className="text-[11px] text-muted-foreground">보컬 트레이닝 보조</p>
      </div>

      <div className="ml-auto flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1.5">
        <Circle
          className={`h-2.5 w-2.5 ${
            recording ? "fill-danger text-danger animate-pulse" : "fill-muted-foreground/40 text-muted-foreground/40"
          }`}
        />
        <span className="max-w-[520px] truncate text-xs text-muted-foreground">{status}</span>
      </div>
    </header>
  );
}
