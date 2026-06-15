import { useEffect, useRef, useState } from "react";
import { Pause, Play, Waves, Activity } from "lucide-react";
import { api } from "@/lib/api";
import { Spectrogram } from "./Spectrogram";
import { SpectrumView } from "./SpectrumView";

type Tab = "spectrogram" | "spectrum";

interface Props {
  spectrogram: number[][];
}

// 스펙트로그램 / 실시간 스펙트럼(EQ) 탭 + 프리즈(멈춤).
export function VizTabs({ spectrogram }: Props) {
  const [tab, setTab] = useState<Tab>("spectrogram");
  const [frozen, setFrozen] = useState(false);
  const [spec, setSpec] = useState<{ freqs: number[]; db: number[] }>({ freqs: [], db: [] });
  const timer = useRef<number | null>(null);

  // 실시간 스펙트럼 폴링: 스펙트럼 탭 + 프리즈 해제일 때만. 빈 응답은 무시(마지막 곡선 유지).
  useEffect(() => {
    if (tab !== "spectrum" || frozen) {
      if (timer.current) window.clearInterval(timer.current);
      timer.current = null;
      return;
    }
    timer.current = window.setInterval(async () => {
      const s = await api.get_spectrum();
      if (s.freqs.length > 1) setSpec(s);
    }, 50);
    return () => {
      if (timer.current) window.clearInterval(timer.current);
    };
  }, [tab, frozen]);

  const TabBtn = ({ id, icon, label }: { id: Tab; icon: React.ReactNode; label: string }) => (
    <button
      onClick={() => setTab(id)}
      className={`flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
        tab === id ? "bg-secondary text-foreground" : "text-muted-foreground hover:text-foreground"
      }`}
    >
      {icon}
      {label}
    </button>
  );

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-lg border border-border bg-card">
      <div className="flex items-center justify-between border-b border-border px-2 py-1.5">
        <div className="flex items-center gap-1">
          <TabBtn id="spectrogram" icon={<Waves className="h-3.5 w-3.5" />} label="스펙트로그램" />
          <TabBtn id="spectrum" icon={<Activity className="h-3.5 w-3.5" />} label="실시간 스펙트럼" />
        </div>
        {tab === "spectrum" && (
          <button
            onClick={() => setFrozen((f) => !f)}
            className={`flex items-center gap-1 rounded-md border px-2 py-1 text-[11px] transition-colors ${
              frozen
                ? "border-warning/50 bg-warning/10 text-warning"
                : "border-border text-muted-foreground hover:bg-secondary/60"
            }`}
            title="실시간 스펙트럼을 멈추고 현재 곡선을 고정"
          >
            {frozen ? <Play className="h-3 w-3" /> : <Pause className="h-3 w-3" />}
            {frozen ? "재개" : "프리즈"}
          </button>
        )}
      </div>
      <div className="relative min-h-0 flex-1">
        {tab === "spectrogram" ? (
          <Spectrogram data={spectrogram} />
        ) : (
          <SpectrumView freqs={spec.freqs} db={spec.db} />
        )}
        {tab === "spectrum" && frozen && (
          <span className="absolute right-2 top-2 rounded bg-warning/20 px-1.5 py-0.5 text-[10px] text-warning">
            ❚❚ 프리즈됨
          </span>
        )}
      </div>
    </div>
  );
}
