import { useCallback, useEffect, useRef, useState } from "react";
import { AudioLines, Waves } from "lucide-react";
import type { AnalysisResult } from "@/lib/types";
import { api, isBackendReady } from "@/lib/api";
import { mockAnalysis } from "@/lib/mock";
import { Panel } from "@/components/ui/panel";
import { Header } from "@/components/Header";
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
  const [elapsed, setElapsed] = useState(0);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [status, setStatus] = useState("오디오 인터페이스를 선택하고 녹음을 시작하세요.");
  const levelTimer = useRef<number | null>(null);
  const elapsedTimer = useRef<number | null>(null);

  useEffect(() => {
    api.set_output_device(outputIdx);
  }, [outputIdx]);

  // 백엔드 미연결(브라우저/데모): 주입 시드 또는 목 데이터로 미리 채운다.
  useEffect(() => {
    if (isBackendReady()) return;
    const seed = (window as unknown as { __VOCELAB_SEED__?: AnalysisResult }).__VOCELAB_SEED__;
    setResult(seed ?? mockAnalysis);
    setStatus(seed ? `녹음 완료 (${seed.duration.toFixed(1)}s) — 실 분석 데이터` : "데모 모드 — 목 데이터");
  }, []);

  const pollLevel = useCallback(() => {
    levelTimer.current = window.setInterval(async () => setLevel(await api.get_level()), 60);
    const start = Date.now();
    setElapsed(0);
    elapsedTimer.current = window.setInterval(() => setElapsed((Date.now() - start) / 1000), 100);
  }, []);

  const stopTimers = () => {
    if (levelTimer.current) window.clearInterval(levelTimer.current);
    if (elapsedTimer.current) window.clearInterval(elapsedTimer.current);
    levelTimer.current = elapsedTimer.current = null;
    setLevel(0);
  };

  const onRecordToggle = useCallback(async () => {
    if (!recording) {
      await api.start_recording(inputIdx);
      setRecording(true);
      setStatus("● 녹음 중입니다. 발성하세요.");
      pollLevel();
    } else {
      stopTimers();
      setRecording(false);
      setStatus("분석 중…");
      const res = await api.stop_recording();
      setResult(res);
      if (feedback) {
        await api.play(true);
        setStatus(`녹음 완료 (${res.duration.toFixed(1)}s). 🔁 반복 재생 중 — ■ 로 멈춤`);
      } else {
        setStatus(`녹음 완료 (${res.duration.toFixed(1)}s). ▶ 재생으로 들어보세요.`);
      }
    }
  }, [recording, inputIdx, feedback, pollLevel]);

  // 스페이스바로 녹음 토글 (입력 포커스가 아닐 때)
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName;
      if (e.code === "Space" && tag !== "INPUT" && tag !== "SELECT" && tag !== "TEXTAREA") {
        e.preventDefault();
        onRecordToggle();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onRecordToggle]);

  return (
    <div className="flex h-screen flex-col gap-3 p-4">
      <Header recording={recording} status={status} />
      <DeviceBar onInputChange={setInputIdx} onOutputChange={setOutputIdx} />

      <div className="grid min-h-0 flex-1 grid-cols-[1fr_360px] gap-3">
        <div className="flex min-h-0 flex-col gap-3">
          <Panel
            title="파형"
            icon={<AudioLines className="h-3.5 w-3.5" />}
            right={result ? `${result.duration.toFixed(1)}s` : undefined}
            className="h-[36%]"
            bodyClassName="p-2"
          >
            <Waveform data={result?.waveform ?? []} />
          </Panel>
          <Panel
            title="스펙트로그램"
            icon={<Waves className="h-3.5 w-3.5" />}
            right="0–5 kHz"
            className="min-h-0 flex-1"
          >
            <Spectrogram data={result?.spectrogram ?? []} />
          </Panel>
        </div>
        <MetricsPanel metrics={result?.metrics ?? []} />
      </div>

      <ScalePractice />

      <Transport
        recording={recording}
        canPlay={!!result}
        feedback={feedback}
        level={level}
        elapsed={elapsed}
        onRecordToggle={onRecordToggle}
        onPlay={() => api.play(feedback)}
        onStop={() => api.stop_playback()}
        onFeedbackChange={setFeedback}
      />
    </div>
  );
}
