import * as React from "react";
import { cn } from "@/lib/utils";

interface PanelProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "title"> {
  title?: React.ReactNode;
  icon?: React.ReactNode;
  right?: React.ReactNode;
  bodyClassName?: string;
}

// 제목 헤더 + 본문을 가진 표준 패널. 모든 패널이 동일한 카드/헤더 언어를 쓴다.
export function Panel({ title, icon, right, children, className, bodyClassName, ...props }: PanelProps) {
  return (
    <div className={cn("vl-card flex flex-col overflow-hidden", className)} {...props}>
      {(title || right) && (
        <div className="flex items-center justify-between border-b border-white/[0.06] px-3 py-2">
          <div className="vl-head">
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
