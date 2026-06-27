import { Activity, Mic } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import type { DevicesState } from "@/lib/useDevices";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";

interface Props {
  devices: DevicesState;
  onDone: () => void;
}

// 설치 후 첫 실행 화면 — 언어 선택 + 한 줄 소개 + 마이크 선택 후 시작.
export function Welcome({ devices, onDone }: Props) {
  const { lang, setLang, t } = useI18n();
  const { inputs, inputIdx, setInput } = devices;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-background" />
      <div className="vl-enter relative z-10 w-full max-w-md rounded-2xl bg-card p-7 text-center shadow-2xl">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/15">
          <Activity className="h-7 w-7 text-primary" />
        </div>
        <h1 className="text-xl font-bold tracking-tight">
          Voce<span className="text-primary">Lab</span>
        </h1>
        <p className="mx-auto mt-2 max-w-xs text-sm text-muted-foreground">{t("welcome.subtitle")}</p>

        {/* 언어 선택 */}
        <div className="mt-6 text-left">
          <label className="vl-label">{t("welcome.lang")}</label>
          <div className="mt-1.5 grid grid-cols-2 gap-2">
            {(["ko", "en"] as const).map((l) => (
              <button
                key={l}
                onClick={() => setLang(l)}
                className={`rounded-lg border px-3 py-2.5 text-sm font-medium transition-colors ${
                  lang === l
                    ? "border-primary bg-primary/10 text-foreground"
                    : "border-border text-muted-foreground hover:bg-secondary/60"
                }`}
              >
                {l === "ko" ? "한국어" : "English"}
              </button>
            ))}
          </div>
        </div>

        {/* 입력 장치 (마이크) */}
        <div className="mt-4 text-left">
          <label className="mb-1.5 flex items-center gap-1.5 vl-label">
            <Mic className="h-3.5 w-3.5" />
            {t("welcome.device")}
          </label>
          {inputs.length > 0 ? (
            <Select value={inputIdx ?? ""} onChange={(e) => setInput(Number(e.target.value))}>
              {inputs.map((d) => (
                <option key={d.index} value={d.index}>
                  {d.label}
                </option>
              ))}
            </Select>
          ) : (
            <p className="text-xs text-muted-foreground/70">{t("welcome.device.none")}</p>
          )}
        </div>

        <Button className="mt-6 w-full" size="lg" onClick={onDone}>
          {t("welcome.start")}
        </Button>
      </div>
    </div>
  );
}
