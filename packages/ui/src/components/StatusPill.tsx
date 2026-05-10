import * as React from "react";
import { cn } from "../lib/cn";

export type StatusPillTone = "neutral" | "success" | "warning" | "danger" | "info";

const toneClass: Record<StatusPillTone, string> = {
  neutral: "bg-ink-50 text-ink-700",
  success: "bg-[#E8F1EA] text-[#3B6A4A]",
  warning: "bg-[#F7ECDD] text-[#8C5A1F]",
  danger: "bg-[#F4DEDA] text-[#8E3B30]",
  info: "bg-[#EAEAEC] text-[#3D3F47]",
};

export interface StatusPillProps extends React.HTMLAttributes<HTMLSpanElement> {
  tone?: StatusPillTone;
}

export const StatusPill = React.forwardRef<HTMLSpanElement, StatusPillProps>(
  ({ className, tone = "neutral", ...props }, ref) => (
    <span
      ref={ref}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium",
        toneClass[tone],
        className,
      )}
      {...props}
    />
  ),
);
StatusPill.displayName = "StatusPill";
