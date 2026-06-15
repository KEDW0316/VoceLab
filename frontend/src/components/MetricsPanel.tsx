import { FileText, BarChart3 } from "lucide-react";
import type { Metric } from "@/lib/types";

const CATEGORY_ORDER = ["음질", "음높이", "공명·음색", "비브라토"];

// 카테고리별 액센트 색 (좌측 스트라이프/점)
const CATEGORY_COLOR: Record<string, string> = {
  음질: "hsl(var(--primary))",
  음높이: "hsl(var(--accent))",
  "공명·음색": "hsl(200 80% 55%)",
  비브라토: "hsl(var(--warning))",
};

function groupByCategory(metrics: Metric[]) {
  const map = new Map<string, Metric[]>();
  for (const m of metrics) {
    if (!map.has(m.category)) map.set(m.category, []);
    map.get(m.category)!.push(m);
  }
  return [...map.entries()].sort(
    (a, b) => CATEGORY_ORDER.indexOf(a[0]) - CATEGORY_ORDER.indexOf(b[0])
  );
}

// 카드 폭에 맞게 자릿수를 줄인다(큰 Hz 값은 정수, 작은 값은 소수).
function fmtValue(m: Metric): string {
  if (m.value === null) return "—";
  const a = Math.abs(m.value);
  if (a >= 100) return Math.round(m.value).toString();
  if (a >= 10) return m.value.toFixed(1);
  return m.value.toFixed(2);
}

function MetricCard({ m }: { m: Metric }) {
  const accent = CATEGORY_COLOR[m.category] ?? "hsl(var(--primary))";
  const tip = [m.description, m.normal && `정상/참고: ${m.normal}`, m.reference && `출처: ${m.reference.title}`]
    .filter(Boolean)
    .join("\n\n");
  return (
    <div
      className="group relative overflow-hidden rounded-md border border-border/70 bg-secondary/20 pl-3 pr-3 py-2 transition-colors hover:border-border hover:bg-secondary/40"
      title={tip}
    >
      <span
        className="absolute inset-y-0 left-0 w-[3px]"
        style={{ background: accent, opacity: 0.7 }}
      />
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-medium text-muted-foreground">{m.label}</span>
        {m.reference && (
          <a
            href={m.reference.url}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-0.5 text-[10px] text-muted-foreground/50 transition-colors hover:text-primary"
            title={`출처: ${m.reference.title}`}
          >
            <FileText className="h-3 w-3" />
          </a>
        )}
      </div>
      <div className="flex items-baseline gap-1">
        <span className="num text-[18px] font-semibold leading-tight text-foreground">
          {fmtValue(m)}
        </span>
        <span className="text-[10px] text-muted-foreground">{m.unit}</span>
      </div>
    </div>
  );
}

export function MetricsPanel({ metrics }: { metrics: Metric[] }) {
  const groups = groupByCategory(metrics);
  return (
    <div className="flex h-full flex-col overflow-hidden rounded-lg border border-border bg-card">
      <div className="flex items-center gap-2 border-b border-border px-4 py-3">
        <BarChart3 className="h-4 w-4 text-primary" />
        <div>
          <h2 className="text-sm font-semibold leading-none">음향 지표</h2>
          <p className="mt-1 text-[10px] text-muted-foreground">
            카드에 마우스를 올리면 설명·출처
          </p>
        </div>
      </div>
      <div className="flex-1 space-y-4 overflow-y-auto p-3">
        {metrics.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-2 px-4 text-center">
            <BarChart3 className="h-8 w-8 text-muted-foreground/30" />
            <p className="text-xs text-muted-foreground">
              녹음하면 14개 음향 지표가
              <br />
              여기에 표시됩니다.
            </p>
          </div>
        ) : (
          groups.map(([category, items]) => (
            <div key={category} className="space-y-1.5">
              <div className="flex items-center gap-1.5 px-0.5">
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ background: CATEGORY_COLOR[category] }}
                />
                <h3 className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                  {category}
                </h3>
              </div>
              <div className="grid grid-cols-2 gap-1.5">
                {items.map((m) => (
                  <MetricCard key={m.key} m={m} />
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
