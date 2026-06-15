import { Circle, Play, RotateCcw, Square } from "lucide-react";
import { Button } from "@/components/ui/button";
import { LevelMeter } from "./LevelMeter";

interface Props {
  recording: boolean;
  canPlay: boolean;
  feedback: boolean;
  level: number; // 0..1
  elapsed: number; // 녹음 경과(초)
  onRecordToggle: () => void;
  onPlay: () => void;
  onStop: () => void;
  onFeedbackChange: (v: boolean) => void;
}

function fmt(s: number) {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${m}:${sec.toString().padStart(2, "0")}`;
}

export function Transport({
  recording, canPlay, feedback, level, elapsed,
  onRecordToggle, onPlay, onStop, onFeedbackChange,
}: Props) {
  return (
    <div className="flex items-center gap-4 rounded-lg border border-border bg-card px-4 py-3">
      {/* 녹음 */}
      <Button
        variant={recording ? "destructive" : "default"}
        size="lg"
        onClick={onRecordToggle}
        className="min-w-[140px] shadow-lg shadow-primary/10"
      >
        <Circle className={`h-3.5 w-3.5 fill-current ${recording ? "animate-pulse" : ""}`} />
        {recording ? "정지" : "녹음"}
      </Button>

      {/* 경과 시간 */}
      <span
        className={`num w-14 text-lg ${recording ? "text-danger" : "text-muted-foreground"}`}
      >
        {fmt(elapsed)}
      </span>

      <div className="h-8 w-px bg-border" />

      {/* 재생 트랜스포트 */}
      <Button variant="secondary" onClick={onPlay} disabled={!canPlay}>
        <Play className="h-4 w-4" /> 재생
      </Button>
      <Button variant="outline" size="icon" onClick={onStop} title="정지">
        <Square className="h-4 w-4" />
      </Button>

      {/* 레벨미터 */}
      <div className="flex flex-1 items-center gap-2">
        <span className="text-[11px] uppercase tracking-wide text-muted-foreground">in</span>
        <div className="flex-1">
          <LevelMeter level={level} />
        </div>
      </div>

      {/* 피드백 모드 토글 */}
      <button
        onClick={() => onFeedbackChange(!feedback)}
        className={`flex items-center gap-2 rounded-md border px-3 py-1.5 text-xs transition-colors ${
          feedback
            ? "border-primary/50 bg-primary/10 text-primary"
            : "border-border text-muted-foreground hover:bg-secondary/60"
        }`}
        title="켜면 녹음 정지 즉시 방금 녹음을 반복 재생합니다(귀 훈련)."
      >
        <RotateCcw className="h-3.5 w-3.5" />
        피드백 모드
      </button>
    </div>
  );
}
