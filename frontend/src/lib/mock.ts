import type { AnalysisResult, Device, Metric, Scale, SessionSummary } from "./types";

const BETTER: Record<string, "high" | "low" | null> = {
  cpps: "high", hnr: "high", jitter: "low", shimmer: "low",
};

// pywebview 백엔드가 없을 때(브라우저 단독 개발/스크린샷용) 쓰는 목 데이터.

export const mockInputs: Device[] = [
  { index: 0, label: "Focusrite Scarlett 2i2 [WASAPI]" },
  { index: 1, label: "내장 마이크 [WASAPI]" },
];
export const mockOutputs: Device[] = [
  { index: 2, label: "Built-in Output [WASAPI]" },
  { index: 3, label: "Headphones [WASAPI]" },
];

export const mockScales: Scale[] = [
  { key: "five_tone", name: "5-tone 스케일", syllable: "마/아 (ma)", glide: false, solfege: "도 레 미 파 솔 파 미 레 도", description: "도레미파솔파미레도. 가장 기본적인 음정 워밍업. 반음씩 올려가며 반복." },
  { key: "major_octave", name: "메이저 스케일 (옥타브)", syllable: "아 (ah)", glide: false, solfege: "도 레 미 파 솔 라 시 도˙ …", description: "한 옥타브 전체를 오르내린다." },
  { key: "major_triad", name: "아르페지오 (3화음)", syllable: "마/모 (mo)", glide: false, solfege: "도 미 솔 도˙ 솔 미 도", description: "화음 음정 감각과 음역 확장에 좋다." },
  { key: "staccato_arp", name: "스타카토 아르페지오", syllable: "하/헤 (he)", glide: false, solfege: "도 미 솔 미 도", description: "짧게 끊어서. 성대 민첩성·온셋 훈련." },
  { key: "sustained_vowel", name: "지속 모음 (롱톤)", syllable: "아 (ah)", glide: false, solfege: "도", description: "한 음을 길게. CPP·지터·쉬머·HNR 측정에 최적." },
  { key: "siren", name: "사이렌 (글라이드)", syllable: "응 (ng)", glide: true, solfege: "글라이드 ↗↘", description: "끊지 않고 한 옥타브 오르내리며 미끄러뜨린다." },
];

function mk(
  key: string, label: string, value: number | null, unit: string,
  category: string, description: string, normal = "",
  status: Metric["status"] = "info", note = "",
): Metric {
  return {
    key, label, value, unit, category, description, normal, status, note,
    better: BETTER[key] ?? null,
    display: value === null ? "—" : value.toFixed(2),
    reference: { title: `${label} 출처`, citation: "", url: "https://doi.org/10.0000/example", summary: description },
  };
}

export const mockSessions: SessionSummary[] = [
  { id: "20260615-0840-aa", created_at: "2026-06-15T08:40:00", label: "워밍업 후", duration: 1.6, cpps: 8.91, cpps_status: "good" },
  { id: "20260615-0815-bb", created_at: "2026-06-15T08:15:00", label: "워밍업 전", duration: 1.5, cpps: 5.2, cpps_status: "watch" },
  { id: "20260614-2110-cc", created_at: "2026-06-14T21:10:00", label: "", duration: 2.1, cpps: 7.0, cpps_status: "good" },
];

