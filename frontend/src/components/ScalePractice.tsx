import { useEffect, useState } from "react";
import { ChevronDown, ChevronUp, Music2, Play } from "lucide-react";
import type { Scale } from "@/lib/types";
import { api, whenBackendReady } from "@/lib/api";
import { loadPref, savePref } from "@/lib/storage";
import { useI18n } from "@/lib/i18n";
import { SCALE_EN, solfegeTokens } from "@/lib/content";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";

const NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
const TONICS = [3, 4, 5].flatMap((o) =>
  NOTES.filter((n) => !(o === 5 && n !== "C")).map((n) => `${n}${o}`)
);

export function ScalePractice() {
  const { lang, t } = useI18n();
  const [scales, setScales] = useState<Scale[]>([]);
  const [scaleKey, setScaleKey] = useState("");
  const [tonic, setTonic] = useState(() => loadPref("tonic") || "C4");

  useEffect(() => {
    let cancelled = false;
    const load = () =>
      api.list_scales().then((s) => {
        if (cancelled || !s.length) return;
        setScales(s);
        setScaleKey((prev) => {
          if (prev && s.some((x) => x.key === prev)) return prev;
          const saved = loadPref("scale");
          return s.some((x) => x.key === saved) ? saved! : s[0].key;
        });
      });
    load(); // 즉시 로드(백엔드 없으면 목, 있으면 실제) — 목록이 절대 비지 않게
    whenBackendReady().then((real) => {
      if (real) load(); // 백엔드 준비되면 실제 목록(17종)으로 갱신
    });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (scaleKey) savePref("scale", scaleKey);
  }, [scaleKey]);
  useEffect(() => {
    savePref("tonic", tonic);
  }, [tonic]);

  const scale = scales.find((s) => s.key === scaleKey);
  // 솔페지는 이동도(movable-do)라 토닉과 무관 — 스케일 데이터의 값을 그대로 사용
  const solfege = scale?.solfege ?? "";
  // EN일 땐 영어 이름/설명/음절로 덮어씀
  const en = (s: Scale) => (lang === "en" ? SCALE_EN[s.key] : undefined);
  const nameOf = (s: Scale) => en(s)?.name ?? s.name;

  const transpose = (d: number) => {
    const i = TONICS.indexOf(tonic) + d;
    if (i >= 0 && i < TONICS.length) setTonic(TONICS[i]);
  };

  return (
    <div className="vl-card p-3">
      <div className="flex flex-wrap items-center gap-2">
        <div className="vl-head">
          <Music2 className="h-3.5 w-3.5" />
          {t("panel.scales")}
        </div>

        <div className="min-w-[180px] flex-1">
          <Select value={scaleKey} onChange={(e) => setScaleKey(e.target.value)}>
            {scales.map((s) => (
              <option key={s.key} value={s.key}>
                {nameOf(s)}
              </option>
            ))}
          </Select>
        </div>

        {/* 키 트랜스포즈 */}
        <div className="flex items-center gap-1 rounded-md bg-secondary/60 p-1">
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => transpose(-1)} title={t("scales.transpose.down")}>
            <ChevronDown className="h-4 w-4" />
          </Button>
          <span className="num w-9 text-center text-sm font-semibold">{tonic}</span>
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => transpose(1)} title={t("scales.transpose.up")}>
            <ChevronUp className="h-4 w-4" />
          </Button>
        </div>

        <Button onClick={() => api.play_guide_tone(scaleKey, tonic)}>
          <Play className="h-4 w-4" /> {t("scales.guide")}
        </Button>
      </div>

      {scale && (
        <div className="mt-2.5 flex flex-wrap items-center gap-x-3 gap-y-1.5">
          {/* 솔페지 pill */}
          <div className="flex flex-wrap items-center gap-1">
            {scale.glide ? (
              <span className="rounded-md bg-secondary px-2 py-0.5 text-xs text-foreground">{t("scales.glide")}</span>
            ) : (
              solfegeTokens(solfege, lang).map((n, i) => (
                <span key={i} className="num rounded-md bg-secondary px-1.5 py-0.5 text-xs text-foreground">
                  {n}
                </span>
              ))
            )}
          </div>
          <span className="rounded-md border border-border px-2 py-0.5 text-[11px] text-muted-foreground">
            {t("scales.syllable")} {en(scale)?.syllable ?? scale.syllable}
          </span>
          <p className="vl-label leading-snug">{en(scale)?.desc ?? scale.description}</p>
        </div>
      )}
    </div>
  );
}
