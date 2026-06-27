import { useCallback, useEffect, useState } from "react";
import type { Device } from "./types";
import { api, whenBackendReady } from "./api";
import { loadPref, savePref } from "./storage";

export interface DevicesState {
  inputs: Device[];
  outputs: Device[];
  inputIdx: number | null;
  outputIdx: number | null;
  inputLabel: string | null;
  outputLabel: string | null;
  setInput: (idx: number) => void;
  setOutput: (idx: number) => void;
  refresh: () => void;
}

// 저장된 라벨과 일치하는 장치를 우선 선택(인덱스는 바뀔 수 있으므로 라벨로 기억).
function pick(devs: Device[], key: string): Device | undefined {
  const saved = loadPref(key);
  return devs.find((d) => d.label === saved) ?? devs[0];
}

// 장치 목록/선택을 한 곳에서 관리 — 설정 패널, 상태바, 녹음/모니터가 공유한다.
export function useDevices(): DevicesState {
  const [inputs, setInputs] = useState<Device[]>([]);
  const [outputs, setOutputs] = useState<Device[]>([]);
  const [inputIdx, setInputIdx] = useState<number | null>(null);
  const [outputIdx, setOutputIdx] = useState<number | null>(null);

  const refresh = useCallback(() => {
    api.list_devices().then(({ inputs, outputs }) => {
      setInputs(inputs);
      setOutputs(outputs);
      const i = pick(inputs, "inputDevice");
      const o = pick(outputs, "outputDevice");
      setInputIdx(i?.index ?? null);
      setOutputIdx(o?.index ?? null);
      api.set_output_device(o?.index ?? null);
    });
  }, []);

  useEffect(() => {
    whenBackendReady().then(refresh);
  }, [refresh]);

  const setInput = (idx: number) => {
    setInputIdx(idx);
    const dev = inputs.find((d) => d.index === idx);
    if (dev) savePref("inputDevice", dev.label);
  };
  const setOutput = (idx: number) => {
    setOutputIdx(idx);
    api.set_output_device(idx);
    const dev = outputs.find((d) => d.index === idx);
    if (dev) savePref("outputDevice", dev.label);
  };

  return {
    inputs,
    outputs,
    inputIdx,
    outputIdx,
    inputLabel: inputs.find((d) => d.index === inputIdx)?.label ?? null,
    outputLabel: outputs.find((d) => d.index === outputIdx)?.label ?? null,
    setInput,
    setOutput,
    refresh,
  };
}