export const mockMetrics: Metric[] = [
  mk("cpps", "CPPS", 8.91, "dB", "음질", "켑스트럼 피크 두드러짐 — 높을수록 또렷한 발성.", "≥ 4 dB 권장", "good", "또렷하고 안정적인 발성"),
  mk("hnr", "HNR", 23.4, "dB", "음질", "배음 대비 잡음 비. 높을수록 깨끗.", "≥ 20 dB", "good", "깨끗한 발성(잡음 적음)"),
  mk("jitter", "Jitter", 1.31, "%", "음질", "주기 간 주파수 섭동.", "< 1%", "watch", "약간 불안정"),
  mk("shimmer", "Shimmer", 3.12, "%", "음질", "주기 간 진폭 섭동.", "< 3.8%", "good", "음량(진폭) 안정적"),
  mk("f0_mean", "평균 F0", 220.5, "Hz", "음높이", "기본 주파수의 평균."),
  mk("f0_sd", "F0 표준편차", 7.4, "Hz", "음높이", "음높이의 흔들림."),
  mk("f1", "F1", 551.9, "Hz", "공명·음색", "제1 포먼트 — 개구도."),
  mk("f2", "F2", 1623.0, "Hz", "공명·음색", "제2 포먼트 — 혀 전후."),
  mk("f3", "F3", 2998.2, "Hz", "공명·음색", "제3 포먼트 — 음색."),
  mk("alpha", "Alpha ratio", -11.3, "dB", "공명·음색", "고역 대 저역 에너지 비."),
  mk("hammarberg", "Hammarberg", 10.6, "dB", "공명·음색", "저역 대 고역 피크 차."),
  mk("spr", "SPR", 9.4, "dB", "공명·음색", "Singer's Formant 지표."),
  mk("vibrato_rate", "비브라토 rate", 5.5, "Hz", "비브라토", "비브라토 주기.", "4–7 Hz", "good", "자연스러운 비브라토 주기"),
  mk("vibrato_extent", "비브라토 extent", 1.18, "반음", "비브라토", "비브라토 폭.", "0.5–2 반음", "good", "적당한 비브라토 폭"),
];

export function mockWaveform(n = 600): number[] {
  const out: number[] = [];
  for (let i = 0; i < n; i++) {
    const t = i / n;
    const env = Math.sin(Math.PI * t); // 페이드 인/아웃
    const vib = 0.5 + 0.5 * Math.abs(Math.sin(2 * Math.PI * 5.5 * t * 6));
    out.push(Math.min(1, env * vib)); // 0..1 진폭 엔벨로프
  }
  return out;
}

export function mockSpectrogram(freqBins = 96, timeBins = 200): number[][] {
  const m: number[][] = [];
  for (let f = 0; f < freqBins; f++) {
    const row: number[] = [];
    const harmonic = [8, 16, 24, 40].some((h) => Math.abs(f - h) < 2);
    for (let t = 0; t < timeBins; t++) {
      const base = harmonic ? 0.85 : 0.12;
      const noise = Math.random() * 0.18;
      const decay = Math.exp(-f / 60);
      row.push(Math.min(1, base * decay + noise * 0.4));
    }
    m.push(row);
  }
  return m;
}

// 실시간 스펙트럼(EQ 곡선) 목 — 로그 주파수 + 포먼트형 피크 + 롤오프
export function mockSpectrum(n = 180): { freqs: number[]; db: number[] } {
  const fmin = 50, fmax = 16000;
  const freqs: number[] = [];
  const db: number[] = [];
  const peaks = [
    [220, 0], [620, -6], [1100, -10], [2900, -14], // F0 + 포먼트 + 링
  ];
  for (let i = 0; i < n; i++) {
    const f = fmin * Math.pow(fmax / fmin, i / (n - 1));
    let v = -60 - 6 * Math.log2(f / 200); // 전체 롤오프
    for (const [pf, pgain] of peaks) {
      v = Math.max(v, pgain - 0.0009 * Math.pow(f - pf, 2) / (pf / 200));
    }
    v += (Math.random() - 0.5) * 3;
    freqs.push(Math.round(f));
    db.push(Math.max(-90, Math.min(0, Math.round(v * 10) / 10)));
  }
  return { freqs, db };
}

export const mockAnalysis: AnalysisResult = {
  duration: 1.6,
  waveform: mockWaveform(),
  spectrogram: mockSpectrogram(),
  metrics: mockMetrics,
};

// "워밍업 전" 변형 — 더 낮은 CPPS/HNR, 더 높은 jitter/shimmer (비교 데모용)
const beforeAdjust: Record<string, number> = {
  cpps: 5.2, hnr: 16.8, jitter: 2.1, shimmer: 5.4,
};
export const mockAnalysisBefore: AnalysisResult = {
  duration: 1.5,
  waveform: mockWaveform(),
  spectrogram: mockSpectrogram(),
  metrics: mockMetrics.map((m) =>
    m.key in beforeAdjust ? { ...m, value: beforeAdjust[m.key] } : m
  ),
};
