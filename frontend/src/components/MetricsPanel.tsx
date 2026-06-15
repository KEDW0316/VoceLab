import { FileText } from "lucide-react";
import type { Metric } from "@/lib/types";
import { Card } from "@/components/ui/card";

const CATEGORY_ORDER = ["음질", "음높이", "공명·음색", "비브라토"];

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

function MetricCard({ m }: { m: Metric }) {
  const tip = [m.description, m.normal && `정상/참고: ${m.normal}`, m.reference && `출처: ${m.reference.title}`]
    .filter(Boolean)
    .join("\n\n");
  return (
    <div
      className="group flex flex-col gap-0.5 rounded-lg border border-border/60 bg-secondary/30 px-3 py-2 transition-colors hover:border-primary/40"
      title={tip}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs text-sky-300/90">{m.label}</span>
        {m.reference && (
          <a
            href={m.reference.url}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-0.5 text-[10px] text-emerald-500/70 opacity-0 transition-opacity group-hover:opacity-100 hover:text-emerald-400"
          >
            <FileText className="h-3 w-3" /> 출처
          </a>
        )}
      </div>
      <div className="flex items-baseline gap-1">
        <span className="text-xl font-bold tabular-nums text-primary">{m.display}</span>
        <span className="text-[10px] text-muted-foreground">{m.unit}</span>
      </div>
    </div>
  );
}

export function MetricsPanel({ metrics }: { metrics: Metric[] }) {
  const groups = groupByCategory(metrics);
  return (
    <Card className="flex h-full flex-col overflow-hidden">
      <div className="border-b border-border px-4 py-3">
        <h2 className="text-sm font-semibold">음향 지표</h2>
        <p className="text-[11px] text-muted-foreground">
          카드에 마우스를 올리면 설명·출처가 보입니다
        </p>
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto p-3">
        {metrics.length === 0 && (
          <p className="px-1 py-6 text-center text-xs text-muted-foreground">
            녹음 후 분석 결과가 여기에 표시됩니다.
          </p>
        )}
        {groups.map(([category, items]) => (
          <div key={category} className="space-y-1.5">
            <h3 className="px-0.5 text-[11px] font-semibold uppercase tracking-wide text-accent">
              {category}
            </h3>
            {items.map((m) => (
              <MetricCard key={m.key} m={m} />
            ))}
          </div>
        ))}
      </div>
    </Card>
  );
}
