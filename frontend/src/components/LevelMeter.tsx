interface Props {
  level: number; // 0..1
  segments?: number;
}

// DAW 스타일 세그먼트 VU 미터 (green → amber → red 존).
export function LevelMeter({ level, segments = 28 }: Props) {
  const lit = Math.round(Math.min(1, Math.max(0, level)) * segments);
  return (
    <div className="flex h-3 items-center gap-[2px]">
      {Array.from({ length: segments }).map((_, i) => {
        const frac = i / segments;
        const on = i < lit;
        const color =
          frac > 0.85
            ? "var(--level-high)"
            : frac > 0.65
              ? "var(--level-mid)"
              : "var(--level-low)";
        return (
          <div
            key={i}
            className="h-full flex-1 rounded-[1px] transition-opacity duration-75"
            style={{
              background: `hsl(${color})`,
              opacity: on ? 1 : 0.12,
              boxShadow: on ? `0 0 6px hsl(${color} / 0.6)` : "none",
            }}
          />
        );
      })}
    </div>
  );
}
