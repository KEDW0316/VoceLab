import { Circle, Play, Square } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Props {
  recording: boolean;
  canPlay: boolean;
  feedback: boolean;
  level: number; // 0..1
  onRecordToggle: () => void;
  onPlay: () => void;
  onStop: () => void;
  onFeedbackChange: (v: boolean) => void;
}

export function Transport({
  recording, canPlay, feedback, level, onRecordToggle, onPlay, onStop, onFeedbackChange,
}: Props) {
  return (
    <div className="space-y-2">
      {/* 입력 레벨미터 */}
      <div className="flex items-center gap-2">
        <span className="w-16 text-xs text-muted-foreground">입력 레벨</span>
        <div className="h-2 flex-1 overflow-hidden rounded-full bg-secondary">
          <div
            className="h-full rounded-full bg-gradient-to-r from-primary to-accent transition-[width] duration-75"
            style={{ width: `${Math.min(100, level * 100)}%` }}
          />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant={recording ? "destructive" : "default"}
          onClick={onRecordToggle}
          className="min-w-[120px]"
        >
          <Circle className={recording ? "h-3 w-3 animate-pulse fill-current" : "h-3 w-3 fill-current"} />
          {recording ? "녹음 중… 정지" : "녹음"}
        </Button>
        <Button variant="secondary" onClick={onPlay} disabled={!canPlay}>
          <Play className="h-4 w-4" /> 재생
        </Button>
        <Button variant="outline" size="icon" onClick={onStop} title="정지">
          <Square className="h-4 w-4" />
        </Button>

        <label className="ml-auto flex cursor-pointer items-center gap-2 text-xs text-muted-foreground">
          <input
            type="checkbox"
            checked={feedback}
            onChange={(e) => onFeedbackChange(e.target.checked)}
            className="h-4 w-4 accent-[hsl(var(--primary))]"
          />
          피드백 모드 (녹음 후 자동 반복재생)
        </label>
      </div>
    </div>
  );
}
