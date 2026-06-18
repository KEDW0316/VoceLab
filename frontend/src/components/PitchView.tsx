interface Pitch {
  hz: number | null;
  note?: string;
  octave?: number;
  cents?: number;
}

// 스펙트럼 위 실시간 음정(노트+옥타브+센트) — 튜너처럼.
export function PitchView({ pitch }: { pitch: Pitch }) {
  const has = pitch.hz != null;
  const cents = pitch.cents ?? 0;
  const inTune = Math.abs(cents) <= 10;
  const centColor = !has
    ? "hsl(var(--muted-foreground))"
    : inTune
      ? "hsl(var(--success))"
      : "hsl(var(--warning))";

  return (
    <div className="pointer-events-none absolute left-3 top-3 flex items-center gap-2 rounded-md bg-background/70 px-2.5 py-1.5 backdrop-blur-sm">
      {has ? (
        <>
          <span className="num text-2xl font-bold leading-none text-foreground">
            {pitch.note}
            <span className="text-base text-muted-foreground">{pitch.octave}</span>
          </span>
          <div className="flex flex-col leading-tight">
            <span className="num text-[11px] font-semibold" style={{ color: centColor }}>
              {cents > 0 ? "+" : ""}
              {cents}¢
            </span>
            <span className="num text-[10px] text-muted-foreground">{pitch.hz?.toFixed(0)}Hz</span>
          </div>
        </>
      ) : (
        <span className="text-xs text-muted-foreground">♪ 음정 없음</span>
      )}
    </div>
  );
}
