import { useEffect, useState } from "react";
import { Mic, RefreshCw, Speaker } from "lucide-react";
import type { Device } from "@/lib/types";
import { api } from "@/lib/api";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";

interface Props {
  onInputChange: (i: number | null) => void;
  onOutputChange: (i: number | null) => void;
}

export function DeviceBar({ onInputChange, onOutputChange }: Props) {
  const [inputs, setInputs] = useState<Device[]>([]);
  const [outputs, setOutputs] = useState<Device[]>([]);

  const refresh = () => {
    api.list_devices().then(({ inputs, outputs }) => {
      setInputs(inputs);
      setOutputs(outputs);
      onInputChange(inputs[0]?.index ?? null);
      onOutputChange(outputs[0]?.index ?? null);
    });
  };

  useEffect(refresh, []);

  return (
    <div className="flex items-center gap-2">
      <div className="flex flex-1 items-center gap-2">
        <Mic className="h-4 w-4 shrink-0 text-muted-foreground" />
        <Select onChange={(e) => onInputChange(Number(e.target.value))}>
          {inputs.map((d) => (
            <option key={d.index} value={d.index}>
              {d.label}
            </option>
          ))}
        </Select>
      </div>
      <div className="flex flex-1 items-center gap-2">
        <Speaker className="h-4 w-4 shrink-0 text-muted-foreground" />
        <Select onChange={(e) => onOutputChange(Number(e.target.value))}>
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
