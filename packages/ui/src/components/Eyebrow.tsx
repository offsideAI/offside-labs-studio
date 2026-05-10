import * as React from "react";
import { cn } from "../lib/cn";

export const Eyebrow = React.forwardRef<HTMLSpanElement, React.HTMLAttributes<HTMLSpanElement>>(
  ({ className, ...props }, ref) => (
    <span
      ref={ref}
      className={cn(
        "font-styrene text-xs font-bold uppercase tracking-eyebrow text-tan-text",
        className,
      )}
      {...props}
    />
  ),
);
Eyebrow.displayName = "Eyebrow";
