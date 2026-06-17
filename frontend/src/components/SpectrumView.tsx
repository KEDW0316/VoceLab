import { useEffect, useRef } from "react";
import { Activity } from "lucide-react";

interface Props {
  freqs: number[];
  db: number[]; // 절대 dBFS (≈0..-100)
  floor?: number;
}

const GRID_FREQS = [100, 1000, 10000];
const GRID_DB = [-20, -40, -60, -80];

function fmtHz(f: number) {
  return f >= 1000 ? `${f / 1000}k` : `${f}`;
}

// DAW EQ식 실시간 스펙트럼 곡선 (로그 주파수 × dB).
export function SpectrumView({ freqs, db, floor = -100 }: Props) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    const ctx = canvas.getContext("2d")!;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, w, h);

    if (freqs.length < 2) return;
    const fmin = freqs[0], fmax = freqs[freqs.length - 1];
    const lmin = Math.log10(fmin), lmax = Math.log10(fmax);
    const xOf = (f: number) => ((Math.log10(f) - lmin) / (lmax - lmin)) * w;
    const yOf = (d: number) => (Math.min(0, Math.max(floor, d)) / floor) * h;

    // 그리드
    ctx.font = "9px ui-monospace, monospace";
    ctx.fillStyle = "rgba(255,255,255,0.28)";
    ctx.strokeStyle = "rgba(255,255,255,0.06)";
    ctx.lineWidth = 1;
    for (const gf of GRID_FREQS) {
      if (gf < fmin || gf > fmax) continue;
      const x = xOf(gf);
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
      ctx.fillText(fmtHz(gf), x + 3, h - 4);
    }
    for (const gd of GRID_DB) {
      const y = yOf(gd);
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
      ctx.fillText(`${gd}`, 3, y - 2);
    }

    // 막대(기둥) 분석기 — 데이터를 N개 막대로 묶어 각 구간의 피크 dB로 그린다.
    const N = Math.min(64, freqs.length);
    const per = freqs.length / N;
    const grad = ctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, "rgba(94, 234, 212, 1)");   // 위(강): 밝은 틸
    grad.addColorStop(0.5, "rgba(20, 224, 184, 0.95)");
    grad.addColorStop(1, "rgba(13, 148, 136, 0.5)"); // 아래: 어두운 틸
    ctx.fillStyle = grad;
    const slot = w / N;
    const gap = Math.max(1, slot * 0.18);
    const barW = slot - gap;
    for (let i = 0; i < N; i++) {
      let peak = floor;
      const s = Math.floor(i * per);
      const e = Math.max(s + 1, Math.floor((i + 1) * per));
      for (let j = s; j < e && j < db.length; j++) peak = Math.max(peak, db[j]);
      const y = yOf(peak);
      ctx.fillRect(i * slot + gap / 2, y, barW, h - y);
    }
  }, [freqs, db, floor]);

  return (
    <div className="relative h-full w-full">
      <canvas ref={ref} className="h-full w-full" />
      {freqs.length < 2 && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-1.5 text-muted-foreground/40">
          <Activity className="h-7 w-7" />
          <span className="text-xs">입력 신호를 기다리는 중… (소리를 내보세요)</span>
        </div>
      )}
    </div>
  );
}
