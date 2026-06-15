import { useEffect, useRef } from "react";
import { Waves } from "lucide-react";

interface Props {
  data: number[][]; // [freq][time], 0..1
}

// inferno 유사 컬러맵
const STOPS: [number, [number, number, number]][] = [
  [0.0, [0, 0, 4]],
  [0.25, [40, 11, 84]],
  [0.5, [101, 21, 110]],
  [0.7, [159, 42, 99]],
  [0.85, [212, 72, 66]],
  [0.95, [245, 125, 21]],
  [1.0, [252, 255, 164]],
];

function color(t: number): [number, number, number] {
  for (let i = 1; i < STOPS.length; i++) {
    if (t <= STOPS[i][0]) {
      const [t0, c0] = STOPS[i - 1];
      const [t1, c1] = STOPS[i];
      const f = (t - t0) / (t1 - t0 || 1);
      return [
        c0[0] + (c1[0] - c0[0]) * f,
        c0[1] + (c1[1] - c0[1]) * f,
        c0[2] + (c1[2] - c0[2]) * f,
      ];
    }
  }
  return STOPS[STOPS.length - 1][1];
}

export function Spectrogram({ data }: Props) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas || !data.length) return;
    const freqBins = data.length;
    const timeBins = data[0].length;

    // 네이티브 해상도 오프스크린에 픽셀 채우고, 표시 캔버스로 스케일 복사
    const off = document.createElement("canvas");
    off.width = timeBins;
    off.height = freqBins;
    const octx = off.getContext("2d")!;
    const img = octx.createImageData(timeBins, freqBins);
    for (let f = 0; f < freqBins; f++) {
      const yRow = freqBins - 1 - f; // 저주파를 아래로
      for (let t = 0; t < timeBins; t++) {
        const [r, g, b] = color(Math.max(0, Math.min(1, data[f][t])));
        const idx = (yRow * timeBins + t) * 4;
        img.data[idx] = r;
        img.data[idx + 1] = g;
        img.data[idx + 2] = b;
        img.data[idx + 3] = 255;
      }
    }
    octx.putImageData(img, 0, 0);

    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    const ctx = canvas.getContext("2d")!;
    ctx.scale(dpr, dpr);
    ctx.imageSmoothingEnabled = true;
    ctx.drawImage(off, 0, 0, w, h);
  }, [data]);

  return (
    <div className="relative h-full w-full">
      <canvas ref={ref} className="h-full w-full" />
      {!data.length && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-1.5 text-muted-foreground/40">
          <Waves className="h-7 w-7" />
          <span className="text-xs">녹음하면 스펙트로그램이 표시됩니다</span>
        </div>
      )}
    </div>
  );
}
