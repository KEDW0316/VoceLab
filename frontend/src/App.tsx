import { useCallback, useEffect, useRef, useState } from "react";
import { AudioLines } from "lucide-react";
import type { AnalysisResult, SessionSummary } from "@/lib/types";
import { api, isBackendReady } from "@/lib/api";
import { mockAnalysis } from "@/lib/mock";
import { Panel } from "@/components/ui/panel";
import { Header } from "@/components/Header";
import { DeviceBar } from "@/components/DeviceBar";
import { Waveform } from "@/components/Waveform";
import { VizTabs } from "@/components/VizTabs";
import { MetricsPanel } from "@/components/MetricsPanel";
import { ScalePractice } from "@/components/ScalePractice";
import { SessionBar } from "@/components/SessionBar";
import { Transport } from "@/components/Transport";

function toBaselineMap(r: AnalysisResult): Record<string, number | null> {
  return Object.fromEntries(r.metrics.map((m) => [m.key, m.value]));
}

export default function App() {
  const [inputIdx, setInputIdx] = useState<number | null>(null);
  const [outputIdx, setOutputIdx] = useState<number | null>(null);
  const [recording, setRecording] = useState(false);
  const [feedback, setFeedback] = useState(false);
  const [level, setLevel] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [status, setStatus] = useState("오디오 인터페이스를 선택하고 녹음을 시작하세요.");
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [currentId, setCurrentId] = useState<string | null>(null);
  const [baselineId, setBaselineId] = useState<string | null>(null);
  const [baseline, setBaseline] = useState<Record<string, number | null> | null>(null);
  const levelTimer = useRef<number | null>(null);
  const elapsedTimer = useRef<number | null>(null);

  const refreshSessions = useCallback(() => {
    api.list_sessions().then(setSessions);
  }, []);
  useEffect(refreshSessions, [refreshSessions]);

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
      setCurrentId(res.session_id ?? null);
      refreshSessions();
      if (feedback) {
        await api.play(true);
        setStatus(`녹음 완료 (${res.duration.toFixed(1)}s). 🔁 반복 재생 중 — ■ 로 멈춤`);
      } else {
        setStatus(`녹음 완료 (${res.duration.toFixed(1)}s). ▶ 재생으로 들어보세요.`);
      }
    }
  }, [recording, inputIdx, feedback, pollLevel, refreshSessions]);

  // 세션 핸들러
  const loadSession = async (id: string) => {
    const res = await api.get_session(id);
    if (res) {
      setResult(res);
      setCurrentId(id);
      setStatus("기록 불러옴 — ▶ 또는 기록의 재생 버튼으로 들어보세요.");
    }
  };
  const deleteSession = async (id: string) => {
    await api.delete_session(id);
    if (baselineId === id) {
      setBaselineId(null);
      setBaseline(null);
    }
    refreshSessions();
  };
  const setBaselineSession = async (id: string) => {
    if (baselineId === id) {
      setBaselineId(null);
      setBaseline(null);
      return;
    }
    const res = await api.get_session(id);
    if (res) {
      setBaselineId(id);
      setBaseline(toBaselineMap(res));
    }
  };

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
          <VizTabs spectrogram={result?.spectrogram ?? []} />
        </div>
        <MetricsPanel metrics={result?.metrics ?? []} baseline={baseline} />
      </div>

      <SessionBar
        sessions={sessions}
        currentId={currentId}
        baselineId={baselineId}
        onLoad={loadSession}
        onPlay={(id) => api.play_session(id, feedback)}
        onDelete={deleteSession}
        onSetBaseline={setBaselineSession}
      />

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
