import { useEffect, useRef, useState } from "react";
import { Activity, Pause, Play } from "lucide-react";
import { api } from "@/lib/api";
import { SpectrumView } from "./SpectrumView";

interface Props {
  inputIdx: number | null;
  recording: boolean;
}

// 실시간 스펙트럼(EQ) — 상시 표시. 녹음 안 할 땐 모니터 입력으로 갱신, 프리즈로 고정.
export function SpectrumPanel({ inputIdx, recording }: Props) {
  const [frozen, setFrozen] = useState(false);
  const [spec, setSpec] = useState<{ freqs: number[]; db: number[] }>({ freqs: [], db: [] });
  const timer = useRef<number | null>(null);

  // 녹음 중이 아니면 모니터 입력을 켜서 계속 스펙트럼이 흐르게 한다.
  useEffect(() => {
    if (!recording) {
      api.start_monitor(inputIdx);
      return () => {
        api.stop_monitor();
      };
    }
  }, [recording, inputIdx]);

  // 폴링(프리즈 시 멈춤). 빈 응답은 무시(마지막 곡선 유지).
  useEffect(() => {
    if (frozen) {
      if (timer.current) window.clearInterval(timer.current);
      return;
    }
    timer.current = window.setInterval(async () => {
      const s = await api.get_spectrum();
      if (s.freqs.length > 1) setSpec(s);
    }, 50);
    return () => {
      if (timer.current) window.clearInterval(timer.current);
    };
  }, [frozen]);

  return (
    <div className="vl-card flex min-h-0 flex-1 flex-col overflow-hidden">
      <div className="flex items-center justify-between border-b border-white/[0.06] px-3 py-2">
        <div className="vl-head">
          <Activity className="h-3.5 w-3.5" /> 실시간 스펙트럼
        </div>
        <button
          onClick={() => setFrozen((f) => !f)}
          className={`flex items-center gap-1 rounded-md border px-2 py-0.5 text-[11px] transition-colors ${
            frozen
              ? "border-warning/50 bg-warning/10 text-warning"
              : "border-border text-muted-foreground hover:bg-secondary/60"
          }`}
          title="현재 곡선을 멈춰서 고정"
        >
          {frozen ? <Play className="h-3 w-3" /> : <Pause className="h-3 w-3" />}
          {frozen ? "재개" : "프리즈"}
        </button>
      </div>
      <div className="relative min-h-0 flex-1">
        <SpectrumView freqs={spec.freqs} db={spec.db} />
        {frozen && (
          <span className="absolute right-2 top-2 rounded bg-warning/20 px-1.5 py-0.5 text-[10px] text-warning">
            ❚❚ 프리즈됨
          </span>
        )}
      </div>
    </div>
  );
}
