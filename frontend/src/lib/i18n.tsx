import { createContext, useCallback, useContext, useState, type ReactNode } from "react";

export type Lang = "ko" | "en";

const STORAGE = "vocelab.lang";
const STORAGE_ONBOARDED = "vocelab.onboarded";

function readOnboarded(): boolean {
  try {
    return localStorage.getItem(STORAGE_ONBOARDED) === "1";
  } catch {
    return false;
  }
}

export function detectLang(): Lang {
  try {
    const saved = localStorage.getItem(STORAGE);
    if (saved === "ko" || saved === "en") return saved;
  } catch {
    /* ignore */
  }
  const nav = (typeof navigator !== "undefined" && navigator.language) || "en";
  return nav.toLowerCase().startsWith("ko") ? "ko" : "en";
}

// UI 크롬 문자열. {var} 는 t(key, {var}) 로 치환.
const DICT: Record<string, { ko: string; en: string }> = {
  "donate": { ko: "후원", en: "Donate" },
  "donate.title": { ko: "개발자에게 커피 한 잔 ☕", en: "Buy the developer a coffee ☕" },
  "device.refresh": { ko: "장치 새로고침", en: "Refresh devices" },

  // Header / Settings
  "header.settings": { ko: "설정", en: "Settings" },
  "settings.title": { ko: "설정", en: "Settings" },
  "settings.language": { ko: "언어", en: "Language" },
  "settings.input": { ko: "입력 장치 (마이크)", en: "Input (microphone)" },
  "settings.output": { ko: "출력 장치 (스피커)", en: "Output (speaker)" },
  "settings.theme": { ko: "테마", en: "Theme" },
  "settings.theme.dark": { ko: "다크", en: "Dark" },
  "settings.done": { ko: "완료", en: "Done" },

  // Welcome (first run)
  "welcome.greeting": { ko: "VoceLab에 오신 걸 환영해요", en: "Welcome to VoceLab" },
  "welcome.subtitle": {
    ko: "녹음하고 바로 듣고, Praat 기반 음향 지표로 발성을 확인하세요.",
    en: "Record, play back instantly, and check your voice with Praat-based metrics.",
  },
  "welcome.lang": { ko: "언어 / Language", en: "Language / 언어" },
  "welcome.device": { ko: "입력 장치 (마이크)", en: "Input device (microphone)" },
  "welcome.device.none": {
    ko: "장치를 찾는 중… 나중에 설정에서 선택할 수 있어요.",
    en: "Looking for devices… you can pick one later in Settings.",
  },
  "welcome.start": { ko: "시작하기", en: "Get started" },

  // Status bar
  "statusbar.noDevice": { ko: "장치 없음", en: "No device" },

  // Transport
  "transport.record": { ko: "녹음", en: "Record" },
  "transport.recording": { ko: "녹음 중…", en: "Recording…" },
  "transport.play": { ko: "재생", en: "Play" },
  "transport.stop": { ko: "정지", en: "Stop" },
  "transport.loop": { ko: "반복 재생", en: "Loop" },
  "transport.loop.title": {
    ko: "켜면 녹음을 멈추는 즉시 방금 녹음을 반복 재생합니다.",
    en: "When on, the take loops as soon as you stop recording.",
  },
  "transport.record.start.title": { ko: "녹음 시작 (Space)", en: "Start recording (Space)" },
  "transport.record.stop.title": { ko: "녹음 정지", en: "Stop recording" },
  "transport.play.title": { ko: "방금 녹음 재생", en: "Play the take" },

  // Panels
  "panel.waveform": { ko: "파형", en: "Waveform" },
  "panel.spectrum": { ko: "실시간 스펙트럼", en: "Live spectrum" },
  "panel.pitch": { ko: "실시간 음정", en: "Live pitch" },
  "panel.history": { ko: "기록", en: "History" },
  "panel.scales": { ko: "스케일 연습", en: "Scale practice" },

  "spectrum.freeze": { ko: "프리즈", en: "Freeze" },
  "spectrum.resume": { ko: "재개", en: "Resume" },
  "spectrum.frozen": { ko: "프리즈됨", en: "Frozen" },
  "spectrum.freeze.title": { ko: "현재 곡선을 멈춰서 고정", en: "Freeze the current curve" },
  "spectrum.empty": {
    ko: "입력 신호를 기다리는 중… (소리를 내보세요)",
    en: "Waiting for input… (make a sound)",
  },

  "waveform.empty": {
    ko: "녹음하면 파형이 표시됩니다 · 클릭으로 재생 위치 선택",
    en: "Record to see the waveform · click to set the playback point",
  },
  "waveform.seek.title": { ko: "클릭한 위치부터 재생", en: "Play from the clicked point" },

  "pitch.empty": { ko: "소리를 내면 음정이 표시됩니다 ♪", en: "Make a sound to see pitch ♪" },
  "pitch.cents": { ko: "센트", en: "cents" },

  // Metrics
  "metrics.empty": {
    ko: "녹음하면 핵심 음향 지표(CPPS · HNR · 지터 · 쉬머)가 표시됩니다.",
    en: "Record to see core metrics (CPPS · HNR · Jitter · Shimmer).",
  },
  "metrics.normal": { ko: "정상/참고", en: "Normal/ref" },
  "status.good": { ko: "양호", en: "Good" },
  "status.watch": { ko: "주의", en: "Watch" },
  "status.poor": { ko: "개선 필요", en: "Needs work" },
  "status.info": { ko: "정보", en: "Info" },

  // Scale practice
  "scales.guide": { ko: "가이드 톤", en: "Guide tone" },
  "scales.syllable": { ko: "음절", en: "Syllable" },
  "scales.transpose.down": { ko: "반음 내림", en: "Down a semitone" },
  "scales.transpose.up": { ko: "반음 올림", en: "Up a semitone" },
  "scales.glide": { ko: "글라이드 ↗↘", en: "Glide ↗↘" },

  // Session bar
  "history.baselineHint": { ko: "★=비교 기준", en: "★=baseline" },
  "history.empty": {
    ko: "녹음하면 자동으로 여기에 저장됩니다.",
    en: "Recordings are saved here automatically.",
  },
  "history.untitled": { ko: "무제", en: "Untitled" },
  "history.play": { ko: "재생", en: "Play" },
  "history.baseline": { ko: "비교 기준 설정", en: "Set as baseline" },
  "history.delete": { ko: "삭제", en: "Delete" },

  // Status line
  "st.idle": {
    ko: "오디오 인터페이스를 선택하고 녹음을 시작하세요.",
    en: "Pick an audio interface and start recording.",
  },
  "st.ready": {
    ko: "준비됨 — 오디오 인터페이스를 선택하고 녹음을 시작하세요.",
    en: "Ready — pick an audio interface and start recording.",
  },
  "st.recording": { ko: "● 녹음 중입니다. 발성하세요.", en: "● Recording. Sing/speak now." },
  "st.analyzing": { ko: "녹음 완료 ({s}s). 분석 중…", en: "Recorded ({s}s). Analyzing…" },
  "st.loop": {
    ko: "녹음 완료 ({s}s). 🔁 반복 재생 중 — ■ 로 멈춤",
    en: "Recorded ({s}s). 🔁 Looping — ■ to stop",
  },
  "st.done": {
    ko: "녹음 완료 ({s}s). 파형을 클릭하거나 ▶로 재생하세요.",
    en: "Recorded ({s}s). Click the waveform or ▶ to play.",
  },
  "st.demo": {
    ko: "데모 모드 — 목 데이터 (백엔드 미연결)",
    en: "Demo mode — mock data (backend not connected)",
  },
  "st.seed": { ko: "녹음 완료 ({s}s) — 실 분석 데이터", en: "Recorded ({s}s) — real analysis data" },
  "st.loaded": {
    ko: "기록 불러옴 — 파형을 클릭하거나 ▶로 재생하세요.",
    en: "Loaded a take — click the waveform or ▶ to play.",
  },
  "st.playingLoop": { ko: "🔁 반복 재생 중 — ■ 로 멈춤", en: "🔁 Looping — ■ to stop" },
  "st.playing": { ko: "재생 중…", en: "Playing…" },
};

interface Ctx {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: string, vars?: Record<string, string | number>) => string;
  onboarded: boolean;
  completeOnboarding: () => void;
}

const I18nContext = createContext<Ctx>({
  lang: "en",
  setLang: () => {},
  t: (k) => k,
  onboarded: true,
  completeOnboarding: () => {},
});

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(detectLang);
  const [onboarded, setOnboarded] = useState<boolean>(readOnboarded);
  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    try {
      localStorage.setItem(STORAGE, l);
    } catch {
      /* ignore */
    }
  }, []);
  const completeOnboarding = useCallback(() => {
    setOnboarded(true);
    try {
      localStorage.setItem(STORAGE_ONBOARDED, "1");
    } catch {
      /* ignore */
    }
  }, []);
  const t = useCallback(
    (key: string, vars?: Record<string, string | number>) => {
      let s = DICT[key]?.[lang] ?? key;
      if (vars) for (const [k, v] of Object.entries(vars)) s = s.replace(`{${k}}`, String(v));
      return s;
    },
    [lang]
  );
  return (
    <I18nContext.Provider value={{ lang, setLang, t, onboarded, completeOnboarding }}>
      {children}
    </I18nContext.Provider>
  );
}

export const useI18n = () => useContext(I18nContext);
