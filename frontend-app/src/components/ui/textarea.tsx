import * as React from "react";
import { cn } from "@/lib/utils";

function Textarea({
  className,
  style,
  ...props
}: React.ComponentProps<"textarea">) {
  return (
    <textarea
      {...props}
      className={cn(
        "w-full min-h-[130px] rounded-md px-4 py-3 text-base md:text-sm",
        "bg-surface-input border border-theme",
        "transition-all duration-200",
        "focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:border-primary outline-none",
        "disabled:cursor-not-allowed disabled:opacity-50",
        // Force text colors using Tailwind with important modifier
        "!text-gray-900 dark:!text-gray-100",
        "placeholder:!text-gray-500 dark:placeholder:!text-gray-400",
        className
      )}
      style={{
        // Double ensure with inline styles as fallback
        color: document.documentElement.classList.contains('dark') ? '#f1f5f9' : '#111827',
        ...style
      }}
    />
  );
}

export { Textarea };