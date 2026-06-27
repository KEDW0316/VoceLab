import { useCallback, useEffect, useRef, useState } from "react";
import { AudioLines } from "lucide-react";
import type { AnalysisResult, SessionSummary } from "@/lib/types";
import { api, whenBackendReady } from "@/lib/api";
import { mockAnalysis } from "@/lib/mock";
import { loadPref, savePref } from "@/lib/storage";
import { useI18n } from "@/lib/i18n";
import { useDevices } from "@/lib/useDevices";
import { Panel } from "@/components/ui/panel";
import { Header } from "@/components/Header";
import { StatusBar } from "@/components/StatusBar";
import { Settings } from "@/components/Settings";
import { Welcome } from "@/components/Welcome";
import { Waveform } from "@/components/Waveform";
import { SpectrumPanel } from "@/components/SpectrumPanel";
import { MetricsPanel } from "@/components/MetricsPanel";
import { ScalePractice } from "@/components/ScalePractice";
import { SessionBar } from "@/components/SessionBar";
import { Transport } from "@/components/Transport";
import { PitchView } from "@/components/PitchView";

function toBaselineMap(r: AnalysisResult): Record<string, number | null> {
  return Object.fromEntries(r.metrics.map((m) => [m.key, m.value]));
}

// 상태줄: 번역 키 + 보간 변수를 보관 → 언어 토글 시 자동으로 다시 번역됨
type Status = { key: string; vars?: Record<string, string | number> };

export default function App() {
  const { t, onboarded, completeOnboarding } = useI18n();
  const devices = useDevices();
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [recording, setRecording] = useState(false);
  const [feedback, setFeedback] = useState(() => loadPref("feedback") === "1");
  const [level, setLevel] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [status, setStatus] = useState<Status>({ key: "st.idle" });
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

  // 백엔드(pywebview) 준비를 기다린 뒤 한 번만 판단한다.
  // 실제 백엔드면 빈 화면에서 시작(데모 데이터 X), 진짜 브라우저면 데모/시드 표시.
  useEffect(() => {
    whenBackendReady().then((real) => {
      refreshSessions();
      if (real) {
        setStatus({ key: "st.ready" });
        return;
      }
      const seed = (window as unknown as { __VOCELAB_SEED__?: AnalysisResult }).__VOCELAB_SEED__;
      setResult(seed ?? mockAnalysis);
      setStatus(seed ? { key: "st.seed", vars: { s: seed.duration.toFixed(1) } } : { key: "st.demo" });
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
      await api.start_recording(devices.inputIdx);
      setRecording(true);
      setStatus({ key: "st.recording" });
      pollLevel();
    } else {
      stopTimers();
      setRecording(false);
      // 1) 정지 즉시 가벼운 결과(길이·파형) → 바로 재생 (분석을 기다리지 않음)
      const quick = await api.stop_recording();
      setResult(quick);
      setCurrentId(null);
      setPlayhead(0);
      if (feedback) {
        api.play(true, 0); // 방금 녹음(last_recording) 즉시 반복재생
        setPlaying(true);
      } else {
        setPlaying(false);
      }
      setStatus({ key: "st.analyzing", vars: { s: quick.duration.toFixed(1) } });
      // 2) 무거운 분석/저장은 백그라운드 — 끝나면 지표·기록 채움
      api.analyze_current().then((full) => {
        setResult(full);
        setCurrentId(full.session_id ?? null);
        refreshSessions();
        setStatus({
          key: feedback ? "st.loop" : "st.done",
          vars: { s: full.duration.toFixed(1) },
        });
      });
    }
  }, [recording, devices.inputIdx, feedback, pollLevel, refreshSessions, stopPlay]);

  // 세션 핸들러
  const loadSession = async (id: string) => {
    const res = await api.get_session(id);
    if (res) {
      stopPlay();
      setResult(res);
      setCurrentId(id);
      setPlayhead(0);
      setStatus({ key: "st.loaded" });
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
    <div className="flex h-screen flex-col">
      <Header onOpenSettings={() => setSettingsOpen(true)} />

      {/* 2단: 좌(시각화) / 우(컨트롤·연습·기록) */}
      <main className="vl-enter grid min-h-0 flex-1 grid-cols-[1fr_minmax(320px,360px)] gap-2 p-3">
        {/* 좌측 — 파형(컴팩트) + 스펙트럼(세로로 길게) + 핵심 지표 */}
        <div className="flex min-h-0 flex-col gap-2">
          <Panel
            title={t("panel.waveform")}
            icon={<AudioLines className="h-3.5 w-3.5" />}
            right={result ? `${result.duration.toFixed(1)}s` : undefined}
            className="h-[84px] shrink-0"
            bodyClassName="p-1.5"
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
          <SpectrumPanel inputIdx={devices.inputIdx} recording={recording} />
          <MetricsPanel metrics={result?.metrics ?? []} baseline={baseline} />
        </div>

        {/* 우측 — 녹음/재생, 스케일 연습, 기록 */}
        <div className="flex min-h-0 flex-col gap-2 overflow-y-auto">
          <Transport
            recording={recording}
            playing={playing}
            canPlay={!!result}
            feedback={feedback}
            level={level}
            elapsed={elapsed}
            onRecordToggle={onRecordToggle}
            onPlay={() => playFrom(playhead)}
            onStop={stopPlay}
            onFeedbackChange={setFeedback}
          />
          <ScalePractice />
          <SessionBar
            sessions={sessions}
            currentId={currentId}
            baselineId={baselineId}
            onLoad={loadSession}
            onPlay={(id) => api.play_session(id, feedback)}
            onDelete={deleteSession}
            onSetBaseline={setBaselineSession}
          />
          {/* 남는 공간에 큰 실시간 음정 */}
          <PitchView />
        </div>
      </main>

      <StatusBar
        inputLabel={devices.inputLabel}
        outputLabel={devices.outputLabel}
        status={t(status.key, status.vars)}
        recording={recording}
        onOpenSettings={() => setSettingsOpen(true)}
      />

      <Settings open={settingsOpen} onClose={() => setSettingsOpen(false)} devices={devices} />
      {!onboarded && <Welcome devices={devices} onDone={completeOnboarding} />}
    </div>
  );
}
