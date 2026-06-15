import { useEffect, useRef } from "react";

interface Props {
  data: number[];
  duration: number;
}

// 캔버스에 파형(중앙선 기준 대칭 채움)을 그린다.
export function Waveform({ data, duration }: Props) {
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

    const mid = h / 2;
    // 중앙선
    ctx.strokeStyle = "rgba(255,255,255,0.08)";
    ctx.beginPath();
    ctx.moveTo(0, mid);
    ctx.lineTo(w, mid);
    ctx.stroke();

    if (!data.length) return;
    const n = data.length;
    ctx.fillStyle = "rgba(45, 212, 191, 0.85)"; // primary(teal)
    ctx.beginPath();
    ctx.moveTo(0, mid);
    for (let x = 0; x < w; x++) {
      const i = Math.floor((x / w) * n);
      const v = data[Math.min(i, n - 1)];
      ctx.lineTo(x, mid - v * mid * 0.95);
    }
    for (let x = w - 1; x >= 0; x--) {
      const i = Math.floor((x / w) * n);
      const v = data[Math.min(i, n - 1)];
      ctx.lineTo(x, mid + v * mid * 0.95);
    }
    ctx.closePath();
    ctx.fill();
  }, [data]);

  return (
    <div className="relative h-full w-full">
      <canvas ref={ref} className="h-full w-full" />
      <span className="absolute bottom-1 right-2 text-[10px] text-muted-foreground">
        {duration.toFixed(1)}s
      </span>
    </div>
  );
}
