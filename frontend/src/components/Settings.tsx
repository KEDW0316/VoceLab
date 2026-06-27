import { type ReactNode } from "react";
import { Mic, RefreshCw, Volume2 } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import type { DevicesState } from "@/lib/useDevices";
import { Modal } from "@/components/ui/modal";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";

interface Props {
  open: boolean;
  onClose: () => void;
  devices: DevicesState;
}

function Field({ label, icon, children }: { label: string; icon?: ReactNode; children: ReactNode }) {
  return (
    <div>
      <label className="mb-1.5 flex items-center gap-1.5 vl-label">
        {icon}
        {label}
      </label>
      {children}
    </div>
  );
}

export function Settings({ open, onClose, devices }: Props) {
  const { lang, setLang, t } = useI18n();
  const { inputs, outputs, inputIdx, outputIdx, setInput, setOutput, refresh } = devices;

  return (
    <Modal open={open} onClose={onClose} title={t("settings.title")}>
      <div className="space-y-4">
        {/* 언어 */}
        <Field label={t("settings.language")}>
          <div className="flex overflow-hidden rounded-md border border-border">
            {(["ko", "en"] as const).map((l) => (
              <button
                key={l}
                onClick={() => setLang(l)}
                className={`flex-1 px-3 py-1.5 text-sm transition-colors ${
                  lang === l ? "bg-secondary text-foreground" : "text-muted-foreground hover:bg-secondary/60"
                }`}
              >
                {l === "ko" ? "한국어" : "English"}
              </button>
            ))}
          </div>
        </Field>

        {/* 입력 장치 */}
        <Field label={t("settings.input")} icon={<Mic className="h-3.5 w-3.5" />}>
          <Select value={inputIdx ?? ""} onChange={(e) => setInput(Number(e.target.value))}>
            {inputs.map((d) => (
              <option key={d.index} value={d.index}>
                {d.label}
              </option>
            ))}
          </Select>
        </Field>

        {/* 출력 장치 */}
        <Field label={t("settings.output")} icon={<Volume2 className="h-3.5 w-3.5" />}>
          <Select value={outputIdx ?? ""} onChange={(e) => setOutput(Number(e.target.value))}>
            {outputs.map((d) => (
              <option key={d.index} value={d.index}>
                {d.label}
              </option>
            ))}
          </Select>
        </Field>

        <div className="flex items-center justify-between pt-1">
          <Button variant="outline" size="sm" onClick={refresh}>
            <RefreshCw className="h-3.5 w-3.5" /> {t("device.refresh")}
          </Button>
          <Button size="sm" onClick={onClose}>
            {t("settings.done")}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
