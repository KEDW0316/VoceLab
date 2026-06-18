import { useEffect, useState } from "react";
import { Music4 } from "lucide-react";
import { api } from "@/lib/api";

type Pitch = { hz: number | null; note?: string; octave?: number; cents?: number };

// 영문 음이름 → 한글 고정도(다=도) 표기
const KO: Record<string, string> = {
  C: "도", "C#": "도#", D: "레", "D#": "레#", E: "미", F: "파",
  "F#": "파#", G: "솔", "G#": "솔#", A: "라", "A#": "라#", B: "시",
};

// 우측 하단 큰 실시간 음정 표시. 녹음/재생/모니터 음정을 한글 "3옥 도"로.
export function PitchView() {
  const [p, setP] = useState<Pitch>({ hz: null });

  useEffect(() => {
    const t = window.setInterval(async () => setP(await api.get_pitch()), 80);
    return () => window.clearInterval(t);
  }, []);

  const has = p.hz != null;
  const cents = p.cents ?? 0;
  const inTune = Math.abs(cents) <= 10;
  const centColor = inTune ? "hsl(var(--success))" : "hsl(var(--warning))";
  const ko = p.note ? KO[p.note] ?? p.note : "";

  return (
    <div className="vl-card flex min-h-0 flex-1 flex-col p-3">
      <div className="vl-head mb-1">
        <Music4 className="h-3.5 w-3.5" /> 실시간 음정
      </div>
      <div className="flex flex-1 flex-col items-center justify-center">
        {has ? (
          <>
            <div className="num text-6xl font-bold leading-none text-foreground">
              <span className="text-3xl text-muted-foreground">{p.octave}옥 </span>
              {ko}
            </div>
            <div className="mt-3 flex items-center gap-2 num text-sm">
              <span className="font-semibold" style={{ color: centColor }}>
                {cents > 0 ? "+" : ""}
                {cents}센트
              </span>
              <span className="text-muted-foreground">· {p.hz?.toFixed(0)}Hz</span>
            </div>
          </>
        ) : (
          <span className="text-sm text-muted-foreground">소리를 내면 음정이 표시됩니다 ♪</span>
        )}
      </div>
    </div>
  );
}
