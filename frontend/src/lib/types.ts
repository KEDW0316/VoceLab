export interface Device {
  index: number;
  label: string;
}

export interface Reference {
  title: string;
  citation: string;
  url: string;
  summary: string;
}

export interface Metric {
  key: string;
  label: string;
  value: number | null;
  display: string;
  unit: string;
  description: string;
  normal: string;
  category: string;
  status: "good" | "watch" | "poor" | "info";
  note: string;
  better: "high" | "low" | null; // 전/후 비교 델타 색칠 방향
  reference: Reference | null;
}

export interface AnalysisResult {
  duration: number;
  waveform: number[]; // 다운샘플된 모노 (-1..1)
  spectrogram?: number[][]; // (lean UI에선 미사용)
  metrics: Metric[];
  session_id?: string | null;
}

export interface SessionSummary {
  id: string;
  created_at: string;
  label: string;
  duration: number;
  cpps: number | null;
  cpps_status: Metric["status"];
}

export interface Scale {
  key: string;
  name: string;
  description: string;
  syllable: string;
  solfege: string;
  glide: boolean;
}

export interface PyApi {
  list_devices(): Promise<{ inputs: Device[]; outputs: Device[] }>;
  set_output_device(index: number | null): Promise<void>;
  start_recording(inputIndex: number | null): Promise<void>;
  stop_recording(): Promise<AnalysisResult>; // 빠른 반환(길이·파형). 지표 X
  analyze_current(): Promise<AnalysisResult>; // 무거운 분석 + 세션 저장(백그라운드)
  get_level(): Promise<number>;
  get_spectrum(): Promise<{ freqs: number[]; db: number[] }>;
  get_pitch(): Promise<{ hz: number | null; note?: string; octave?: number; cents?: number }>;
  start_monitor(inputIndex: number | null): Promise<void>;
  stop_monitor(): Promise<void>;
  play(loop: boolean, start?: number): Promise<void>;
  stop_playback(): Promise<void>;
  list_scales(): Promise<Scale[]>;
  solfege_for(scaleKey: string, tonic: string): Promise<string>;
  play_guide_tone(scaleKey: string, tonic: string): Promise<void>;
  list_sessions(): Promise<SessionSummary[]>;
  get_session(id: string): Promise<AnalysisResult | null>;
  delete_session(id: string): Promise<boolean>;
  label_session(id: string, label: string): Promise<boolean>;
  play_session(id: string, loop: boolean, start?: number): Promise<void>;
}
