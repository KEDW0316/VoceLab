import { useEffect, useRef } from "react";
import { AudioLines } from "lucide-react";

interface Props {
  data: number[]; // 진폭 엔벨로프 0..1
}

export function Waveform({ data }: Props) {
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
    ctx.strokeStyle = "rgba(255,255,255,0.06)";
    ctx.beginPath();
    ctx.moveTo(0, mid);
    ctx.lineTo(w, mid);
    ctx.stroke();

    if (!data.length) return;
    const n = data.length;
    const grad = ctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, "rgba(20, 224, 184, 0.95)");
    grad.addColorStop(0.5, "rgba(20, 224, 184, 0.55)");
    grad.addColorStop(1, "rgba(20, 224, 184, 0.95)");
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.moveTo(0, mid);
    for (let x = 0; x < w; x++) {
      const v = data[Math.min(Math.floor((x / w) * n), n - 1)];
      ctx.lineTo(x, mid - v * mid * 0.92);
    }
    for (let x = w - 1; x >= 0; x--) {
      const v = data[Math.min(Math.floor((x / w) * n), n - 1)];
      ctx.lineTo(x, mid + v * mid * 0.92);
    }
    ctx.closePath();
    ctx.fill();
  }, [data]);

  return (
    <div className="relative h-full w-full">
      <canvas ref={ref} className="h-full w-full" />
      {!data.length && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-1.5 text-muted-foreground/40">
          <AudioLines className="h-7 w-7" />
          <span className="text-xs">녹음하면 파형이 표시됩니다</span>
        </div>
      )}
    </div>
  );
}
