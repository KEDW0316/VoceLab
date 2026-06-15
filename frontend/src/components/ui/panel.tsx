import * as React from "react";
import { cn } from "@/lib/utils";

interface PanelProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "title"> {
  title?: React.ReactNode;
  icon?: React.ReactNode;
  right?: React.ReactNode;
  bodyClassName?: string;
}

// 제목 헤더 + 본문을 가진 표준 패널(카드).
export function Panel({ title, icon, right, children, className, bodyClassName, ...props }: PanelProps) {
  return (
    <div
      className={cn("flex flex-col overflow-hidden rounded-lg border border-border bg-card", className)}
      {...props}
    >
      {(title || right) && (
        <div className="flex items-center justify-between border-b border-border px-3 py-2">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground">
            {icon}
            {title}
          </div>
          {right && <div className="num text-[11px] text-muted-foreground">{right}</div>}
        </div>
      )}
      <div className={cn("relative flex-1 overflow-hidden", bodyClassName)}>{children}</div>
    </div>
  );
}
