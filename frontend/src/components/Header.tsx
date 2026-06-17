import { Activity } from "lucide-react";

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

      <div className="ml-auto flex items-center gap-1.5">
        {recording && <span className="h-1.5 w-1.5 rounded-full bg-danger" />}
        <span className="max-w-[560px] truncate text-xs text-muted-foreground">{status}</span>
      </div>
    </header>
  );
}
