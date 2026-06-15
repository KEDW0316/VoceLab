import { useEffect, useState } from "react";
import { ChevronDown, ChevronUp, Music, Play } from "lucide-react";
import type { Scale } from "@/lib/types";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

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
    <Card className="p-3">
      <div className="mb-2 flex items-center gap-2">
        <Music className="h-4 w-4 text-accent" />
        <h2 className="text-sm font-semibold">스케일 연습</h2>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <div className="min-w-[200px] flex-1">
          <Select value={scaleKey} onChange={(e) => setScaleKey(e.target.value)}>
            {scales.map((s) => (
              <option key={s.key} value={s.key}>
                {s.name}
              </option>
            ))}
          </Select>
        </div>
        <span className="text-xs text-muted-foreground">키</span>
        <div className="w-20">
          <Select value={tonic} onChange={(e) => setTonic(e.target.value)}>
            {TONICS.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </Select>
        </div>
        <Button variant="outline" size="icon" onClick={() => transpose(-1)} title="반음 내림">
          <ChevronDown className="h-4 w-4" />
        </Button>
        <Button variant="outline" size="icon" onClick={() => transpose(1)} title="반음 올림">
          <ChevronUp className="h-4 w-4" />
        </Button>
        <Button onClick={() => api.play_guide_tone(scaleKey, tonic)}>
          <Play className="h-4 w-4" /> 가이드 톤
        </Button>
      </div>
      {scale && (
        <div className="mt-2 space-y-1">
          <p className="text-xs text-muted-foreground">{scale.description}</p>
          <div className="flex items-center gap-2">
            <Badge>음절 {scale.syllable}</Badge>
            <span className="text-[13px] font-medium text-primary">{solfege}</span>
          </div>
        </div>
      )}
    </Card>
  );
}
