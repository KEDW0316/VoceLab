import { History, Play, Star, Trash2 } from "lucide-react";
import type { SessionSummary } from "@/lib/types";
import { useI18n } from "@/lib/i18n";

const STATUS_COLOR: Record<string, string> = {
  good: "hsl(var(--success))",
  watch: "hsl(var(--warning))",
  poor: "hsl(var(--danger))",
  info: "hsl(var(--muted-foreground))",
};

function time(iso: string) {
  const d = new Date(iso);
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${d.getMinutes().toString().padStart(2, "0")}`;
}

interface Props {
  sessions: SessionSummary[];
  currentId: string | null;
  baselineId: string | null;
  onLoad: (id: string) => void;
  onPlay: (id: string) => void;
  onDelete: (id: string) => void;
  onSetBaseline: (id: string) => void;
}

export function SessionBar({
  sessions, currentId, baselineId, onLoad, onPlay, onDelete, onSetBaseline,
}: Props) {
  const { t } = useI18n();
  return (
    <div className="vl-card p-3">
      <div className="mb-1.5 vl-head">
        <History className="h-3.5 w-3.5" /> {t("panel.history")}
        <span className="font-normal text-muted-foreground/60">
          ({sessions.length}) · {t("history.baselineHint")}
        </span>
      </div>
      {sessions.length === 0 ? (
        <p className="px-1 py-1.5 vl-label">{t("history.empty")}</p>
      ) : (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {sessions.map((s) => {
            const selected = s.id === currentId;
            const isBaseline = s.id === baselineId;
            return (
              <div
                key={s.id}
                onClick={() => onLoad(s.id)}
                className={`vl-lift group relative w-[136px] shrink-0 cursor-pointer rounded-md px-2.5 py-1.5 ${
                  selected ? "bg-primary/15" : "bg-secondary/40 hover:bg-secondary/60"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="num text-[11px] text-muted-foreground">{time(s.created_at)}</span>
                  {isBaseline && <Star className="h-3 w-3 fill-primary text-primary" />}
                </div>
                <div className="truncate text-[11px] text-foreground/90">
                  {s.label || t("history.untitled")}
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-[11px] text-muted-foreground">CPPS</span>
                  <span
                    className="num text-sm font-semibold"
                    style={{ color: STATUS_COLOR[s.cpps_status] }}
                  >
                    {s.cpps === null ? "—" : s.cpps.toFixed(1)}
                  </span>
                </div>

                {/* 액션 (호버 시) */}
                <div className="mt-1 flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                  <button onClick={(e) => { e.stopPropagation(); onPlay(s.id); }} title={t("history.play")} className="rounded p-0.5 hover:bg-secondary">
                    <Play className="h-3.5 w-3.5 text-muted-foreground hover:text-primary" />
                  </button>
                  <button onClick={(e) => { e.stopPropagation(); onSetBaseline(s.id); }} title={t("history.baseline")} className="rounded p-0.5 hover:bg-secondary">
                    <Star className={`h-3.5 w-3.5 ${isBaseline ? "fill-primary text-primary" : "text-muted-foreground hover:text-primary"}`} />
                  </button>
                  <button onClick={(e) => { e.stopPropagation(); onDelete(s.id); }} title={t("history.delete")} className="ml-auto rounded p-0.5 hover:bg-secondary">
                    <Trash2 className="h-3.5 w-3.5 text-muted-foreground hover:text-danger" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
