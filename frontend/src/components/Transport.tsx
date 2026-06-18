import { Circle, Play, Square, RotateCcw } from "lucide-react";
import { LevelMeter } from "./LevelMeter";

interface Props {
  recording: boolean;
  playing: boolean;
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
  recording, playing, canPlay, feedback, level, elapsed,
  onRecordToggle, onPlay, onStop, onFeedbackChange,
}: Props) {
  return (
    <div className="vl-card px-4 py-3">
      {/* 입력 레벨미터 */}
      <div className="mb-3 flex items-center gap-2">
        <span className="text-[11px] uppercase tracking-wide text-muted-foreground">IN</span>
        <div className="flex-1">
          <LevelMeter level={level} />
        </div>
        {recording && <span className="num text-sm text-danger">{fmt(elapsed)}</span>}
      </div>

      <div className="flex items-center justify-center gap-6">
        {/* 녹음 (가장 큼) */}
        <div className="flex flex-col items-center gap-1.5">
          <button
            onClick={onRecordToggle}
            className={`flex h-20 w-20 items-center justify-center rounded-full border-2 transition-all active:scale-95 ${
              recording
                ? "border-danger bg-danger/20"
                : "border-danger/70 bg-danger/90 hover:bg-danger"
            }`}
            title={recording ? "녹음 정지" : "녹음 시작 (Space)"}
          >
            {recording ? (
              <Square className="h-7 w-7 fill-danger text-danger" />
            ) : (
              <Circle className="h-9 w-9 fill-white text-white" />
            )}
          </button>
          <span className={`text-xs font-medium ${recording ? "text-danger" : "text-foreground"}`}>
            {recording ? "녹음 중…" : "녹음"}
          </span>
        </div>

        {/* 재생 / 정지 토글 */}
        <div className="flex flex-col items-center gap-1.5">
          <button
            onClick={playing ? onStop : onPlay}
            disabled={!canPlay}
            className={`flex h-20 w-20 items-center justify-center rounded-full border-2 transition-all active:scale-95 disabled:opacity-30 ${
              playing
                ? "border-primary bg-primary/20"
                : "border-primary/70 bg-primary/90 text-primary-foreground hover:bg-primary"
            }`}
            title={playing ? "정지" : "방금 녹음 재생"}
          >
            {playing ? (
              <Square className="h-7 w-7 fill-primary text-primary" />
            ) : (
              <Play className="h-9 w-9 fill-current" />
            )}
          </button>
          <span className="text-xs font-medium text-foreground">{playing ? "정지" : "재생"}</span>
        </div>
      </div>

      {/* 피드백 반복재생 (보조 토글) — 별도 줄 */}
      <div className="mt-3 flex justify-center">
        <button
          onClick={() => onFeedbackChange(!feedback)}
          className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs transition-colors ${
            feedback
              ? "bg-primary/10 text-primary"
              : "text-muted-foreground hover:bg-secondary/60"
          }`}
          title="켜면 녹음을 멈추는 즉시 방금 녹음을 반복 재생합니다."
        >
          <RotateCcw className="h-3.5 w-3.5" />
          반복 재생
        </button>
      </div>
    </div>
  );
}
