import * as React from "react";
import { cn } from "../lib/cn";

export const Hairline = React.forwardRef<HTMLHRElement, React.HTMLAttributes<HTMLHRElement>>(
  ({ className, ...props }, ref) => (
    <hr ref={ref} className={cn("border-t hairline", className)} {...props} />
  ),
);
Hairline.displayName = "Hairline";
