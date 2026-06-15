import { useEffect, useState } from "react";
import { Mic, RefreshCw, Speaker } from "lucide-react";
import type { Device } from "@/lib/types";
import { api, whenBackendReady } from "@/lib/api";
import { loadPref, savePref } from "@/lib/storage";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";

interface Props {
  onInputChange: (i: number | null) => void;
  onOutputChange: (i: number | null) => void;
}

export function DeviceBar({ onInputChange, onOutputChange }: Props) {
  const [inputs, setInputs] = useState<Device[]>([]);
  const [outputs, setOutputs] = useState<Device[]>([]);
  const [inputIdx, setInputIdx] = useState<number | null>(null);
  const [outputIdx, setOutputIdx] = useState<number | null>(null);

  // 저장된 라벨과 일치하는 장치를 우선 선택(인덱스는 바뀔 수 있으므로 라벨로 기억).
  const pick = (devs: Device[], key: string): Device | undefined => {
    const saved = loadPref(key);
    return devs.find((d) => d.label === saved) ?? devs[0];
  };

  const refresh = () => {
    api.list_devices().then(({ inputs, outputs }) => {
      setInputs(inputs);
      setOutputs(outputs);
      const i = pick(inputs, "inputDevice");
      const o = pick(outputs, "outputDevice");
      setInputIdx(i?.index ?? null);
      setOutputIdx(o?.index ?? null);
      onInputChange(i?.index ?? null);
      onOutputChange(o?.index ?? null);
    });
  };

  useEffect(() => {
    whenBackendReady().then(refresh);
  }, []);

  const onInput = (idx: number) => {
    setInputIdx(idx);
    const dev = inputs.find((d) => d.index === idx);
    if (dev) savePref("inputDevice", dev.label);
    onInputChange(idx);
  };
  const onOutput = (idx: number) => {
    setOutputIdx(idx);
    const dev = outputs.find((d) => d.index === idx);
    if (dev) savePref("outputDevice", dev.label);
    onOutputChange(idx);
  };

  return (
    <div className="flex items-center gap-2">
      <div className="flex flex-1 items-center gap-2">
        <Mic className="h-4 w-4 shrink-0 text-muted-foreground" />
        <Select value={inputIdx ?? ""} onChange={(e) => onInput(Number(e.target.value))}>
          {inputs.map((d) => (
            <option key={d.index} value={d.index}>
              {d.label}
            </option>
          ))}
        </Select>
      </div>
      <div className="flex flex-1 items-center gap-2">
        <Speaker className="h-4 w-4 shrink-0 text-muted-foreground" />
        <Select value={outputIdx ?? ""} onChange={(e) => onOutput(Number(e.target.value))}>
          {outputs.map((d) => (
            <option key={d.index} value={d.index}>
              {d.label}
            </option>
          ))}
        </Select>
      </div>
      <Button variant="outline" size="icon" onClick={refresh} title="장치 새로고침">
        <RefreshCw className="h-4 w-4" />
      </Button>
    </div>
  );
}
