import type { PyApi } from "./types";
import * as mock from "./mock";

declare global {
  interface Window {
    pywebview?: { api: PyApi };
  }
}

// pywebview가 주입한 실제 API가 있으면 사용하고, 없으면(브라우저 단독) 목으로 폴백한다.
const mockApi: PyApi = {
  async list_devices() {
    return { inputs: mock.mockInputs, outputs: mock.mockOutputs };
  },
  async set_output_device() {},
  async start_recording() {},
  async stop_recording() {
    return mock.mockAnalysis;
  },
  async get_level() {
    return 0.4 + Math.random() * 0.3;
  },
  async get_spectrum() {
    return mock.mockSpectrum();
  },
  async get_pitch() {
    return { hz: 220.5, note: "A", octave: 3, cents: 8 };
  },
  async start_monitor() {},
  async stop_monitor() {},
  async play() {},
  async stop_playback() {},
  async list_scales() {
    return mock.mockScales;
  },
  async solfege_for(scaleKey) {
    return mock.mockScales.find((s) => s.key === scaleKey)?.solfege ?? "";
  },
  async play_guide_tone() {},
  async list_sessions() {
    return mock.mockSessions;
  },
  async get_session(id) {
    return id === "20260615-0815-bb" ? mock.mockAnalysisBefore : mock.mockAnalysis;
  },
  async delete_session() {
    return true;
  },
  async label_session() {
    return true;
  },
  async play_session() {},
};

export const isBackendReady = () =>
  typeof window !== "undefined" && !!window.pywebview?.api;

// pywebview는 'pywebviewready' 시점에 api를 주입한다. 마운트 즉시 판단하면
// 백엔드가 있는데도 목 데이터를 깔게 되므로, 준비를 기다린 뒤 한 번만 확정한다.
let _readyPromise: Promise<boolean> | null = null;
export function whenBackendReady(timeoutMs = 2000): Promise<boolean> {
  if (_readyPromise) return _readyPromise;
  _readyPromise = new Promise<boolean>((resolve) => {
    if (isBackendReady()) return resolve(true);
    let done = false;
    const finish = (v: boolean) => {
      if (done) return;
      done = true;
      window.clearInterval(poll);
      window.removeEventListener("pywebviewready", onReady);
      resolve(v);
    };
    const onReady = () => finish(true);
    window.addEventListener("pywebviewready", onReady, { once: true });
    const start = Date.now();
    const poll = window.setInterval(() => {
      if (isBackendReady()) finish(true);
      else if (Date.now() - start > timeoutMs) finish(false); // 진짜 브라우저 → 데모
    }, 100);
  });
  return _readyPromise;
}

export const api: PyApi = new Proxy({} as PyApi, {
  get(_t, prop: string) {
    const real = window.pywebview?.api as PyApi | undefined;
    const target = (real ?? mockApi) as unknown as Record<string, unknown>;
    return target[prop];
  },
});
