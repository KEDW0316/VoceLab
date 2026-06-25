import { Activity, Coffee } from "lucide-react";
import { KOFI_URL } from "@/lib/config";

interface Props {
  recording: boolean;
  status: string;
}

export function Header({ recording, status }: Props) {
  return (
    <header className="flex items-center gap-2.5">
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/15">
        <Activity className="h-4 w-4 text-primary" />
      </div>
      <h1 className="text-sm font-bold tracking-tight">
        Voce<span className="text-primary">Lab</span>
      </h1>

      <div className="ml-auto flex items-center gap-3">
        {recording && <span className="h-1.5 w-1.5 rounded-full bg-danger" />}
        <span className="max-w-[460px] truncate text-xs text-muted-foreground">{status}</span>
        <a
          href={KOFI_URL}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1 rounded-md px-2 py-1 text-[11px] text-muted-foreground transition-colors hover:bg-secondary/60 hover:text-primary"
          title="개발자에게 커피 한 잔 ☕"
        >
          <Coffee className="h-3.5 w-3.5" />
          후원
        </a>
      </div>
    </header>
  );
}
