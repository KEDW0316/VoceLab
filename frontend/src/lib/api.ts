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
  async start_recording() {},
  async stop_recording() {
    return mock.mockAnalysis;
  },
  async get_level() {
    return 0.4 + Math.random() * 0.3;
  },
  async play() {},
  async stop_playback() {},
  async list_scales() {
    return mock.mockScales;
  },
  async solfege_for(scaleKey) {
    return mock.mockScales.find((s) => s.key === scaleKey)?.solfege ?? "";
  },
  async play_guide_tone() {},
};

export const isBackendReady = () =>
  typeof window !== "undefined" && !!window.pywebview?.api;

export const api: PyApi = new Proxy({} as PyApi, {
  get(_t, prop: string) {
    const real = window.pywebview?.api as PyApi | undefined;
    const target = (real ?? mockApi) as unknown as Record<string, unknown>;
    return target[prop];
  },
});
