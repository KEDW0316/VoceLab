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
  reference: Reference | null;
}

export interface AnalysisResult {
  duration: number;
  waveform: number[]; // 다운샘플된 모노 (-1..1)
  spectrogram: number[][]; // [freq][time], 0..1 정규화
  metrics: Metric[];
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
  stop_recording(): Promise<AnalysisResult>;
  get_level(): Promise<number>;
  play(loop: boolean): Promise<void>;
  stop_playback(): Promise<void>;
  list_scales(): Promise<Scale[]>;
  solfege_for(scaleKey: string, tonic: string): Promise<string>;
  play_guide_tone(scaleKey: string, tonic: string): Promise<void>;
}
