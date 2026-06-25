import type { Metric } from "@/lib/types";
import { useI18n } from "@/lib/i18n";
import { METRIC_EN } from "@/lib/content";

// 핵심 지표만 (CPPS·HNR·지터·쉬머). 모든 카드가 동일한 형태.
const CORE = ["cpps", "hnr", "jitter", "shimmer"];

const STATUS_COLOR: Record<Metric["status"], string> = {
  good: "hsl(var(--success))",
  watch: "hsl(var(--warning))",
  poor: "hsl(var(--danger))",
  info: "hsl(var(--foreground))",
};
const STATUS_KEY: Record<Metric["status"], string> = {
  good: "status.good",
  watch: "status.watch",
  poor: "status.poor",
  info: "status.info",
};

function fmt(v: number | null): string {
  if (v === null) return "—";
  const a = Math.abs(v);
  return a >= 100 ? Math.round(v).toString() : a >= 10 ? v.toFixed(1) : v.toFixed(2);
}

function Card({ m, base }: { m: Metric; base?: number | null }) {
  const { lang, t } = useI18n();
  const color = STATUS_COLOR[m.status];
  const en = lang === "en" ? METRIC_EN[m.key] : undefined;
  const label = en?.label ?? m.label;
  const description = en?.desc ?? m.description;
  const normal = en?.normal ?? m.normal;
  const tip = [description, normal && `${t("metrics.normal")}: ${normal}`].filter(Boolean).join("\n\n");

  let delta: string | null = null;
  let deltaColor = "hsl(var(--muted-foreground))";
  if (base != null && m.value != null) {
    const d = m.value - base;
    if (Math.abs(d) >= 0.01) {
      const improved = m.better === "high" ? d > 0 : m.better === "low" ? d < 0 : null;
      deltaColor = improved == null ? deltaColor : improved ? "hsl(var(--success))" : "hsl(var(--danger))";
      delta = `${d > 0 ? "▲" : "▼"}${Math.abs(d) >= 10 ? Math.abs(d).toFixed(0) : Math.abs(d).toFixed(1)}`;
    }
  }

  return (
    <div className="vl-card flex flex-1 flex-col gap-1 px-3 py-2.5" title={tip}>
      <div className="flex items-center gap-1.5">
        <span className="h-1.5 w-1.5 rounded-full" style={{ background: color }} title={t(STATUS_KEY[m.status])} />
        <span className="vl-label">{label}</span>
        {delta && <span className="num ml-auto text-[11px]" style={{ color: deltaColor }}>{delta}</span>}
      </div>
      <div className="flex items-baseline whitespace-nowrap">
        <span className="num text-[22px] font-semibold leading-none" style={{ color }}>{fmt(m.value)}</span>
        <span className="ms-0.5 text-[11px] text-muted-foreground">{m.unit}</span>
      </div>
    </div>
  );
}

export function MetricsPanel({
  metrics,
  baseline,
}: {
  metrics: Metric[];
  baseline?: Record<string, number | null> | null;
}) {
  const { t } = useI18n();
  const core = CORE.map((k) => metrics.find((m) => m.key === k)).filter(Boolean) as Metric[];
  if (core.length === 0) {
    return (
      <div className="vl-card px-3 py-2.5 text-center vl-label">
        {t("metrics.empty")}
      </div>
    );
  }
  return <div className="flex gap-2">{core.map((m) => <Card key={m.key} m={m} base={baseline ? baseline[m.key] : undefined} />)}</div>;
}
