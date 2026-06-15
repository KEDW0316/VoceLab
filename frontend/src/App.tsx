import { useCallback, useEffect, useRef, useState } from "react";
import { AudioLines } from "lucide-react";
import type { AnalysisResult, SessionSummary } from "@/lib/types";
import { api, whenBackendReady } from "@/lib/api";
import { mockAnalysis } from "@/lib/mock";
import { loadPref, savePref } from "@/lib/storage";
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
  const [feedback, setFeedback] = useState(() => loadPref("feedback") === "1");
  const [level, setLevel] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [status, setStatus] = useState("오디오 인터페이스를 선택하고 녹음을 시작하세요.");
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [currentId, setCurrentId] = useState<string | null>(null);
  const [baselineId, setBaselineId] = useState<string | null>(null);
  const [baseline, setBaseline] = useState<Record<string, number | null> | null>(null);
  const [playing, setPlaying] = useState(false);
  const [playhead, setPlayhead] = useState(0); // 재생 시작 위치(초)
  const levelTimer = useRef<number | null>(null);
  const elapsedTimer = useRef<number | null>(null);
  const playTimer = useRef<number | null>(null);

  // 현재 표시 중인 오디오를 start(초)부터 재생. 녹음/세션 모두 currentId로 통일.
  const playFrom = useCallback(
    (sec: number) => {
      const dur = result?.duration ?? 0;
      setPlayhead(sec);
      if (currentId) api.play_session(currentId, feedback, sec);
      else api.play(feedback, sec);
      setPlaying(true);
      if (playTimer.current) window.clearTimeout(playTimer.current);
      if (!feedback && dur > 0) {
        playTimer.current = window.setTimeout(() => setPlaying(false), (dur - sec) * 1000 + 150);
      }
    },
    [result, currentId, feedback]
  );

  const stopPlay = useCallback(() => {
    api.stop_playback();
    setPlaying(false);
    if (playTimer.current) window.clearTimeout(playTimer.current);
  }, []);

  const refreshSessions = useCallback(() => {
    api.list_sessions().then(setSessions);
  }, []);

  // 피드백 모드 기억
  useEffect(() => {
    savePref("feedback", feedback ? "1" : "0");
  }, [feedback]);

  useEffect(() => {
    api.set_output_device(outputIdx);
  }, [outputIdx]);

  // 백엔드(pywebview) 준비를 기다린 뒤 한 번만 판단한다.
  // 실제 백엔드면 빈 화면에서 시작(데모 데이터 X), 진짜 브라우저면 데모/시드 표시.
  useEffect(() => {
    whenBackendReady().then((real) => {
      refreshSessions();
      if (real) {
        setStatus("준비됨 — 오디오 인터페이스를 선택하고 녹음을 시작하세요.");
        return;
      }
      const seed = (window as unknown as { __VOCELAB_SEED__?: AnalysisResult }).__VOCELAB_SEED__;
      setResult(seed ?? mockAnalysis);
      setStatus(seed ? `녹음 완료 (${seed.duration.toFixed(1)}s) — 실 분석 데이터` : "데모 모드 — 목 데이터 (백엔드 미연결)");
    });
  }, [refreshSessions]);

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
      stopPlay();
      setPlayhead(0);
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
      setPlayhead(0);
      refreshSessions();
      if (feedback) {
        if (res.session_id) api.play_session(res.session_id, true, 0);
        else api.play(true, 0);
        setPlaying(true);
        setStatus(`녹음 완료 (${res.duration.toFixed(1)}s). 🔁 반복 재생 중 — ■ 로 멈춤`);
      } else {
        setPlaying(false);
        setStatus(`녹음 완료 (${res.duration.toFixed(1)}s). 파형을 클릭하거나 ▶로 재생하세요.`);
      }
    }
  }, [recording, inputIdx, feedback, pollLevel, refreshSessions, stopPlay]);

  // 세션 핸들러
  const loadSession = async (id: string) => {
    const res = await api.get_session(id);
    if (res) {
      stopPlay();
      setResult(res);
      setCurrentId(id);
      setPlayhead(0);
      setStatus("기록 불러옴 — 파형을 클릭하거나 ▶로 재생하세요.");
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
            <Waveform
              data={result?.waveform ?? []}
              duration={result?.duration ?? 0}
              startSec={playhead}
              playing={playing}
              loop={feedback}
              onSeek={playFrom}
            />
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
        onPlay={() => playFrom(playhead)}
        onStop={stopPlay}
        onFeedbackChange={setFeedback}
      />
    </div>
  );
}
