import { useEffect, useState } from "react";
import { Music4 } from "lucide-react";
import { api } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { pitchDisplay } from "@/lib/content";

type Pitch = { hz: number | null; note?: string; octave?: number; cents?: number };

// 우측 하단 큰 실시간 음정 표시. ko="3옥 도", en="C4".
export function PitchView() {
  const { lang, t } = useI18n();
  const [p, setP] = useState<Pitch>({ hz: null });

  useEffect(() => {
    const timer = window.setInterval(async () => setP(await api.get_pitch()), 80);
    return () => window.clearInterval(timer);
  }, []);

  const has = p.hz != null;
  const cents = p.cents ?? 0;
  const inTune = Math.abs(cents) <= 10;
  const centColor = inTune ? "hsl(var(--success))" : "hsl(var(--warning))";
  const { oct, name } = pitchDisplay(p.note ?? "", p.octave ?? 0, lang);

  return (
    <div className="vl-card flex min-h-0 flex-1 flex-col p-3">
      <div className="vl-head mb-1">
        <Music4 className="h-3.5 w-3.5" /> {t("panel.pitch")}
      </div>
      <div className="flex flex-1 flex-col items-center justify-center">
        {has ? (
          <>
            <div className="num text-6xl font-bold leading-none text-foreground">
              {lang === "ko" ? (
                <>
                  <span className="text-3xl text-muted-foreground">{oct} </span>
                  {name}
                </>
              ) : (
                <>
                  {name}
                  <span className="text-3xl text-muted-foreground">{oct}</span>
                </>
              )}
            </div>
            <div className="mt-3 flex items-center gap-2 num text-sm">
              <span className="font-semibold" style={{ color: centColor }}>
                {cents > 0 ? "+" : ""}
                {cents}{lang === "ko" ? "" : " "}{t("pitch.cents")}
              </span>
              <span className="text-muted-foreground">· {p.hz?.toFixed(0)}Hz</span>
            </div>
          </>
        ) : (
          <span className="text-sm text-muted-foreground">{t("pitch.empty")}</span>
        )}
      </div>
    </div>
  );
}
