import { useEffect, useState } from "react";
import { ChevronDown, ChevronUp, Music2, Play } from "lucide-react";
import type { Scale } from "@/lib/types";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";

const NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
const TONICS = [3, 4, 5].flatMap((o) =>
  NOTES.filter((n) => !(o === 5 && n !== "C")).map((n) => `${n}${o}`)
);

export function ScalePractice() {
  const [scales, setScales] = useState<Scale[]>([]);
  const [scaleKey, setScaleKey] = useState("");
  const [tonic, setTonic] = useState("C4");
  const [solfege, setSolfege] = useState("");

  useEffect(() => {
    api.list_scales().then((s) => {
      setScales(s);
      if (s.length) setScaleKey(s[0].key);
    });
  }, []);

  const scale = scales.find((s) => s.key === scaleKey);

  useEffect(() => {
    if (scaleKey) api.solfege_for(scaleKey, tonic).then(setSolfege);
  }, [scaleKey, tonic]);

  const transpose = (d: number) => {
    const i = TONICS.indexOf(tonic) + d;
    if (i >= 0 && i < TONICS.length) setTonic(TONICS[i]);
  };

  return (
    <div className="rounded-lg border border-border bg-card p-3">
      <div className="flex flex-wrap items-center gap-2">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground">
          <Music2 className="h-4 w-4 text-accent" />
          스케일 연습
        </div>

        <div className="min-w-[180px] flex-1">
          <Select value={scaleKey} onChange={(e) => setScaleKey(e.target.value)}>
            {scales.map((s) => (
              <option key={s.key} value={s.key}>
                {s.name}
              </option>
            ))}
          </Select>
        </div>

        {/* 키 트랜스포즈 */}
        <div className="flex items-center gap-1 rounded-md border border-border bg-secondary/40 p-1">
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => transpose(-1)} title="반음 내림">
            <ChevronDown className="h-4 w-4" />
          </Button>
          <span className="num w-9 text-center text-sm font-semibold text-primary">{tonic}</span>
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => transpose(1)} title="반음 올림">
            <ChevronUp className="h-4 w-4" />
          </Button>
        </div>

        <Button onClick={() => api.play_guide_tone(scaleKey, tonic)}>
          <Play className="h-4 w-4" /> 가이드 톤
        </Button>
      </div>

      {scale && (
        <div className="mt-2.5 flex flex-wrap items-center gap-x-3 gap-y-1.5">
          {/* 솔페지 pill */}
          <div className="flex flex-wrap items-center gap-1">
            {scale.glide ? (
              <span className="rounded bg-secondary px-2 py-0.5 text-xs text-primary">글라이드 ↗↘</span>
            ) : (
              solfege.split(" ").filter(Boolean).map((n, i) => (
                <span
                  key={i}
                  className="num rounded bg-secondary px-1.5 py-0.5 text-xs text-primary"
                >
                  {n}
                </span>
              ))
            )}
          </div>
          <span className="rounded-full border border-border px-2 py-0.5 text-[10px] text-muted-foreground">
            음절 {scale.syllable}
          </span>
          <p className="text-xs text-muted-foreground">{scale.description}</p>
        </div>
      )}
    </div>
  );
}
