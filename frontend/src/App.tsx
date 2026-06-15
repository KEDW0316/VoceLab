import { useCallback, useEffect, useRef, useState } from "react";
import { Activity } from "lucide-react";
import type { AnalysisResult } from "@/lib/types";
import { api, isBackendReady } from "@/lib/api";
import { mockAnalysis } from "@/lib/mock";
import { Card } from "@/components/ui/card";
import { DeviceBar } from "@/components/DeviceBar";
import { Waveform } from "@/components/Waveform";
import { Spectrogram } from "@/components/Spectrogram";
import { MetricsPanel } from "@/components/MetricsPanel";
import { ScalePractice } from "@/components/ScalePractice";
import { Transport } from "@/components/Transport";

export default function App() {
  const [inputIdx, setInputIdx] = useState<number | null>(null);
  const [outputIdx, setOutputIdx] = useState<number | null>(null);
  const [recording, setRecording] = useState(false);
  const [feedback, setFeedback] = useState(false);
  const [level, setLevel] = useState(0);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [status, setStatus] = useState("오디오 인터페이스를 선택하고 녹음을 시작하세요.");
  const levelTimer = useRef<number | null>(null);

  // outputIdx는 백엔드 재생 시 사용 — 참조 유지
  useEffect(() => void outputIdx, [outputIdx]);

  // 백엔드(pywebview)가 없는 브라우저/데모 모드에서는 목 분석 결과로 미리 채운다.
  useEffect(() => {
    if (!isBackendReady()) {
      setResult(mockAnalysis);
      setStatus("데모 모드 — 목 데이터 표시 중 (백엔드 미연결)");
    }
  }, []);

  const pollLevel = useCallback(() => {
    levelTimer.current = window.setInterval(async () => {
      setLevel(await api.get_level());
    }, 60);
  }, []);

  const stopPolling = () => {
    if (levelTimer.current) window.clearInterval(levelTimer.current);
    levelTimer.current = null;
    setLevel(0);
  };

  const onRecordToggle = async () => {
    if (!recording) {
      await api.start_recording(inputIdx);
      setRecording(true);
      setStatus("녹음 중입니다. 발성하세요.");
      pollLevel();
    } else {
      stopPolling();
      setRecording(false);
      setStatus("분석 중…");
      const res = await api.stop_recording();
      setResult(res);
      if (feedback) {
        await api.play(true);
        setStatus(`녹음 완료 (${res.duration.toFixed(1)}s). 🔁 반복 재생 중 — 정지로 멈춤`);
      } else {
        setStatus(`녹음 완료 (${res.duration.toFixed(1)}s). ▶ 재생으로 바로 들어보세요.`);
      }
    }
  };

  return (
    <div className="flex h-screen flex-col gap-3 bg-background p-3">
      {/* 헤더 */}
      <header className="flex items-center gap-2">
        <Activity className="h-5 w-5 text-primary" />
        <h1 className="text-lg font-bold tracking-tight">VoceLab</h1>
        <span className="text-xs text-muted-foreground">보컬 트레이닝 보조</span>
      </header>

      <DeviceBar onInputChange={setInputIdx} onOutputChange={setOutputIdx} />

      {/* 메인: 좌(파형+스펙트로그램) / 우(지표) */}
      <div className="grid min-h-0 flex-1 grid-cols-[1fr_300px] gap-3">
        <div className="flex min-h-0 flex-col gap-3">
          <Card className="h-[34%] overflow-hidden p-2">
            <Waveform data={result?.waveform ?? []} duration={result?.duration ?? 0} />
          </Card>
          <Card className="min-h-0 flex-1 overflow-hidden p-0">
            <Spectrogram data={result?.spectrogram ?? []} />
          </Card>
        </div>
        <MetricsPanel metrics={result?.metrics ?? []} />
      </div>

      <ScalePractice />

      <Transport
        recording={recording}
        canPlay={!!result}
        feedback={feedback}
        level={level}
        onRecordToggle={onRecordToggle}
        onPlay={() => api.play(feedback)}
        onStop={() => api.stop_playback()}
        onFeedbackChange={setFeedback}
      />

      <footer className="text-center text-xs text-muted-foreground">{status}</footer>
    </div>
  );
}
