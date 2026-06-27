import { Activity, Coffee, Settings as SettingsIcon } from "lucide-react";
import { KOFI_URL } from "@/lib/config";
import { useI18n } from "@/lib/i18n";

interface Props {
  onOpenSettings: () => void;
}

export function Header({ onOpenSettings }: Props) {
  const { t } = useI18n();
  return (
    <header className="flex items-center gap-2.5 border-b border-border px-3 py-2">
      <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/15">
        <Activity className="h-4 w-4 text-primary" />
      </div>
      <h1 className="text-sm font-bold tracking-tight">
        Voce<span className="text-primary">Lab</span>
      </h1>

      <div className="ml-auto flex items-center gap-1">
        <button
          onClick={onOpenSettings}
          className="flex items-center gap-1.5 rounded-md px-2 py-1 text-[11px] text-muted-foreground transition-colors hover:bg-secondary/60 hover:text-foreground"
          title={t("header.settings")}
        >
          <SettingsIcon className="h-3.5 w-3.5" />
          {t("header.settings")}
        </button>
        <a
          href={KOFI_URL}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1 rounded-md px-2 py-1 text-[11px] text-muted-foreground transition-colors hover:bg-secondary/60 hover:text-primary"
          title={t("donate.title")}
        >
          <Coffee className="h-3.5 w-3.5" />
          {t("donate")}
        </a>
      </div>
    </header>
  );
}
