import { useEffect, useRef } from "react";
import { AudioLines } from "lucide-react";
import { useI18n } from "@/lib/i18n";

interface Props {
  data: number[]; // 진폭 엔벨로프 0..1
  duration: number; // 초
  startSec: number; // 재생 시작 마커 위치(초)
  playing: boolean;
  loop: boolean;
  onSeek: (sec: number) => void; // 파형 클릭 → 그 위치에서 재생
}

export function Waveform({ data, duration, startSec, playing, loop, onSeek }: Props) {
  const { t } = useI18n();
  const ref = useRef<HTMLCanvasElement>(null);
  const raf = useRef<number | null>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d")!;

    const draw = (cursorSec: number | null) => {
      const dpr = window.devicePixelRatio || 1;
      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      if (canvas.width !== w * dpr || canvas.height !== h * dpr) {
        canvas.width = w * dpr;
        canvas.height = h * dpr;
      }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      const mid = h / 2;

      // 중앙선
      ctx.strokeStyle = "rgba(255,255,255,0.06)";
      ctx.beginPath();
      ctx.moveTo(0, mid);
      ctx.lineTo(w, mid);
      ctx.stroke();

      // 파형
      if (data.length) {
        const n = data.length;
        const grad = ctx.createLinearGradient(0, 0, 0, h);
        grad.addColorStop(0, "rgba(20, 224, 184, 0.9)");
        grad.addColorStop(0.5, "rgba(20, 224, 184, 0.5)");
        grad.addColorStop(1, "rgba(20, 224, 184, 0.9)");
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
      }

      if (duration > 0) {
        // 시작 마커 (은은한 흰 선)
        const mx = (startSec / duration) * w;
        ctx.strokeStyle = "rgba(255,255,255,0.35)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(mx, 0);
        ctx.lineTo(mx, h);
        ctx.stroke();

        // 재생 헤드 (밝은 틸)
        if (cursorSec != null) {
          const cx = (cursorSec / duration) * w;
          ctx.strokeStyle = "rgba(45, 212, 191, 1)";
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.moveTo(cx, 0);
          ctx.lineTo(cx, h);
          ctx.stroke();
        }
      }
    };

    if (playing && duration > 0) {
      const t0 = performance.now();
      const tick = () => {
        const elapsed = (performance.now() - t0) / 1000;
        let pos = startSec + elapsed;
        if (pos >= duration) {
          if (loop) pos = ((startSec + elapsed) % duration) || 0;
          else pos = duration;
        }
        draw(pos);
        raf.current = requestAnimationFrame(tick);
      };
      raf.current = requestAnimationFrame(tick);
      return () => {
        if (raf.current) cancelAnimationFrame(raf.current);
      };
    }
    draw(null); // 정지 상태: 마커만
  }, [data, duration, startSec, playing, loop]);

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const sec = ((e.clientX - rect.left) / rect.width) * duration;
    onSeek(Math.max(0, Math.min(duration, sec)));
  };

  return (
    <div
      className="relative h-full w-full cursor-pointer"
      onClick={handleClick}
      title={t("waveform.seek.title")}
    >
      <canvas ref={ref} className="h-full w-full" />
      {!data.length && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-1.5 text-muted-foreground/40">
          <AudioLines className="h-7 w-7" />
          <span className="text-xs">{t("waveform.empty")}</span>
        </div>
      )}
    </div>
  );
}
