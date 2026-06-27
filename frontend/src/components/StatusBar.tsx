import { Mic, Volume2 } from "lucide-react";
import { useI18n } from "@/lib/i18n";

interface Props {
  inputLabel: string | null;
  outputLabel: string | null;
  status: string;
  recording: boolean;
  onOpenSettings: () => void;
}

// 하단 상태바 — 현재 장치 + 샘플레이트 + 상태 메시지 (DAW/IDE식). 장치 클릭 시 설정.
export function StatusBar({ inputLabel, outputLabel, status, recording, onOpenSettings }: Props) {
  const { t } = useI18n();
  return (
    <footer className="flex items-center gap-1 border-t border-border px-3 py-1.5 text-[11px] text-muted-foreground">
      <button
        onClick={onOpenSettings}
        className="flex items-center gap-1.5 rounded px-1.5 py-0.5 transition-colors hover:bg-secondary/60 hover:text-foreground"
        title={t("header.settings")}
      >
        <Mic className="h-3 w-3 shrink-0" />
        <span className="max-w-[200px] truncate">{inputLabel ?? t("statusbar.noDevice")}</span>
      </button>
      <button
        onClick={onOpenSettings}
        className="flex items-center gap-1.5 rounded px-1.5 py-0.5 transition-colors hover:bg-secondary/60 hover:text-foreground"
        title={t("header.settings")}
      >
        <Volume2 className="h-3 w-3 shrink-0" />
        <span className="max-w-[200px] truncate">{outputLabel ?? t("statusbar.noDevice")}</span>
      </button>
      <span className="px-1 text-muted-foreground/30">·</span>
      <span className="num">44.1 kHz</span>

      <div className="ml-auto flex min-w-0 items-center gap-2">
        {recording && <span className="h-1.5 w-1.5 shrink-0 animate-pulse rounded-full bg-danger" />}
        <span className="truncate">{status}</span>
      </div>
    </footer>
  );
}
